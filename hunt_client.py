#!/usr/bin/python3

import socket 
import sys
import curses
from my_functions import f_recvBinary   # import f_recvBinary function
from my_functions import f_recvData     # import f_recvData function
from my_functions import f_draw_screen
import pickle
import struct
from my_functions import f_find_player_loc
from my_functions import f_is_game_end 
import time

BUF_SIZE = 8192           # Buffer size for transfer
HOST = '127.0.0.1'        # Target server IP
PORT = 65432              # Port for transfer
ROWS = 5
COLS = 10
g_key = -1
player_loc = []

if len(sys.argv) != 2:   # Arguments should be 2
 print(sys.argv[0] + ' <message>')
 sys.exit()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # TCP socket
sock.connect((HOST, PORT))                                 # Connect using IP and Port

data = sys.argv[1].encode('utf-8') + b'\n'                 # Send the file name to be downloaded
sock.sendall(data)  
sign = f_recvData(sock, 1).decode('utf-8')  
move = -1
print(sys.argv[1] + '! Your sign is ' + sign)
time.sleep(1)

def main(stdscr): 
 stdscr.clear()  
 f_draw_screen(ROWS, COLS, screen, stdscr)
 while True:   # input until valid key 
  move = stdscr.getch()   # down(258), up(259), left(260), right(261)
  player_loc = f_find_player_loc(screen, sign, ROWS, COLS) 
  # player_loc[0] -> row, player_loc[1] -> col
  if ((move == 261) and (player_loc[1] == COLS-1)): # right: block out of range
    continue
  elif (move == 260) and (player_loc[1] == 0): # left: block out of range
    continue
  elif (move == 259) and (player_loc[0] == 0): # up: block out of range
    continue
  elif (move == 258) and (player_loc[0] == ROWS-1): # down: block out of range
    continue
  else:  # check the other player doesn't exist 
    if move == 261: # right(261)  dup with hunt_server.py
      player_loc[1] += 1  # col change if need
    elif move == 260: # left(260) 
     player_loc[1] -= 1   # col change if need
    elif move == 259: # up(259) 
     player_loc[0] -= 1   # row change if need 
    elif move == 258: # down(258) 
     player_loc[0] += 1   # row change if need 

    if (screen[player_loc[0]][player_loc[1]] != '~') and (screen[player_loc[0]][player_loc[1]] != '$'):
        continue   # block invalid movement
    else:    # send movement info, if it is valid
        result = sock.send(struct.pack('!h',move) + b'\n') 
        #f_draw_screen(ROWS, COLS, screen, stdscr)
        break 

while True:       # continue until game ends
 screen = '' 
 buffer = sock.recv(BUF_SIZE)        # Receive current stateCV
 screen = pickle.loads(buffer)    
 if f_is_game_end(screen):
   break 
 curses.wrapper(main) 

 buffer = sock.recv(BUF_SIZE)        # Receive current stateCV
 screen = pickle.loads(buffer)   
 curses.wrapper(main)
sock.close()                                                   # Termination
