-- unfollow metric

WITH DRIVER AS(
SELECT
    date_kr,
    driver_id,
    seq_id,
    activity_status,
    DATETIME(start_at, 'Asia/Seoul') as start_at_kr,
    DATETIME(end_at, 'Asia/Seoul') as end_at_kr
FROM tada.driver_activity
WHERE 1=1
AND date_kr between DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 4 DAY) and CURRENT_DATE('Asia/Seoul')
AND activity_status = 'DISPATCHING'
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
    vehicle_location_lng,
    vehicle_location_lat,
    destination_assigned_area_name,
    destination_assigned_area_lng,
    destination_assigned_area_lat,
    st_distance(st_geogpoint(vehicle_location_lng, vehicle_location_lat), st_geogpoint(destination_assigned_area_lng, destination_assigned_area_lat)) as straight_meters,
    DATETIME(gps_updated_at, 'Asia/Seoul') as gps_updated_at_kr
FROM tada_prod_us.driver_eta_log as eta
JOIN DRIVER as d ON eta.driver_activity_status = d.activity_status AND eta.driver_id = d.driver_id AND DATETIME(eta.gps_updated_at, 'Asia/Seoul') >= d.start_at_kr AND DATETIME(eta.gps_updated_at, 'Asia/Seoul') <=d.end_at_kr
ORDER BY date_kr, driver_id, gps_updated_at
)

, FINAL_DATA AS(
SELECT
    *,
    FIRST_VALUE(remain_eta) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING ) as first_remain_eta,
    LAST_VALUE(remain_eta) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_remain_eta,
    DATETIME_DIFF(end_at_kr, start_at_kr, MINUTE) as total_dispatching_minute,
    FIRST_VALUE(route_distance_meters) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as first_route_distance_meters,
    LAST_VALUE(route_distance_meters) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_route_distance_meters,
    LAST_VALUE(straight_meters) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_straight_meters,
    LAST_VALUE(seq_id) OVER(PARTITION BY date_kr, driver_id ORDER BY seq_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_seq_id
FROM DATA
)


, FOLLOW_INFO AS(
SELECT
    DISTINCT 
    *,
    CASE WHEN (last_straight_meters <= 1500) OR (last_route_distance_meters <= 3000) OR ((((first_remain_eta * 2/3) > last_remain_eta) AND ((first_route_distance_meters * 2/3) > last_route_distance_meters)) AND(total_dispatching_minute - 2 *(first_remain_eta - last_remain_eta) <0 ) AND(last_route_distance_meters > 3000)) THEN TRUE 
        ELSE FALSE END as is_follow
FROM FINAL_DATA 
WHERE 1=1
    AND seq_id != last_seq_id
)

, FOLLOW_INFO_DRIVER AS(
SELECT
    DISTINCT
    date_kr,
    driver_id,
    seq_id,
    activity_status,
    start_at_kr,
    end_at_kr,
    total_dispatching_minute,
    is_follow,
    destination_assigned_area_name,
    destination_assigned_area_lng,
    destination_assigned_area_lat
FROM FOLLOW_INFO
)

, MERGE_INFO AS(
SELECT
    s.date_kr,
    d.start_at_kr,
    d.end_at_kr,
    s.driver_id,
    d.seq_id,
    TIME(EXTRACT(HOUR FROM DATETIME(s.gps_updated_at, 'Asia/Seoul')), CAST(FLOOR(EXTRACT( MINUTE FROM DATETIME(s.gps_updated_at, 'Asia/Seoul'))/30)*30 AS INT64), 00) as gps_time_kr_30min,
    DATETIME(s.gps_updated_at, 'Asia/Seoul') as gps_updated_at_kr,

    CASE WHEN st_distance(st_geogpoint(s.vehicle_location_lng, s.vehicle_location_lat), st_geogpoint(s.assigned_area_lng, s.assigned_area_lat)) <= 1500 THEN True
        WHEN is_follow = False THEN False
        WHEN is_follow = True THEN True
        WHEN is_follow is NULL THEN False
        END AS is_follow,
    s.activity_status,
    tada_udf.geo_to_h3(vehicle_location_lng, vehicle_location_lat, 7) as current_h3_l7,
    tada_udf.geo_to_h3(assigned_area_lng, assigned_area_lat, 7) as assigned_h3_l7,
    s.vehicle_location_lng,
    s.vehicle_location_lat,
    s.assigned_area_name,
    s.assigned_area_lng,
    s.assigned_area_lat,
    st_distance(st_geogpoint(s.vehicle_location_lng, s.vehicle_location_lat), st_geogpoint(s.assigned_area_lng, s.assigned_area_lat)) as straight_meters,
    FROM tada_prod_us.supply_snapshot as s
    JOIN DRIVER as d ON s.activity_status = d.activity_status AND s.driver_id = d.driver_id AND DATETIME(s.gps_updated_at, 'Asia/Seoul') >= d.start_at_kr AND DATETIME(s.gps_updated_at, 'Asia/Seoul') <= d.end_at_kr
    LEFT JOIN FOLLOW_INFO_DRIVER as f ON s.date_kr = f.date_kr AND s.driver_id = f.driver_id AND DATETIME(s.gps_updated_at, 'Asia/Seoul') BETWEEN  f.start_at_kr AND f.end_at_kr
WHERE 1=1
    AND driver_type = 'LITE'
    AND s.activity_status = 'DISPATCHING'
    AND s.date_kr between DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 4 DAY) and CURRENT_DATE('Asia/Seoul')
ORDER BY date_kr, driver_id, gps_updated_at_kr
)


, CONTIUNE_DISPATCHING AS ( 
SELECT
    *,
    LAST_VALUE(gps_updated_at_kr) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_gps_updated_at_kr_per_seq,
    LAST_VALUE(gps_time_kr_30min) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_gps_time_kr_30min_per_seq,
    ROW_NUMBER() OVER(PARTITION BY date_kr, driver_id, seq_id, current_h3_l7 ORDER BY gps_updated_at_kr) as rn
FROM MERGE_INFO
ORDER BY date_kr, driver_id, gps_updated_at_kr
)

, DISPATCHING_INFO AS (
SELECT
DISTINCT
*
FROM(

    SELECT
    *
    FROM CONTIUNE_DISPATCHING
    WHERE 1=1
    AND  gps_updated_at_kr = last_gps_updated_at_kr_per_seq
    UNION ALL

    SELECT
    *
    FROM CONTIUNE_DISPATCHING
    WHERE 1=1
    AND  rn=3
    AND gps_time_kr_30min != last_gps_time_kr_30min_per_seq
)
ORDER BY date_kr, driver_id, gps_updated_at_kr
)

, ACTUAL_SUPPLY AS(
SELECT
    date_kr,
    gps_time_kr_30min,
    current_h3_l7,
    COUNTIF(is_follow=True) as c_follow_supply,
    COUNTIF(is_follow=False) as c_unfollow_actual_supply,
    -- COUNT(*) as total_actual_supply
FROM DISPATCHING_INFO
GROUP BY 1,2,3
ORDER BY 1,2,3
)

, IF_ALLFOLLOW_SUPPY AS (
SELECT
    date_kr,
    gps_time_kr_30min,
    assigned_h3_l7,
    COUNTIF(is_follow=True) as c_follow_supply,
    COUNTIF((is_follow=False) AND (gps_updated_at_kr = last_gps_updated_at_kr_per_seq)) as c_unfollow_will_supply,
    -- COUNTIF(is_follow=True) +  COUNTIF((is_follow=False) AND (gps_updated_at_kr = last_gps_updated_at_kr_per_seq))  as total_will_supply
FROM DISPATCHING_INFO
GROUP BY 1,2,3
ORDER BY 1,2,3
)


, TS_DUMMY AS(
SELECT 
    DISTINCT
    DATETIME(target_timestamp, 'Asia/Seoul') as target_timestamp_kr,
    h3_origin as h3_l7,
    sgg_nm as gu,
FROM `kr-co-vcnc-tada.tada_ml_monitoring.reallocate_h3_prod_v2` as p
JOIN tada_meta.h3_index_mapping as h ON p.h3_origin = h.h3_index_7
WHERE DATE(target_timestamp, 'Asia/Seoul') between DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 4 DAY) and CURRENT_DATE('Asia/Seoul')
    AND sido_nm like '%서울%'
    AND type = "LITE"
    AND vehicle_region_type = "SEOUL"
)


, HISTORY_DATA AS(
SELECT
    date_kr,
    TIME(EXTRACT(HOUR FROM DATETIME(created_at, 'Asia/Seoul')), CAST(FLOOR(EXTRACT( MINUTE FROM DATETIME(created_at, 'Asia/Seoul'))/30)*30 AS INT64), 00) as created_time_kr_30min,
    tada_udf.geo_to_h3(origin_lng, origin_lat, 7)  as h3_l7,
    COUNTIF(is_valid=True) as c_demand,
    COUNTIF(status='DROPPED_OFF') as c_dropoff,
    COUNTIF(is_valid=True) - COUNTIF(status='DROPPED_OFF') as c_fail,
FROM tada_ext.ride_ext
WHERE date_kr between DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 4 DAY) and CURRENT_DATE('Asia/Seoul')
    AND type = "LITE"
GROUP BY 1,2,3
)

, PLUS_DATA AS(
SELECT
    date_kr,
    TIME(EXTRACT(HOUR FROM DATETIME(created_at, 'Asia/Seoul')), CAST(FLOOR(EXTRACT( MINUTE FROM DATETIME(created_at, 'Asia/Seoul'))/30)*30 AS INT64), 00) as created_time_kr_30min,
    tada_udf.geo_to_h3(origin_lng, origin_lat, 7)  as h3_l7,
    COUNTIF(is_valid=True) as plus_demand
FROM tada_ext.ride_ext
WHERE date_kr between DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 4 DAY) and CURRENT_DATE('Asia/Seoul')
    AND type = "PREMIUM"
GROUP BY 1,2,3
)



, SUPPLY_SNAPSHOT_DATA AS (
SELECT 
  date_kr,
  gps_time_kr_30min,
  h3_l7,
  ROUND(countif(activity_status in ('DISPATCHING', 'RIDING'))/6,1) as snapshot_supply,
  ROUND(countif(activity_status in ('IDLE'))/6,1) as snapshot_idle,
FROM (
  SELECT 
        date_kr,
        vehicle_id, 
        driver_id, 
        vehicle_location_lng, 
        vehicle_location_lat, 
        tada_udf.geo_to_h3(vehicle_location_lng, vehicle_location_lat, 7) h3_l7,
        vehicle_location_address,
        TIME(EXTRACT(HOUR FROM DATETIME(gps_updated_at, 'Asia/Seoul')), CAST(FLOOR(EXTRACT( MINUTE FROM DATETIME(gps_updated_at, 'Asia/Seoul'))/30)*30 AS INT64), 00) as gps_time_kr_30min,
        DATETIME(gps_updated_at, 'Asia/Seoul') as gps_updated_at_kr, 
        activity_status, 
        SPLIT(vehicle_location_address," ")[SAFE_OFFSET(1)] gu
  FROM `kr-co-vcnc-tada.tada_prod_us.supply_snapshot` 
    JOIN `kr-co-vcnc-tada.tada_meta.south_korea_shp` gis ON st_contains(ST_GEOGFROMTEXT(gis.geometry), st_geogpoint(vehicle_location_lng, vehicle_location_lat))
    AND date_kr between DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 4 DAY) and CURRENT_DATE('Asia/Seoul')
  AND driver_type = 'LITE'
  AND sido_nm like '%서울%'
)
GROUP BY 1,2,3
)

--- 배회
, AGENCY AS (
SELECT 
    d.id as driver_id,
    d.name as name,
    a.name as agency_name,
    type
FROM `kr-co-vcnc-tada.tada.driver` as d
LEFT JOIN `tada.driver_agency` as a ON d.agency_id = a.id
)

, BAEHAE_CANDIDATE AS(
SELECT
*
FROM
(
    SELECT
    *
    FROM(
        SELECT
        *,
        LEAD(assigned_area_name) OVER (PARTITION BY filled_ride_id ORDER BY seq_id) as next_assigned_area_name,
        LAST_VALUE(assigned_area_name) OVER (PARTITION BY filled_ride_id ORDER BY seq_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_assigned_area_name
        FROM(
            SELECT
                LAST_VALUE(ride_id IGNORE NULLS) OVER (PARTITION BY schedule_start_at, schedule_end_at, a.driver_id ORDER BY seq_id DESC ) AS filled_ride_id,
                a.driver_id,
                a.seq_id,
                a.activity_status,
                DATETIME(a.start_at, 'Asia/Seoul') as start_at_kr,
                DATETIME(a.end_at, 'Asia/Seoul') as end_at_kr,
                TIMESTAMP_DIFF(a.end_at,a.start_at, MINUTE) as activity_minutes,
                a.start_at,
                a.end_at,
                type,
                h.assigned_area_name,
                h.assigned_area_lng,
                h.assigned_area_lat,
            FROM tada.driver_activity as a
            JOIN tada.driver_working_info as w ON a.driver_id = w.driver_id AND a.seq_id between w.seq_id_start and w.seq_id_end
            JOIN tada.driver_assigned_area_history as h ON a.driver_id = h.driver_id and a.start_at >= h.start_at and a.end_at <= h.end_at
            JOIN AGENCY as ag ON ag.driver_id = a.driver_id
            WHERE 1=1
                AND date_kr between DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 4 DAY) and CURRENT_DATE('Asia/Seoul')
                AND type = 'LITE'
                AND activity_status in ('DISPATCHING', 'IDLE','RIDING')
        )
    )
    WHERE 1=1
        AND assigned_area_name !=last_assigned_area_name
        AND assigned_area_name !=next_assigned_area_name
        AND filled_ride_id is not NULL
)
WHERE 1=1
    AND activity_status = 'IDLE'
    AND activity_minutes > 10
)


, FINAL_BAEHAE_DATA AS(
SELECT
    DISTINCT
    date_kr,
    filled_ride_id,
    seq_id,
    driver_id,
    driver_type as type,
    start_at_kr,
    end_at_kr,
    activity_status,
    activity_minutes,
    assigned_area_name,
    assigned_area_lng,
    assigned_area_lat,
    start_gu,
    end_gu,
    start_h3,
    end_h3,
    straight_meters,
    first_vehicle_location_lng,
    first_vehicle_location_lat,
    last_vehicle_location_lng,
    last_vehicle_location_lat,

FROM(
    SELECT
        *,
        st_distance(st_geogpoint(first_vehicle_location_lng, first_vehicle_location_lat), st_geogpoint(last_vehicle_location_lng, last_vehicle_location_lat)) as straight_meters,
        FIRST_VALUE(gu) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING ) as start_gu,
        LAST_VALUE(gu) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING ) as end_gu,
        FIRST_VALUE(current_h3_l7) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING ) as start_h3,
        LAST_VALUE(current_h3_l7) OVER(PARTITION BY date_kr, driver_id, seq_id ORDER BY gps_updated_at_kr ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING ) as end_h3,
        FROM(
        SELECT
        date_kr,
        filled_ride_id,
        seq_id,
        DATETIME(gps_updated_at, 'Asia/Seoul') as gps_updated_at_kr,
        s.vehicle_id,
        s.driver_id,
        s.driver_type,
        s.vehicle_location_address,
        vehicle_location_lng, 
        vehicle_location_lat, 
        SPLIT(vehicle_location_address," ")[SAFE_OFFSET(1)] gu,
        tada_udf.geo_to_h3(vehicle_location_lng, vehicle_location_lat, 7) as current_h3_l7,
        s.activity_status,
        FIRST_VALUE(vehicle_location_lng) OVER(PARTITION BY date_kr, s.driver_id, seq_id ORDER BY gps_updated_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING ) as first_vehicle_location_lng,
        FIRST_VALUE(vehicle_location_lat) OVER(PARTITION BY date_kr, s.driver_id, seq_id ORDER BY gps_updated_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING ) as first_vehicle_location_lat,
        LAST_VALUE(vehicle_location_lng) OVER(PARTITION BY date_kr, s.driver_id, seq_id ORDER BY gps_updated_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING ) as last_vehicle_location_lng,
        LAST_VALUE(vehicle_location_lat) OVER(PARTITION BY date_kr, s.driver_id, seq_id ORDER BY gps_updated_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING ) as last_vehicle_location_lat,
        s.assigned_area_name,
        s.assigned_area_lng,
        s.assigned_area_lat,
        next_assigned_area_name,
        last_assigned_area_name,
        start_at_kr,
        end_at_kr,
        activity_minutes,
    FROM tada_prod_us.supply_snapshot as s
    JOIN BAEHAE_CANDIDATE as b ON s.driver_id = b.driver_id and s.gps_updated_at between b.start_at and b.end_at
    WHERE 1=1
    AND date_kr between DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 4 DAY) and CURRENT_DATE('Asia/Seoul')
)
)
WHERE 1=1
AND straight_meters > 500
)

, START_BAEHAE_INFO AS(
SELECT
    date_kr,
    TIME(EXTRACT(HOUR FROM start_at_kr), CAST(FLOOR(EXTRACT( MINUTE FROM start_at_kr)/30)*30 AS INT64), 00) as start_time_kr,
    start_h3,
    COUNT(*) as c_start_baehae
FROM FINAL_BAEHAE_DATA
GROUP BY 1,2,3
)

, END_BAEHAE_INFO AS(
SELECT
    date_kr,
    TIME(EXTRACT(HOUR FROM end_at_kr), CAST(FLOOR(EXTRACT( MINUTE FROM end_at_kr)/30)*30 AS INT64), 00) as end_time_kr,
    end_h3,
    COUNT(*) as c_end_baehae
FROM FINAL_BAEHAE_DATA
GROUP BY 1,2,3
)

, BAEHAE_DAILY_INFO AS (
SELECT
    date_kr,
    COUNT(*) as c_baehae,
    ROUND(avg(activity_minutes), 1) as avg_baehae_minutes,
    ROUND(sum(activity_minutes), 1) as sum_baehae_minutes
FROM FINAL_BAEHAE_DATA
WHERE start_gu in (SELECT DISTINCT sgg_nm FROM `kr-co-vcnc-tada.tada_meta.assigned_area` WHERE sido_nm like '%서울%')
GROUP BY 1
)

--- 서울 데이터로 agg 
, AGG_DATA AS(
SELECT
    target_date_kr,
    target_time_kr,
    target_timestamp_kr,
    h3_l7,
    gu,
    c_follow_supply,
    c_unfollow_actual_supply,
    IFNULL(SAFE_DIVIDE(c_unfollow_will_supply , SUM(c_unfollow_will_supply) OVER(PARTITION BY target_timestamp_kr)),0) * SUM(c_unfollow_actual_supply) OVER(PARTITION BY target_timestamp_kr) as c_unfollow_will_supply,
    c_follow_supply + c_unfollow_actual_supply as total_actual_supply,
    c_follow_supply + IFNULL(SAFE_DIVIDE(c_unfollow_will_supply , SUM(c_unfollow_will_supply) OVER(PARTITION BY target_timestamp_kr)),0) * SUM(c_unfollow_actual_supply) OVER(PARTITION BY target_timestamp_kr) as total_will_supply,
    snapshot_supply,
    snapshot_idle,
    c_demand,
    plus_demand,
    c_dropoff,
    c_fail,
    c_start_baehae,
    c_end_baehae
FROM(
    SELECT
        DATE(t.target_timestamp_kr) as target_date_kr,
        TIME(t.target_timestamp_kr) as target_time_kr,
        t.target_timestamp_kr,
        t.h3_l7,
        t.gu,
        IFNULL(a.c_follow_supply, 0) as c_follow_supply,
        IFNULL(a.c_unfollow_actual_supply,0) as c_unfollow_actual_supply,
        IFNULL(i.c_unfollow_will_supply, 0) as c_unfollow_will_supply,
        -- IFNULL(a.total_actual_supply, 0) as total_actual_supply,
        -- IFNULL(i.total_will_supply, 0) as total_will_supply,
        IFNULL(s.snapshot_supply, 0) as snapshot_supply,
        IFNULL(s.snapshot_idle, 0) as snapshot_idle,
        IFNULL(c_demand, 0) as c_demand,
        IFNULL(plus_demand, 0) as plus_demand,
        IFNULL(c_dropoff, 0) as c_dropoff,
        IFNULL(c_fail, 0) as c_fail,
        IFNULL(c_start_baehae, 0) as c_start_baehae,
        IFNULL(c_end_baehae, 0) as c_end_baehae,
    FROM TS_DUMMY as t
    LEFT JOIN ACTUAL_SUPPLY as a ON DATE(t.target_timestamp_kr) = a.date_kr AND TIME(t.target_timestamp_kr) = a.gps_time_kr_30min AND t.h3_l7 = a.current_h3_l7
    LEFT JOIN IF_ALLFOLLOW_SUPPY as i ON DATE(t.target_timestamp_kr) = i.date_kr AND TIME(t.target_timestamp_kr) = i.gps_time_kr_30min AND t.h3_l7 = i.assigned_h3_l7
    LEFT JOIN HISTORY_DATA as h ON DATE(t.target_timestamp_kr) = h.date_kr AND TIME(t.target_timestamp_kr) = h.created_time_kr_30min AND t.h3_l7 = h.h3_l7
    LEFT JOIN PLUS_DATA as p ON DATE(t.target_timestamp_kr) = p.date_kr AND TIME(t.target_timestamp_kr) = p.created_time_kr_30min AND t.h3_l7 = p.h3_l7
    LEFT JOIN SUPPLY_SNAPSHOT_DATA as s ON DATE(t.target_timestamp_kr) = s.date_kr AND TIME(t.target_timestamp_kr) = s.gps_time_kr_30min  AND t.h3_l7=s.h3_l7
    LEFT JOIN START_BAEHAE_INFO as s_b ON DATE(t.target_timestamp_kr) = s_b.date_kr AND TIME(t.target_timestamp_kr) = s_b.start_time_kr  AND t.h3_l7=s_b.start_h3
    LEFT JOIN END_BAEHAE_INFO as e_b ON DATE(t.target_timestamp_kr) = e_b.date_kr AND TIME(t.target_timestamp_kr) = e_b.end_time_kr  AND t.h3_l7=e_b.end_h3
)
)

, FILL_NO_DATA AS(
SELECT
    target_date_kr,
    target_time_kr,
    h3_l7,
    gu,
    IF(c_dropoff > total_actual_supply, c_follow_supply + (c_dropoff-total_actual_supply), c_follow_supply) as c_follow_supply ,
    c_unfollow_actual_supply,
    c_unfollow_will_supply,
    IF(c_dropoff > total_actual_supply, total_actual_supply + (c_dropoff-total_actual_supply), total_actual_supply) as total_actual_supply,
    IF(c_dropoff > total_actual_supply, total_will_supply + (c_dropoff-total_actual_supply), total_will_supply) as total_will_supply,
    snapshot_supply,
    snapshot_idle,
    c_demand,
    plus_demand,
    c_dropoff,
    c_fail,
    c_start_baehae,
    c_end_baehae
FROM AGG_DATA
)

, LAST_DATA AS(
SELECT
    target_date_kr,
    target_time_kr,
    gu,
    SUM(c_follow_supply) as sum_c_follow_supply,
    SUM(c_unfollow_actual_supply) as sum_c_unfollow_actual_supply,
    ROUND(SUM(c_unfollow_will_supply),1) as sum_c_unfollow_will_supply,
    SUM(total_actual_supply) as sum_total_actual_supply,
    ROUND(SUM(total_will_supply), 1) as sum_total_will_supply,
    ROUND(SUM(snapshot_supply),1) as sum_snapshot_supply,
    ROUND(SUM(snapshot_idle), 1) as sum_snapshot_idle,
    SUM(c_demand) as sum_c_demand,
    SUM(plus_demand) as sum_plus_demand,
    SUM(c_dropoff) as sum_c_dropoff,
    SUM(c_fail) as sum_c_fail,
    ROUND(IFNULL(SAFE_DIVIDE(SUM(c_dropoff) , SUM(c_demand)), 1),2) as dropoff_ratio,
    ROUND(IFNULL(SAFE_DIVIDE(SUM(c_demand) , SUM(snapshot_supply)), 1),2) as c_demand_per_snapshot_suppy,
    SUM(total_actual_supply) - SUM(c_demand) as total_actual_supply_minus_c_demand,
    SUM(total_will_supply) - SUM(c_demand) as sum_total_will_supply_minus_c_demand,
    SUM(c_start_baehae) as sum_c_start_baehae,
    SUM(c_end_baehae) as sum_c_end_baehae
FROM FILL_NO_DATA 
GROUP BY 1,2,3

)


, UNFOLLOW_DAILY_METRIC AS(
SELECT
    target_date_kr,
    sum(sum_c_follow_supply) / sum(sum_total_actual_supply) as follow_ratio,
    sum(if(total_actual_supply_minus_c_demand <0, total_actual_supply_minus_c_demand, 0)) as gu_unenqual_metric,
FROM(
    SELECT
        target_date_kr,
        target_time_kr,
        gu,
        sum_c_follow_supply,
        sum_c_unfollow_actual_supply,
        sum_c_unfollow_will_supply,
        sum_total_actual_supply,
        sum_total_will_supply,
        sum_snapshot_supply,
        sum_snapshot_idle,
        sum_c_demand,
        sum_plus_demand,
        sum_c_dropoff,
        sum_c_fail,
        dropoff_ratio,
        c_demand_per_snapshot_suppy,
        total_actual_supply_minus_c_demand,
        ROUND(sum_total_will_supply_minus_c_demand, 1) as sum_total_will_supply_minus_c_demand,
        sum_c_start_baehae,
        sum_c_end_baehae,
    FROM LAST_DATA as l
)
GROUP BY 1
)

, UNFOLLOW_AND_BAEHAE_DAILY_METRIC AS (
SELECT
    target_date_kr,
    follow_ratio,
    gu_unenqual_metric,
    c_baehae,
    avg_baehae_minutes,
    sum_baehae_minutes
FROM UNFOLLOW_DAILY_METRIC as d
JOIN BAEHAE_DAILY_INFO as b ON d.target_date_kr = b.date_kr
)

--- basic metric
, NEW_DEMAND AS (
SELECT
    date_kr,
    COUNT(id) as c_demand,
    COUNTIF(dropped_off_at is not null) as c_dropoff,
    IFNULL(CAST(sum(receipt_total) AS INT64), 0) as sum_receipt_total,
    IFNULL(CAST(sum(non_surge_receipt_total) AS INT64), 0) as sum_non_surge_receipt_total
FROM(
    SELECT 
        date_kr,
        DATETIME(created_at, 'Asia/Seoul') as created_at_kr,
        id,
        status,
        dropped_off_at,
        receipt_total / 1.1 as receipt_total,
        IFNULL(receipt_total * ((100/surge_percentage) / 1.1), (receipt_total / 1.1)) as non_surge_receipt_total
    FROM tada_ext.ride_ext as r
    WHERE type = 'LITE'
        AND IFNULL(SPLIT(origin_address," ")[SAFE_OFFSET(0)],SPLIT(pickup_address," ")[SAFE_OFFSET(0)]) like '%서울%'
        AND is_valid = True
        AND date_kr between DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 4 DAY) and CURRENT_DATE('Asia/Seoul')
)
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
  AND driver_type = 'LITE'
  AND sido_nm like '%서울%'
)
WHERE date_kr between DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 4 DAY) and CURRENT_DATE('Asia/Seoul')
GROUP BY 1
)

, CAR_RIDING_RATIO AS (
SELECT
  DATE(ts, "Asia/Seoul") date_kr,
  COUNT(IF(activity_status = 'RIDING', ts, null)) as riding_minutes,
  COUNT(IF(activity_status = 'DISPATCHING', ts, null)) as dispatching_minutes
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
      JOIN tada.driver as d on dact.driver_id = d.id
      WHERE 1=1
      AND d.type = 'LITE'
      AND dact.activity_status IN ('RIDING', 'DISPATCHING')
      AND dact.driver_id in (SELECT DISTINCT driver_id FROM tada.driver_assigned_area_history as h JOIN tada_meta.assigned_area as a ON h.assigned_area_name = a.name WHERE sido_nm like '%서울%')
      AND DATE(dact.start_at, 'Asia/Seoul') between DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 4 DAY) and CURRENT_DATE('Asia/Seoul')

  ), UNNEST(timestamp_array) ts
)
GROUP BY
  date_kr
ORDER BY date_kr
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
    ROUND(SUM(IF(activity_status in ('DISPATCHING'), sum_distance_delta_meters, 0)),1) as dispatching_distance_meters, 
    ROUND(SUM(IF(activity_status in ('RIDING'), sum_distance_delta_meters, 0)),1) as riding_distance_meters, 
    ROUND(SUM(sum_distance_delta_meters) * 0.187,0) as daily_fuel_cost
FROM tada_ext.driver_activity_distance as d
JOIN AGENCY as a ON d.driver_id = a.driver_id
WHERE 1=1
    AND d.driver_id in (SELECT DISTINCT driver_id FROM tada.driver_assigned_area_history as h JOIN tada_meta.assigned_area as a ON h.assigned_area_name = a.name WHERE sido_nm like '%서울%')
    AND type = "LITE"
    AND activity_status in ('DISPATCHING', 'RIDING')
    AND date_kr between DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 4 DAY) and CURRENT_DATE('Asia/Seoul')
GROUP BY 1,2
)
GROUP BY 1
)


, DAILY_DISPATCH_METRIC AS(
SELECT
    d.date_kr,
    d.c_demand,
    d.c_dropoff,
    sum_receipt_total,
    sum_non_surge_receipt_total,
    snapshot_supply,
    riding_minutes,
    dispatching_minutes,
    sum_dispatching_distance_meters,
    sum_riding_distance_meters,
    sum_daily_fuel_cost
FROM NEW_DEMAND as d
JOIN NEW_SUPPLY as s ON d.date_kr = s.date_kr
JOIN CAR_RIDING_RATIO as c ON d.date_kr = c.date_kr
JOIN FUEL_COST as f ON d.date_kr = f.date_kr
)

SELECT
date_kr,
c_demand,
c_dropoff,
sum_receipt_total,
sum_non_surge_receipt_total,
sum_daily_fuel_cost,
snapshot_supply,
riding_minutes,
dispatching_minutes,
ROUND(sum_dispatching_distance_meters, 1) as sum_dispatching_distance_meters,
ROUND(sum_riding_distance_meters, 1) as sum_riding_distance_meters,
ROUND(follow_ratio, 2) as follow_ratio,
gu_unenqual_metric,
c_baehae,
avg_baehae_minutes,
sum_baehae_minutes,

-- 종합 metric
ROUND(c_demand / snapshot_supply, 2) as c_demand_per_snapshot_supply, -- 공급 대비 수요
ROUND(c_dropoff / c_demand, 2) as dropoff_ratio,
ROUND(c_baehae / (c_dropoff + c_baehae), 2) as c_baehae_ratio,   -- 배회 건수 / (배회건수 + 하차완료수)
ROUND(sum_baehae_minutes / (riding_minutes + sum_baehae_minutes), 2) as baehae_minutes_ratio, -- 배회(분) / (라이딩(분) + 배회(분))
ROUND(sum_riding_distance_meters / (sum_riding_distance_meters + sum_dispatching_distance_meters), 2) as ride_distance_meters_per_total_move_meters,
ROUND(sum_dispatching_distance_meters / (sum_riding_distance_meters + sum_dispatching_distance_meters), 2) as dispatching_distance_meters_per_total_move_meters,
ROUND(riding_minutes / (riding_minutes + dispatching_minutes), 2) as riding_ratio,
ROUND(c_dropoff / ((riding_minutes + dispatching_minutes) / 60), 2) as c_dropoff_per_working_hour,
ROUND(sum_receipt_total / ((riding_minutes + dispatching_minutes) / 60), 2) as sum_receipt_total_per_working_hour,
ROUND(sum_non_surge_receipt_total / ((riding_minutes + dispatching_minutes) / 60), 2) as sum_non_surge_receipt_total_per_working_hour,
ROUND((sum_receipt_total - sum_daily_fuel_cost) / ((riding_minutes + dispatching_minutes) / 60), 2) as sum_receipt_total_minus_sum_daily_fuel_cost_per_working_hour, -- (서징 포함 매출 - 유류비) / 일한 시간
ROUND((sum_non_surge_receipt_total - sum_daily_fuel_cost) / ((riding_minutes + dispatching_minutes) / 60), 2) as sum_non_receipt_total_minus_sum_daily_fuel_cost_per_working_hour, -- (서징 미포함 매출 - 유류비) / 일한 시간
'LITE' as type,
'SEOUL' as region

FROM DAILY_DISPATCH_METRIC as d
JOIN UNFOLLOW_AND_BAEHAE_DAILY_METRIC as u ON d.date_kr = u.target_date_kr
WHERE date_kr between DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 3 DAY) and DATE_SUB(CURRENT_DATE('Asia/Seoul'), INTERVAL 1 DAY)
ORDER BY date_kr