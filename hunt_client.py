#!/usr/bin/python3

import socket 
import sys
import curses
import pickle
import struct
import time
from os import system
from my_functions import f_recvBinary   # import f_recvBinary function
from my_functions import f_recvData     # import f_recvData function
from my_functions import f_draw_screen
from my_functions import f_find_player_loc
from my_functions import f_is_game_end 
from my_functions import update_loc


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
 while True:   # input until valid key        
   buffer = sock.recv(BUF_SIZE)        # Receive current stateCV
   if (buffer):
    screen = pickle.loads(buffer)
    if f_is_game_end(screen, stdscr):  # Check if found winner
      stdscr.getch()  # Wait until a key is pressed to stop the game
      break

   if f_is_game_end(screen, stdscr):  # Check if found winner
    stdscr.getch()  # Wait until a key is pressed to stop the game
    break
  
   turn = screen[ROWS][0]  # Decide player's turn
   
   stdscr.clear()  # Clear the old screen
   f_draw_screen(ROWS, COLS, screen, stdscr)  # Print the new screen
   stdscr.refresh()   # Refresh screen

   if sign == turn:
    while True:
      curses.flushinp()  # Flush all acidental key press
      move = stdscr.getch()   # down(258), up(259), left(260), right(261)
      player_loc = f_find_player_loc(screen, sign, ROWS, COLS)  

      if ((move == 261) and (player_loc[1] == COLS-1)): # right: block out of range
        continue
      elif (move == 260) and (player_loc[1] == 0): # left: block out of range
        continue
      elif (move == 259) and (player_loc[0] == 0): # up: block out of range
        continue
      elif (move == 258) and (player_loc[0] == ROWS-1): # down: block out of range
        continue
      else:  # check the other player doesn't exist 
        update_loc(player_loc, move)
        if (screen[player_loc[0]][player_loc[1]] != '~') and (screen[player_loc[0]][player_loc[1]] != '$'):
          continue   # block invalid movement
        else:    # send movement info, if it is valid
          result = sock.send(struct.pack('!h',move) + b'\n') 
          break
 
curses.wrapper(main)    

sock.close()  # Termination
