#!/usr/bin/python3

import curses
import os
import pickle
import struct
import threading
import socket
from os import path
from my_functions import f_sendBinary  # import function for sending binary data
from my_functions import f_recvData    # import function for receiving file name
from my_functions import f_draw_screen
from my_functions import gen_random_number
from my_functions import convert_num_to_position
from my_functions import convert_position_to_num
from my_functions import f_find_player_loc
from my_functions import f_is_game_end_server
from my_functions import update_loc

###########################
# Initialize the game
###########################
BUF_SIZE = 8192                          # Receive size 
HOST = ''                                # All IPs are allowed to connect
PORT = 65432                             # Port for communication
ROWS = 5
COLS = 10
NUM_TREASURE = 3

screen = [['~'] * COLS for _ in range(ROWS) ]
screen[0][0] = 'X'                # player X position
screen[ROWS-1][COLS-1] = 'Y'      # player Y position
screen.append('X')  # turn starts at player X

for i in gen_random_number(NUM_TREASURE):  # initialize the random treasures
 row = convert_num_to_position(i)[0] 
 col = convert_num_to_position(i)[1]  
 screen[row][col] = '$'  

class Player:
 def __init__(self, no, point, sign, loc, name):
  self.no = no   # 0:player1, 1:player2
  self.point = point
  self.sign = sign   # X:player1, Y:player2
  self.loc = loc  # 2 dimension ex. [0,0]
  self.name = name

p1 = Player(0, 0, 'X',[0,0],'')              # Player X info
p2 = Player(1, 0, 'Y',[ROWS-1,COLS-1],'')    # Player Y info

locks = []                
for i in range(2):
 locks.append(threading.Semaphore())   # create a single-marble semaphore
 locks[-1].acquire()                   # acquire each of marbles
 

def contactPlayer(player_id, stdscr, sock): 
 sc, sockname = sock.accept()
 print('Client:', sc.getpeername())
 if player_id == 0:
   p = p1
 else:
   p = p2
 p.name = f_recvData(sc, 1).decode('utf-8')  # player name 
 sc.sendall(p.sign.encode('utf-8') + b'\n') 
 remain_treasure = NUM_TREASURE
  
 screen_string = pickle.dumps(screen)   # Convert current state to binary
 sc.send(screen_string)                 # Send screen state 
  

 while True:    
  locks[player_id].acquire()   # each tries to acquire the marble => SWITCH STEP 1
  if f_is_game_end_server(sc, p1.point, p2.point, NUM_TREASURE):  # Check if found winner
    locks[(player_id + 1) % 2].release()  # Continue to the next player's turn
    break
  else:
    screen_string = pickle.dumps(screen)   # Convert current state to binary
    sc.send(screen_string)                 # Send screen state

  move = struct.unpack('!h',f_recvData(sc, 1))[0]   # Receive movement 

  p.loc = f_find_player_loc(screen, p.sign, ROWS, COLS)  # return row, col of player
  screen[p.loc[0]][p.loc[1]] = '~' # current set to '~'
  update_loc(p.loc, move)  # Update the map
  if screen[p.loc[0]][p.loc[1]] == '$':  # Check if treasure is taken
   p.point += 1  # Increase player point
   remain_treasure -= 1  # Decrease the remain treasure
   if remain_treasure == 0:    # Check game end
    print('>>>> Game is over <<<<')
    if (f_is_game_end_server(sc, p1.point, p2.point, NUM_TREASURE)):  # Check game end
      break
    
  screen[p.loc[0]][p.loc[1]] = p.sign  # I DON'T KNOW
  
  if screen[ROWS][0] == 'X':   # If current turn is player X's turn
      screen.pop()             # Remove player X's turn
      screen.append('Y')       # Add player Y's turn
  else: 
      screen.pop()             # Remove player Y's turn
      screen.append('X')       # Add player X's turn

  screen_string = pickle.dumps(screen)   # Convert current state to binary
  sc.send(screen_string)                 # Send screen state 
 
  locks[(player_id + 1) % 2].release()  # release other's marble  => SWITCH SETP 2

  screen_string = pickle.dumps(screen)   # Convert current state to binary
  sc.send(screen_string)                 # Send screen state 
 #### >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   

def main(stdscr):
 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     # TCP socket
 sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # Provide an application program; socket layer, reuse port anyway
 sock.bind((HOST, PORT))                                      # Designated IP and Port are used for connection
 sock.listen(2)        #!!!!!!!! 2 connection is allowed at a time
 print('Server:', sock.getsockname())

 num_players = 0
 while num_players !=2:     # will execute 2 times, exit
  threading.Thread(target = contactPlayer, args = (num_players, stdscr, sock, )).start()   # create a thread for each
  num_players = num_players + 1
 locks[0].release()    # Start first one: Release the first marble to the 1st player 
 
curses.wrapper(main)  

