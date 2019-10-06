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
from my_functions import f_is_game_end_server
import pickle
import struct
import threading

###########################
# Initialize the game
###########################
BUF_SIZE = 8192                          # Receive size 
HOST = ''                                # All IPs are allowed to connect
PORT = 65432                             # Port for communication
ROWS = 5
COLS = 10
NUM_TREASURE = 1

screen = [['~'] * COLS for _ in range(ROWS) ]
screen[0][0] = 'X'                         # reset the first screen 
screen[ROWS-1][COLS-1] = 'Y'  

for i in gen_random_number(NUM_TREASURE):  # initialize the treasures
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

p1 = Player(0, 0, 'X',[0,0],'')
p2 = Player(1, 0, 'Y',[ROWS-1,COLS-1],'')   

# Thread >> ##########################
locks = []                
for i in range(2):
 locks.append(threading.Semaphore())   # create a single-marble semaphore
 locks[-1].acquire()                   # acquire each of marbles


##############################################################################
def contactPlayer(player_id):  
 sc, sockname = sock.accept()
 print('Client:', sc.getpeername())
 if player_id == 0:
   p = p1
 else:
   p = p2
 p.name = f_recvData(sc, 1).decode('utf-8')  # player name 
 sc.sendall(p.sign.encode('utf-8') + b'\n') 
 remain_treasure = NUM_TREASURE

 screen_string = pickle.dumps(screen)   # convert current state to binary
 sc.send(screen_string)                 # send screen state 

 while True:   
  if f_is_game_end_server(sc, p1.point, p2.point, NUM_TREASURE):
    break
  ######@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  locks[player_id].acquire()####################### each tries to acquire the marble => SWITCH STEP 1
  if f_is_game_end_server(sc, p1.point, p2.point, NUM_TREASURE):
    break
  #111111111111111111111111
  screen_string = pickle.dumps(screen)   # convert current state to binary
  sc.send(screen_string)                 # send screen state
   
  move = struct.unpack('!h',f_recvData(sc, 1))[0]   # receive movement ##### very import!!!
     #print(move) # down(258), up(259), left(260), right(261)
  p.loc = f_find_player_loc(screen, p.sign, ROWS, COLS)  # return row, col of player
  screen[p.loc[0]][p.loc[1]] = '~' # current set to '~'

  if move == 261: # right(261)  
   p.loc[1] += 1  # col change if need
  elif move == 260: # left(260)
   p.loc[1] -= 1   # col change if need
  elif move == 259: # up(259) 
   p.loc[0] -= 1   # row change if need 
  elif move == 258: # down(258) 
   p.loc[0] += 1   # row change if need 

  if screen[p.loc[0]][p.loc[1]] == '$':
   p.point += 1 
   remain_treasure -= 1 
   print(p.name + ' points: ' + str(p.point)) 
   ###>>>  End the Game to Clients!!!
   if (p1.point + p2.point) == NUM_TREASURE:
    print('>>>> Game Over <<<<')
   ###<<<
  screen[p.loc[0]][p.loc[1]] = p.sign
  # 222222222222222222222222222222222
  screen_string = pickle.dumps(screen)   # convert current state to binary
  sc.send(screen_string)                 # send screen state 

  ### $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
  locks[(player_id + 1) % 2].release()  # release other's marble  => SWITCH SETP 2

##############################################################################

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     # TCP socket
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # Provide an application program; socket layer, reuse port anyway
sock.bind((HOST, PORT))                                      # Designated IP and Port are used for connection
sock.listen(2)        #!!!!!!!! 2 connection is allowed at a time
print('Server:', sock.getsockname())

num_players = 0
while num_players !=2:     # will execute 2 times, exit
 threading.Thread(target = contactPlayer, args = (num_players,)).start()   # create a thread for each
 num_players = num_players + 1
locks[0].release()    # Start first one: Release the first marble to the 1st player 
 

