#!/usr/bin/python3

import curses
import os
from os import path
import socket
from my_functions import f_sendBinary  # import function for sending binary data
from my_functions import f_recvData    # import function for receiving file name
from my_functions import f_draw_screen
from my_functions import gen_random_number
from my_functions import convert_num_to_position
from my_functions import convert_position_to_num
from my_functions import f_find_player_loc
import pickle
import struct

BUF_SIZE = 8192                          # Receive size
SMALL_BUF_SIZE = 1
HOST = ''                                # All IPs are allowed to connect
PORT = 65432                             # Port for communication
ROWS = 10
COLS = 20
NUM_TREASURE = 10
 
def main(stdscr):
 stdscr.clear()
 screen = [['~'] * 20 for _ in range(10) ]
 screen[0][0] = 'X'                         # reset the first screen 
 screen[ROWS-1][COLS-1] = 'Y' 
 for i in gen_random_number(NUM_TREASURE):
  row = convert_num_to_position(i)[0] 
  col = convert_num_to_position(i)[1]
  screen[row][col] = '$' 
 f_draw_screen(ROWS, COLS, screen, stdscr)
 k = stdscr.getkey()

###########################
#curses.wrapper(main)       # warn: always should appear after main()
###########################

screen = [['~'] * 20 for _ in range(10) ]
screen[0][0] = 'X'                         # reset the first screen 
screen[ROWS-1][COLS-1] = 'Y' 
player1_loc = [0,0]    # initial players location
player2_loc = [9,199] 
player1_point = 0
player2_point = 0


for i in gen_random_number(NUM_TREASURE):
 row = convert_num_to_position(i)[0] 
 col = convert_num_to_position(i)[1]  
 screen[row][col] = '$'  

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     # TCP socket
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # Provide an application program; socket layer, reuse port anyway
sock.bind((HOST, PORT))                                      # Designated IP and Port are used for connection
sock.listen(1)                                               # 1 connection is allowed at a time
print('Server:', sock.getsockname())

while True:
 sc, sockname = sock.accept()               # Wait until a connection is established
 print('Client:', sc.getpeername())
# sc.sendall(str(screen).encode('utf-8') + b'\n')  # Send the size

 player_name = f_recvData(sc, SMALL_BUF_SIZE)  # player name
 print(player_name)

 while True:
  screen_string = pickle.dumps(screen)   # convert array to binary
  sc.send(screen_string)                 # send screen state
  move = struct.unpack('!h',f_recvData(sc, SMALL_BUF_SIZE))[0]   # receive movement 
  #print(move) # down(258), up(259), left(260), right(261)
  player1_loc = f_find_player_loc(screen, 'X', ROWS, COLS)  # return row, col of player
  screen[player1_loc[0]][player1_loc[1]] = '~' # current set to '~'

  if move == 261: # right(261)  
   player1_loc[1] += 1  # col change if need
  elif move == 260: # left(260)
   player1_loc[1] -= 1   # col change if need
  elif move == 259: # up(259) 
   player1_loc[0] -= 1   # row change if need 
  elif move == 258: # down(258) 
   player1_loc[0] += 1   # row change if need 
  
  if screen[player1_loc[0]][player1_loc[1]] == '$':
    player1_point += 1
    print(player1_point)
  screen[player1_loc[0]][player1_loc[1]] = 'X'
   
  if (player1_point + player2_point) == NUM_TREASURE:
    print('game over')
 
 sc.close()                                    # Termination

