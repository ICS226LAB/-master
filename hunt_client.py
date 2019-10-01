#!/usr/bin/python3

import socket 
import sys
import curses
from my_functions import f_recvBinary   # import f_recvBinary function
from my_functions import f_recvData     # import f_recvData function
from my_functions import f_draw_screen
import pickle
import struct

BUF_SIZE = 4096           # Buffer size for transfer
HOST = '127.0.0.1'        # Target server IP
PORT = 65432              # Port for transfer
ROWS = 10
COLS = 20
g_key = -1

if len(sys.argv) != 2:   # Arguments should be 2
 print(sys.argv[0] + ' <message>')
 sys.exit()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # TCP socket
sock.connect((HOST, PORT))                                 # Connect using IP and Port
print('Client:', sock.getsockname())
data = sys.argv[1].encode('utf-8') + b'\n'                 # Send the file name to be downloaded
sock.sendall(data)     
move = -1
def main(stdscr):
 stdscr.clear()  
 f_draw_screen(ROWS, COLS, screen, stdscr)
 move = stdscr.getch()   # down(258), up(259), left(260), right(261)
 result = sock.send(struct.pack('!h',move)) 
 key = stdscr.getkey()
 
#while True:       # continue until game ends
screen = ''
data = sock.recv(BUF_SIZE)        # Receive current state
screen = pickle.loads(data)  
curses.wrapper(main) 


sock.close()                                                   # Termination
