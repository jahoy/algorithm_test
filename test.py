DECLARE start_date DATE DEFAULT DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 15 DAY);
DECLARE end_date DATE DEFAULT DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 1 DAY);

--- unfollow metric
WITH DRIVER AS(
SELECT
*
FROM(
  SELECT
  date_kr,
  driver_activity.driver_id,
  seq_id,
  driver_activity.activity_status,
  DATETIME(start_at, 'Asia/Seoul') as start_at_kr,
  DATETIME(end_at, 'Asia/Seoul') as end_at_kr,
  LEAD(driver_activity.activity_status) OVER(PARTITION BY DATE(start_at, 'Asia/Seoul'), driver_activity.driver_id ORDER BY start_at) as next_activity_status
  FROM tada.driver_activity
  JOIN tada.driver on driver_activity.driver_id = driver.id
  JOIN tada.vehicle on driver_activity.vehicle_id = vehicle.id
  WHERE 1=1
   AND vehicle.taxi_region_type = 'SEOUL' -- 서울 차량
   AND type = "PREMIUM" -- 프리미엄 차량
  AND DATE(start_at, 'Asia/Seoul') between start_date and end_date
)
WHERE 1=1
AND activity_status = 'DISPATCHING'
AND next_activity_status = 'RIDING'
)

, DATA AS(
SELECT
date_kr,
d.driver_id,
seq_id,
activity_status,
start_at_kr,
end_at_kr,
TIMESTAMP_DIFF(eta_time, gps_updated_at, MINUTE) as remain_eta,
route_distance_meters,
st_distance(st_geogpoint(vehicle_location_lng, vehicle_location_lat), st_geogpoint(destination_assigned_area_lng, destination_assigned_area_lat)) as straight_meters,
DATETIME(gps_updated_at, 'Asia/Seoul') as gps_updated_at_kr
FROM tada_prod_us.driver_eta_log as eta
JOIN DRIVER as d ON eta.driver_activity_status = d.activity_status AND eta.driver_id = d.driver_id AND DATETIME(eta.gps_updated_at, 'Asia/Seoul') >= d.start_at_kr AND DATETIME(eta.gps_updated_at, 'Asia/Seoul') <=d.end_at_kr
WHERE 1=1
AND DATE(gps_updated_at, 'Asia/Seoul') between start_date and end_date
ORDER BY date_kr, driver_id, gps_updated_at
)

, FINAL_DATA AS(
SELECT
*,
FIRST_VALUE(remain_eta) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr) as first_remain_eta,
LAST_VALUE(remain_eta) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_remain_eta,
DATETIME_DIFF(end_at_kr, start_at_kr, MINUTE) as total_dispatching_minute,
FIRST_VALUE(route_distance_meters) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr) as first_route_distance_meters,
LAST_VALUE(route_distance_meters) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_route_distance_meters,
LAST_VALUE(seq_id) OVER(PARTITION BY date_kr, driver_id ORDER BY seq_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_seq_id
FROM DATA
)


, FOLLOW_INFO AS(
SELECT
DISTINCT 
date_kr,
driver_id,
start_at_kr,
end_at_kr,
seq_id,
first_remain_eta,
last_remain_eta,
total_dispatching_minute,
first_route_distance_meters,
last_route_distance_meters,
CASE WHEN (last_route_distance_meters <= 3000) OR ((((first_remain_eta * 2/3) > last_remain_eta) OR ((first_route_distance_meters * 2/3) > last_route_distance_meters)) AND(total_dispatching_minute - 2 *(first_remain_eta - last_remain_eta) <0 ) AND(last_route_distance_meters > 3000)) OR straight_meters <= 1500 THEN TRUE -- 대기지역에서 대기 OR 1/3 이상 대기지역으로 움직이다가 납치
    ELSE FALSE END as is_follow
FROM FINAL_DATA 
WHERE 1=1
AND seq_id != last_seq_id -- 마지막 퇴근 직전 dispatching은 제외시키고 계산
AND date_kr between start_date AND end_date -- 기간 조정
)


, DRIVER_SEQ AS(
SELECT
*
FROM(
SELECT
date_kr,
driver_id,
COUNT(seq_id) as c_dispatch,
COUNTIF(is_follow=True) as c_follow,
COUNTIF(is_follow=False) as c_not_follow,
COUNTIF(is_follow=True) / COUNT(seq_id) as follow_ratio_for_driver
FROM FOLLOW_INFO
GROUP BY date_kr, driver_id
ORDER BY date_kr, driver_id
)
WHERE 1=1
AND c_dispatch >= 4 -- 최소 4번 이상 dispathcing 했던 드라이버만 추리기
)


, FOLLOW_RATIO_METRIC AS(
SELECT
date_kr,
SUM(c_follow) / SUM(c_dispatch) as follow_ratio
FROM DRIVER_SEQ
GROUP BY 1
)

-- 주요 수요, 공급 metric
-- 실제 수요 데이터
, SERVICE_CATEGORY AS(
SELECT
date_kr,
ride_id,
CASE WHEN call_view_type like '%LITE%' THEN 'LITE'
     WHEN call_view_type like '%PREMIUM%' THEN 'PREMIUM'
     WHEN call_view_type like '%NEAR_TAXI%' THEN 'NEAR_TAXI'
     WHEN call_view_type like '%DAERI%' THEN 'DAERI'
     END AS service_type,
determined_type
FROM tada_ext.ride_category
WHERE 1=1 
AND date_kr between start_date and end_date
)


, VAILD_SERVICE_CALL AS (
SELECT
*
FROM(
SELECT
  r.date_kr,
  r.created_at,
  LEAD(created_at) OVER (PARTITION BY rider_id ORDER BY created_at ASC) lead_created_at,
  TIMESTAMP_DIFF (LEAD( created_at ) OVER (PARTITION BY rider_id ORDER BY created_at),created_at, MINUTE) AS minute_diff,
  r.id,
  s.service_type,
  r.rider_id,
  r.origin_lng,
  r.origin_lat,
  r.status,
  IFNULL(determined_type, r.type) as determined_type,
  tada_udf.geo_to_h3(origin_lng, origin_lat, 7)  as h3_l7,
  origin_address,
  receipt_total / 1.1 as receipt_total,
  IFNULL(receipt_total * ((100/surge_percentage) / 1.1), (receipt_total / 1.1)) as non_surge_receipt_total
FROM tada.ride as r
JOIN SERVICE_CATEGORY as s ON r.id = s.ride_id and r.date_kr = s.date_kr
)
WHERE 1=1
AND lead_created_at IS NULL OR minute_diff >= 5 OR status = 'DROPPED_OFF' # 유효 호출 조건
)


, NEW_DEMAND AS (
SELECT
date_kr,
-- 가까운 타다
COUNTIF(service_type = 'NEAR_TAXI') as c_near_taxi_total_demand,
COUNTIF(service_type = 'NEAR_TAXI' and determined_type = 'LITE') as c_near_taxi_lite_demand,
COUNTIF(service_type = 'NEAR_TAXI' and determined_type = 'PREMIUM') as c_near_taxi_premium_demand,
COUNTIF(service_type = 'NEAR_TAXI' and determined_type = 'UNKNOWN') as c_near_taxi_unknown_demand,

COUNTIF(service_type = 'NEAR_TAXI' and status = 'DROPPED_OFF') as c_near_taxi_total_dropoff,
COUNTIF(service_type = 'NEAR_TAXI' and determined_type = 'LITE' and status = 'DROPPED_OFF') as c_near_taxi_lite_dropoff,
COUNTIF(service_type = 'NEAR_TAXI' and determined_type = 'PREMIUM' and status = 'DROPPED_OFF') as c_near_taxi_premium_dropoff,

COUNTIF(service_type = 'NEAR_TAXI') - COUNTIF(service_type = 'NEAR_TAXI' and status = 'DROPPED_OFF') as c_near_taxi_fail,

-- 라이트
COUNTIF(service_type = 'LITE') as c_lite_demand,
COUNTIF(service_type = 'LITE' and status = 'DROPPED_OFF') as c_lite_dropoff,
COUNTIF(service_type = 'LITE') - COUNTIF(service_type = 'LITE' and status = 'DROPPED_OFF') as c_lite_fail,

-- 플러스
COUNTIF(service_type = 'PREMIUM') as c_premium_demand,
COUNTIF(service_type = 'PREMIUM' and status = 'DROPPED_OFF') as c_premium_dropoff,
COUNTIF(service_type = 'PREMIUM') - COUNTIF(service_type = 'PREMIUM' and status = 'DROPPED_OFF') as c_premium_fail,

-- 매출
SUM(IF(determined_type = 'LITE'  and status = 'DROPPED_OFF', IFNULL(receipt_total,0),0)) as sum_lite_receipt_total,
SUM(IF(determined_type = 'PREMIUM'  and status = 'DROPPED_OFF', IFNULL(receipt_total,0),0)) as sum_premium_receipt_total,

SUM(IF(determined_type = 'LITE'  and status = 'DROPPED_OFF', IFNULL(non_surge_receipt_total,0),0)) as sum_lite_non_surge_receipt_total,
SUM(IF(determined_type = 'PREMIUM'  and status = 'DROPPED_OFF', IFNULL(non_surge_receipt_total,0),0)) as sum_premium_non_surge_receipt_total,

FROM VAILD_SERVICE_CALL
WHERE SPLIT(origin_address," ")[SAFE_OFFSET(0)] like '%서울%'
GROUP BY 1
)


, NEW_SUPPLY AS (
SELECT 
  date_kr,
  ROUND(countif(activity_status in ('DISPATCHING', 'RIDING'))/6,1) as snapshot_supply
FROM (
  SELECT 
    date_kr,
    vehicle_id, 
    driver_id, 
    vehicle_location_lng, 
    vehicle_location_lat, 
    vehicle_location_address,
    DATETIME(gps_updated_at, 'Asia/Seoul') as gps_updated_at_kr, 
    activity_status, 
  FROM `kr-co-vcnc-tada.tada_prod_us.supply_snapshot` 
    JOIN `kr-co-vcnc-tada.tada_meta.south_korea_shp` gis ON st_contains(ST_GEOGFROMTEXT(gis.geometry), st_geogpoint(vehicle_location_lng, vehicle_location_lat))
  AND driver_type = 'PREMIUM'
  AND sido_nm like '%서울%'
)
WHERE date_kr between start_date and end_date
GROUP BY 1
)

, CAR_RIDING_RATIO AS (
SELECT
date_kr,
SUM(riding_minutes) as riding_minutes,
SUM(dispatching_minutes) as dispatching_minutes,
COUNTIF((riding_minutes + dispatching_minutes) >= 60 * 5) as c_working_driver

FROM(
SELECT
  DATE(ts, "Asia/Seoul") date_kr,
  driver_id,
  COUNT(IF(activity_status = 'RIDING', ts, null)) as riding_minutes,
  COUNT(IF(activity_status = 'DISPATCHING', ts, null)) as dispatching_minutes,
FROM (
  SELECT
    driver_id,
    ts,
    activity_status
  FROM (
      SELECT
        dact.driver_id,
        dact.activity_status,
        dact.start_at,
        dact.end_at,
        GENERATE_TIMESTAMP_ARRAY(dact.start_at, dact.end_at, INTERVAL 1 MINUTE) AS timestamp_array,
      FROM
        `kr-co-vcnc-tada.tada.driver_activity` dact
      join tada.driver on dact.driver_id = driver.id
      join tada.vehicle on dact.vehicle_id = vehicle.id
      WHERE 1=1
      AND dact.activity_status in ('DISPATCHING', 'RIDING')
      AND driver.type = 'PREMIUM'
      AND vehicle.taxi_region_type = 'SEOUL'
      AND DATE(dact.start_at, 'Asia/Seoul') between start_date and end_date

  ), UNNEST(timestamp_array) ts
)
GROUP BY
  date_kr,driver_id
  )
  GROUP BY date_kr
)


, FUEL_COST AS (

SELECT
    date_kr,
    SUM(dispatching_distance_meters) as sum_dispatching_distance_meters,
    SUM(riding_distance_meters) as sum_riding_distance_meters,
    SUM(daily_fuel_cost) as sum_daily_fuel_cost
    FROM(
    SELECT
    date_kr,
    d.driver_id,
    ROUND(SUM(IF(d.activity_status in ('DISPATCHING'), sum_distance_delta_meters, 0)),1) as dispatching_distance_meters, 
    ROUND(SUM(IF(d.activity_status in ('RIDING'), sum_distance_delta_meters, 0)),1) as riding_distance_meters, 
    ROUND(SUM(sum_distance_delta_meters) * 0.187,0) as daily_fuel_cost
FROM tada_ext.driver_activity_distance as d
join tada.driver on d.driver_id = driver.id
join tada.vehicle on d.vehicle_id = vehicle.id
WHERE 1=1
    AND vehicle.taxi_region_type = 'SEOUL'
    AND type = "PREMIUM"
    AND d.activity_status in ('DISPATCHING', 'RIDING')
    AND date_kr between start_date and end_date
GROUP BY 1,2
)
GROUP BY 1
)



, DAILY_DISPATCH_METRIC AS(
SELECT
monday_date_kr,

-- follow_ratio
ROUND(avg(follow_ratio), 2) as avg_follow_ratio,

-- 가까운 타다
ROUND(avg(c_near_taxi_total_demand), 2) as avg_c_near_taxi_total_demand,
ROUND(avg(c_near_taxi_lite_demand), 2) as avg_c_near_taxi_lite_demand,
ROUND(avg(c_near_taxi_premium_demand), 2) as avg_c_near_taxi_premium_demand,
ROUND(avg(c_near_taxi_unknown_demand), 2) as avg_c_near_taxi_unknown_demand,

ROUND(avg(c_near_taxi_total_dropoff), 2) as avg_c_near_taxi_total_dropoff,
ROUND(avg(c_near_taxi_lite_dropoff), 2) as avg_c_near_taxi_lite_dropoff,
ROUND(avg(c_near_taxi_premium_dropoff), 2) as avg_c_near_taxi_premium_dropoff,

ROUND(avg(c_near_taxi_fail), 2) as avg_c_near_taxi_fail,

-- 라이트
ROUND(avg(c_lite_demand), 2) as avg_c_lite_demand,
ROUND(avg(c_lite_dropoff), 2) as avg_c_lite_dropoff,
ROUND(avg(c_lite_fail), 2) as avg_c_lite_fail,

-- 플러스
ROUND(avg(c_premium_demand), 2) as avg_c_premium_demand,
ROUND(avg(c_premium_dropoff), 2) as avg_c_premium_dropoff,
ROUND(avg(c_premium_fail), 2) as avg_c_premium_fail,

-- 매출
ROUND(avg(sum_lite_receipt_total), 2) as avg_sum_lite_receipt_total,
ROUND(avg(sum_premium_receipt_total), 2) as avg_sum_premium_receipt_total,

ROUND(avg(sum_lite_non_surge_receipt_total), 2) as avg_sum_lite_non_surge_receipt_total,
ROUND(avg(sum_premium_non_surge_receipt_total), 2) as avg_sum_premium_non_surge_receipt_total,

ROUND(avg(snapshot_supply), 2) as avg_snapshot_supply,
ROUND(avg(riding_minutes), 2) as avg_riding_minutes,
ROUND(avg(dispatching_minutes), 2) as avg_dispatching_minutes,
ROUND(avg(c_working_driver), 2) as avg_c_working_driver,
ROUND(avg(sum_dispatching_distance_meters), 2) as avg_sum_dispatching_distance_meters,
ROUND(avg(sum_riding_distance_meters), 2) as avg_sum_riding_distance_meters,
ROUND(avg(sum_daily_fuel_cost), 2) as avg_sum_daily_fuel_cost

-- 합으로 계산
-- follow_ratio
ROUND(sum(follow_ratio), 2) as sum_follow_ratio,

-- 가까운 타다
ROUND(sum(c_near_taxi_total_demand), 2) as sum_c_near_taxi_total_demand,
ROUND(sum(c_near_taxi_lite_demand), 2) as sum_c_near_taxi_lite_demand,
ROUND(sum(c_near_taxi_premium_demand), 2) as sum_c_near_taxi_premium_demand,
ROUND(sum(c_near_taxi_unknown_demand), 2) as sum_c_near_taxi_unknown_demand,

ROUND(sum(c_near_taxi_total_dropoff), 2) as sum_c_near_taxi_total_dropoff,
ROUND(sum(c_near_taxi_lite_dropoff), 2) as sum_c_near_taxi_lite_dropoff,
ROUND(sum(c_near_taxi_premium_dropoff), 2) as sum_c_near_taxi_premium_dropoff,

ROUND(sum(c_near_taxi_fail), 2) as sum_c_near_taxi_fail,

-- 라이트
ROUND(sum(c_lite_demand), 2) as sum_c_lite_demand,
ROUND(sum(c_lite_dropoff), 2) as sum_c_lite_dropoff,
ROUND(sum(c_lite_fail), 2) as sum_c_lite_fail,

-- 플러스
ROUND(sum(c_premium_demand), 2) as sum_c_premium_demand,
ROUND(sum(c_premium_dropoff), 2) as sum_c_premium_dropoff,
ROUND(sum(c_premium_fail), 2) as sum_c_premium_fail,

-- 매출
ROUND(sum(sum_lite_receipt_total), 2) as sum_sum_lite_receipt_total,
ROUND(sum(sum_premium_receipt_total), 2) as sum_sum_premium_receipt_total,

ROUND(sum(sum_lite_non_surge_receipt_total), 2) as sum_sum_lite_non_surge_receipt_total,
ROUND(sum(sum_premium_non_surge_receipt_total), 2) as sum_sum_premium_non_surge_receipt_total,

ROUND(sum(snapshot_supply), 2) as sum_snapshot_supply,
ROUND(sum(riding_minutes), 2) as sum_riding_minutes,
ROUND(sum(dispatching_minutes), 2) as sum_dispatching_minutes,
ROUND(sum(c_working_driver), 2) as sum_c_working_driver,
ROUND(sum(sum_dispatching_distance_meters), 2) as sum_sum_dispatching_distance_meters,
ROUND(sum(sum_riding_distance_meters), 2) as sum_sum_riding_distance_meters,
ROUND(sum(sum_daily_fuel_cost), 2) as sum_sum_daily_fuel_cost

FROM(
SELECT
    d.date_kr,
    DATE_SUB(d.date_kr, INTERVAL tada_udf.extract_weekday(d.date_kr) DAY) as monday_date_kr,
    
    -- follow_ratio
    ROUND(follow_ratio,2) as follow_ratio,
    
    -- 가까운 타다
    c_near_taxi_total_demand,
    c_near_taxi_lite_demand,
    c_near_taxi_premium_demand,
    c_near_taxi_unknown_demand,

    c_near_taxi_total_dropoff,
    c_near_taxi_lite_dropoff,
    c_near_taxi_premium_dropoff,

    c_near_taxi_fail,

    -- 라이트
    c_lite_demand,
    c_lite_dropoff,
    c_lite_fail,

    -- 플러스
    c_premium_demand,
    c_premium_dropoff,
    c_premium_fail,

    -- 매출
    sum_lite_receipt_total,
    sum_premium_receipt_total,

    sum_lite_non_surge_receipt_total,
    sum_premium_non_surge_receipt_total,
    
    snapshot_supply,
    riding_minutes,
    dispatching_minutes,
    c_working_driver,
    sum_dispatching_distance_meters,
    sum_riding_distance_meters,
    sum_daily_fuel_cost
    
    
FROM NEW_DEMAND as d
JOIN NEW_SUPPLY as s ON d.date_kr = s.date_kr
JOIN CAR_RIDING_RATIO as c ON d.date_kr = c.date_kr
JOIN FUEL_COST as f ON d.date_kr = f.date_kr
JOIN FOLLOW_RATIO_METRIC as r ON d.date_kr = r.date_kr

)
GROUP BY 1
)

SELECT
monday_date_kr,

-- 재배치 로직 follow_ratio
avg_follow_ratio,

-- 가까운 타다
avg_c_near_taxi_total_demand,
avg_c_near_taxi_lite_demand,
avg_c_near_taxi_premium_demand,
avg_c_near_taxi_unknown_demand,

avg_c_near_taxi_total_dropoff,
avg_c_near_taxi_lite_dropoff,
avg_c_near_taxi_premium_dropoff,

avg_c_near_taxi_fail,

-- 라이트
avg_c_lite_demand,
avg_c_lite_dropoff,
avg_c_lite_fail,

-- 플러스
avg_c_premium_demand,
avg_c_premium_dropoff,
avg_c_premium_fail,

-- 매출
avg_sum_lite_receipt_total,
avg_sum_premium_receipt_total,
avg_sum_lite_non_surge_receipt_total,
avg_sum_premium_non_surge_receipt_total,
avg_sum_daily_fuel_cost,

-- 유효 공급
avg_snapshot_supply,

-- 워킹 시간
avg_riding_minutes,
avg_dispatching_minutes,
avg_c_working_driver,

-- 공급 대비 수요 2가지 관점
ROUND(IFNULL(SAFE_DIVIDE(sum_c_premium_demand , sum_snapshot_supply), 0), 2) as demand_per_supply_1,
ROUND(IFNULL(SAFE_DIVIDE(sum_c_premium_demand + sum_c_near_taxi_premium_demand + sum_c_near_taxi_unknown_demand * 0.5 , sum_snapshot_supply), 0), 2) as demand_per_supply_2,


-- 하차완료율
ROUND(IFNULL(SAFE_DIVIDE(sum_c_near_taxi_total_dropoff , sum_c_near_taxi_total_demand), 1),2) as near_taxi_dropoff_ratio,
ROUND(IFNULL(SAFE_DIVIDE(sum_c_lite_dropoff , sum_c_lite_demand), 1),2) as lite_dropoff_ratio,
ROUND(IFNULL(SAFE_DIVIDE(sum_c_premium_dropoff , sum_c_premium_demand), 1),2) as premium_dropoff_ratio,

-- 가동 비율, 가동율
ROUND(sum_sum_riding_distance_meters / (sum_sum_riding_distance_meters + sum_sum_dispatching_distance_meters), 2) as ride_distance_meters_per_total_move_meters,
ROUND(sum_riding_minutes / (sum_riding_minutes + sum_dispatching_minutes), 2) as riding_ratio,

-- 워킹 시간당 지표
ROUND((sum_c_near_taxi_premium_dropoff + sum_c_premium_dropoff) / ((sum_riding_minutes + sum_dispatching_minutes) / 60), 2) as c_dropoff_per_working_hour,
ROUND(sum_sum_premium_receipt_total / ((sum_riding_minutes + sum_dispatching_minutes) / 60), 2) as sum_receipt_total_per_working_hour,
ROUND(sum_sum_premium_non_surge_receipt_total / ((sum_riding_minutes + sum_dispatching_minutes) / 60), 2) as sum_non_surge_receipt_total_per_working_hour,
ROUND((sum_sum_premium_receipt_total - sum_sum_daily_fuel_cost) / ((sum_riding_minutes + sum_dispatching_minutes) / 60), 2) as sum_receipt_total_minus_sum_daily_fuel_cost_per_working_hour, -- (서징 포함 매출 - 유류비) / 일한 시간
ROUND((sum_sum_premium_non_surge_receipt_total - sum_sum_daily_fuel_cost) / ((sum_riding_minutes + sum_dispatching_minutes) / 60), 2) as sum_non_receipt_total_minus_sum_daily_fuel_cost_per_working_hour, -- (서징 미포함 매출 - 유류비) / 일한 시간

-- 운행기사당 하차완료수
ROUND((sum_c_near_taxi_premium_dropoff + sum_c_premium_dropoff) / sum_c_working_driver, 2) as c_dropoff_per_c_working_driver,

'PREMIUM' as type,
'SEOUL' as region

FROM DAILY_DISPATCH_METRIC
ORDER BY monday_date_kr