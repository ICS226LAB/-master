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
import threading

###########################
# Initialize the game
###########################
BUF_SIZE = 8192                          # Receive size
SMALL_BUF_SIZE = 1
HOST = ''                                # All IPs are allowed to connect
PORT = 65432                             # Port for communication
ROWS = 10
COLS = 20
NUM_TREASURE = 10 

screen = [['~'] * 20 for _ in range(10) ]
screen[0][0] = 'X'                         # reset the first screen 
screen[ROWS-1][COLS-1] = 'Y'  

for i in gen_random_number(NUM_TREASURE):
 row = convert_num_to_position(i)[0] 
 col = convert_num_to_position(i)[1]  
 screen[row][col] = '$'  

class Player:
 def __init__(self, no, point, sign, loc):
  self.no = no   # 0:player1, 1:player2
  self.point = point
  self.sign = sign   # X:player1, Y:player2
  self.loc = loc  # 2 dimension ex. [0,0]

p1 = Player(0, 0, 'X',[0,0])
p2 = Player(1, 0, 'Y',[ROWS-1,COLS-1])   

# Thread >> ##########################
locks = []                
for i in range(2):
 locks.append(threading.Semaphore())   # create a single-marble semaphore
 locks[-1].acquire()                   # acquire each of marbles

def contactPlayer(player_id): 
 # accept here(M)
 sc, sockname = sock.accept()
 print('Client:', sc.getpeername())
 player_name = f_recvData(sc, SMALL_BUF_SIZE)  # player name
 print(player_name) 
 while True:   
  locks[player_id].acquire()        # each tries to acquire the marble => SWITCH STEP 1
  # recv(M)
  
  # send(M)
  screen_string = pickle.dumps(screen)   # convert current state to binary
  sc.send(screen_string)                 # send screen state
  move = struct.unpack('!h',f_recvData(sc, SMALL_BUF_SIZE))[0]   # receive movement 
     #print(move) # down(258), up(259), left(260), right(261)
  p1.loc = f_find_player_loc(screen, 'X', ROWS, COLS)  # return row, col of player
  screen[p1.loc[0]][p1.loc[1]] = '~' # current set to '~'

  if move == 261: # right(261)  
   p1.loc[1] += 1  # col change if need
  elif move == 260: # left(260)
   p1.loc[1] -= 1   # col change if need
  elif move == 259: # up(259) 
   p1.loc[0] -= 1   # row change if need 
  elif move == 258: # down(258) 
   p1.loc[0] += 1   # row change if need 

  if screen[p1.loc[0]][p1.loc[1]] == '$':
   p1.point += 1
   print(p1.point)
  screen[p1.loc[0]][p1.loc[1]] = 'X'

  ### MMM  <<<
  locks[(player_id + 1) % 2].release()  # release other's marble  => SWITCH SETP 2

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     # TCP socket
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # Provide an application program; socket layer, reuse port anyway
sock.bind((HOST, PORT))                                      # Designated IP and Port are used for connection
sock.listen(2)        #!!!!!!!! 2 connection is allowed at a time
print('Server:', sock.getsockname())

# wait until 2 connections -> delete >>>>
#connections = 0
#while True:
# print('Server:', sock.getsockname())
# sc, sockname = sock.accept()               # Wait until a connection is established
# print('Client:', sc.getpeername())
# connections += 1
# player_name = f_recvData(sc, SMALL_BUF_SIZE)  # player name
# print(player_name) 
# if connections == 2:
#   break 
# <<< delte 

num_players = 0
while num_players !=2:     # will execute 2 times, exit
 threading.Thread(target = contactPlayer, args = (num_players,)).start()   # create a thread for each
 num_players = num_players + 1
locks[0].release()    # Start first one: Release the first marble to the 1st player 

# Thread << ##########################
### test fun >>>>>
def play(player_id):
  #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     # TCP socket
  #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # Provide an application program; socket layer, reuse port anyway
  #sock.bind((HOST, PORT))                                      # Designated IP and Port are used for connection
  #sock.listen(2)        #!!!!!!!! 2 connection is allowed at a time
  #print('Server:', sock.getsockname())

  while True:
   #sc, sockname = sock.accept()               # Wait until a connection is established
   #print('Client:', sc.getpeername())
   #player_name = f_recvData(sc, SMALL_BUF_SIZE)  # player name
   #print(player_name) 

   while True: 
     screen_string = pickle.dumps(screen)   # convert current state to binary
     ### 1vs1 comm 
     sc.send(screen_string)                 # send screen state
     move = struct.unpack('!h',f_recvData(sc, SMALL_BUF_SIZE))[0]   # receive movement 
     #print(move) # down(258), up(259), left(260), right(261)
     p1.loc = f_find_player_loc(screen, 'X', ROWS, COLS)  # return row, col of player
     screen[p1.loc[0]][p1.loc[1]] = '~' # current set to '~'

     if move == 261: # right(261)  
      p1.loc[1] += 1  # col change if need
     elif move == 260: # left(260)
      p1.loc[1] -= 1   # col change if need
     elif move == 259: # up(259) 
      p1.loc[0] -= 1   # row change if need 
     elif move == 258: # down(258) 
      p1.loc[0] += 1   # row change if need 
    
     if screen[p1.loc[0]][p1.loc[1]] == '$':
      p1.point += 1
      print(p1.point)
     screen[p1.loc[0]][p1.loc[1]] = 'X'
     break
     #if (p1.point + p2.point) == NUM_TREASURE:
       #print('game over')
      
  ### test fun <<<<<
  sc.close()                                    # Termination

