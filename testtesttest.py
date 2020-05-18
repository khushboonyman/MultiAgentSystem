# -*- coding: utf-8 -*-
"""
Created on Sun May 17 22:50:45 2020

@author: Bruger
"""
sys.setrecursionlimit(100)

a = [[0,0,0,0,0],[0,1,2,3,0],[0,1,2,0,0],[0,0,0,0,0]]
x = [[99,99,99,99,99],[99,-1,-1,-1,99],[99,-1,0,99,99],[99,99,99,99,99]]

max_row = 2

memo = set()
def ComputeOpt(row,col) :    
    if col > 3 or row > 3 or col < 0 or row < 0 :         
        return 99
    if x[row][col] != -1 :
        return x[row][col]
    if (row,col) not in memo :
        memo.add((row,col))
        x[row][col] = 1 + min(ComputeOpt(row,col+1),ComputeOpt(row,col-1),ComputeOpt(row+1,col),ComputeOpt(row-1,col))
        return x[row][col]
    return 99

ComputeOpt(1,1)
           


x = [-1]*10
x[0] = 0

def ComputeOpt(y) :
    if y < 0 or y > 9 :
        return 99
    if x[y] != -1 :
        return x[y]
    x[y] = 1 + min(ComputeOpt(y-1),ComputeOpt(y-2),ComputeOpt(y-3))
    
    return x[y]

ComputeOpt(9)


    