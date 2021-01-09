def practice(s:str) -> int:
    left = 0;
    right = 0;
    
    n = len(s)
    memo = set()
    longgest = 0
    while left < n and right < n:
        if s[right] not in memo:
            memo.add(s[right])
            longgest = max(longgest, right-left+1)
            right += 1;
        else:
            memo.removes(s[left])
            left += 1;
    
    return longgest