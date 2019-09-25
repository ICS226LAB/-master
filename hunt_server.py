#!/usr/bin/python3

import curses
import random

def main(stdscr):
 stdscr.clear()
 screen = [['0'] * 20 for _ in range(10) ]
 screen[0][0] = 'X' 
 screen[9][19] = 'Y' 
 for row in range(10):
  for col in range(20):
   stdscr.addstr(row, col, screen[row][col])
 k = stdscr.getkey()
 print(k)

def gen_random_number():
 countRandomNum = 0
 arrRandomNum = []
 while True:
  tempNum = random.randrange(1,199)
  if arrRandomNum.count(tempNum) < 1: 
   arrRandomNum.append(tempNum)
   countRandomNum += 1 
  if countRandomNum == 10:
   return arrRandomNum

print(gen_random_number())
#curses.wrapper(main)
