class Solution:
    def sprialOrdrer(self, matrix: List[List[int]]) -> List[int]:
        if not matrix:
            return []
        
        row_start, row_end, col_start, col_end = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
        output = []

        while row_start <= row_end or col_start <= col_end:
            # right
            if row_start <= row_end:
                output.extend([matrix[row_start][i]for i in range(col_start, col_end+1)])
                row_start += 1

            # down
            if col_start <= col_end:
                output.extend([matrix[i][col_end] for i in range(row_start, row_end + 1)])
                col_end -= 1

            # left
            if row_start <= row_end:
                output.extend([matrix[row_end][i] for i in range(col_end, col_start -1, -1)])
                row_end -= 1

            # up
            if col_start <= col_end:
                output.extend([matrix[i][col_start] for i in range(row_end, row_start -1, -1)])
                col_start += 1


        return output