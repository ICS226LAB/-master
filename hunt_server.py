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
import pickle

BUF_SIZE = 1024                          # Receive size
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
 #screen = [['~'] * 20 for _ in range(10) ]
 #screen[0][0] = 'X'                         # reset the first screen 
 #screen[ROWS-1][COLS-1] = 'Y' 
 #for i in gen_random_number(NUM_TREASURE):
  #row = convert_num_to_position(i)[0]       # choose first value from 2-array
  #col = convert_num_to_position(i)[1]       # choose second value from 2-array 
  #screen[row][col] = '$' 
# sc.sendall(str(screen).encode('utf-8') + b'\n')  # Send the size
 screen_string = pickle.dumps(screen)       # using pickle to convert array to binary
 sc.send(screen_string)
 print('here 1')
 move = f_recvData(sc, BUF_SIZE)            # move value from client
 print(move)
 print('here2')
 sc.close()                                    # Termination

