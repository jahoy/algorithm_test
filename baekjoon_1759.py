# https://www.acmicpc.net/problem/1759

import sys


def check(comb_str):
    vowel = 0
    consonant = 0
    for char in comb_str:
        if char in ['a', 'e', 'i', 'o', 'u']:
            vowel += 1
        else:
            consonant += 1
    if consonant >=2 and vowel >= 1:
        return True
    else:
        return False 

def solve(L, arr, comb_str, index):
    if len(comb_str) == L:
        if check(comb_str) == True:
            print(''.join(comb_str))
        return
    if index >= len(arr):
        return
    
    solve(L, arr, comb_str + list(arr[index]), index + 1) # 포함 경우
    solve(L, arr, comb_str, index+1) # 미포함 경우

input = sys.stdin.readline
L, C = map(int, input().split())
arr = list(map(str, input().split()))
arr.sort()

comb_str = []
index = 0
solve(L, arr, comb_str, index)


