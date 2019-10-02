#!/usr/bin/python3
from os import path
import os
import curses
import random
ROWS = 10
COLS = 20

### Data receive function with new line
def f_recvData(sock, BUF_SIZE):   # Socket instance, buffer size
 recvData = b''
 while True:
  oneChar = sock.recv(BUF_SIZE)   # Receive as the buffer size
  if oneChar == b"\n":            # Store data until new line appear
   break
  recvData += oneChar
 return recvData

### Binary data send
def f_sendBinary(sock, filename, BUF_SIZE):   # Socket instance, file name, buffer size
 with open(filename, 'rb') as f:              # Open the file to be sent
  data = f.read(BUF_SIZE)                     # Read data as buffer size  
  while data:                                 # Send data until there is no data
   sock.send(data)
   data = f.read(BUF_SIZE) 
 return 1

### Binary data receive
def f_recvBinary(sock, filename, BUF_SIZE):   # Socket instance, file name, buffer size
 countByte = 0                                # Counting received bytes
 with open(filename, 'wb') as f:              # Create a file to be downloaded
  while True:
   data = sock.recv(BUF_SIZE)                 # Receive data and store it until nothing to receive
   countByte += len(data)                     # Increase as the number received  
   f.write(data)
   if not data:
    break
 return countByte 

### Draw current state  ###
def f_draw_screen(ROWS, COLS, screen, stdscr):         # Function: draw current state
 for row in range(ROWS):
  for col in range(COLS):
   stdscr.addstr(row, col, screen[row][col])

### Generate random numbers for treasure ###
def gen_random_number(NUM_TREASURE):   # Function: generate random num for treasure
 countRandomNum = 0
 arrRandomNum = []
 while True:
  tempNum = random.randrange(1, ROWS * COLS - 1)
  if arrRandomNum.count(tempNum) < 1:  # the number doesn't exist then add it to array
   arrRandomNum.append(tempNum)
   countRandomNum += 1 
  if countRandomNum == NUM_TREASURE:   # if number of treasures are picked then return
   return arrRandomNum

### Function: convert num to 2 dimension info
def convert_num_to_position(num):   
 position = []
 row = int(num / COLS) 
 col = (num % COLS)
 position.append(row)
 position.append(col) 
 return position                    # return row, column as 2 values array  

 # Function: convert 2 dimension info to num
def convert_position_to_num(position):  
 return (position[0] * COLS) + (position[1] + 1)

 # find current player location 
def f_find_player_loc(screen, player, rows, cols): 
  location = []
  for row in range(rows):
     for col in range(cols):
        if screen[row][col] == player:
           location.append(row)
           location.append(col) 
           return location 
  return -1
