# https://www.acmicpc.net/problem/2661
import sys
sys.setrecursionlimit(10000)


N = int(input())

def is_safe(string):
    length = len(string)
    loop = length // 2
    start = length - 1
    end = length
    #i 는 자릿수
    for i in range(1, loop+1):
        if string[start-i: end-i] == string[start:end]:
            return False
        start -= 1
    return True

def dfs(length, string):
    if length == N:
        print(int(string))
        exit(0)
    for i in range(1, 4):
        if is_safe(string + str(i)):
            dfs(length+1, string+str(i))

dfs(1, "1")