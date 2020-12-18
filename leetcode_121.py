# https://leetcode.com/problems/best-time-to-buy-and-sell-stock/
# https://leetcode.com/problems/best-time-to-buy-and-sell-stock/discuss/39049/Easy-O(n)-Python-solution
# https://www.youtube.com/watch?v=mj7N8pLCJ6w&ab_channel=KevinNaughtonJr.


class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        max_profit = 0
        buy_price = float('inf')
        
        for price in prices:
            if price < buy_price:
                buy_price = price
            else:
                max_profit = max(max_profit, price - buy_price)
        return max_profit
        