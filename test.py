#!/usr/bin/python3
import sys

screen = [['_'] * 20 for _ in range(10) ]
print(screen.pop(0))
screen[0][0] = 'X'

for i in range(20):
 for j in range(10):
  sys.stdout.write(screen[i][j]) 
 print('\n')
