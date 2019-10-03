#!/usr/bin/python3

import threading

locks = []
for i in range(2):
 locks.append(threading.Semaphore())
 locks[-1].acquire()

def contactPlayer(player_id):
 player_id_str = str(player_id)
 while True:
  locks[player_id].acquire()
  print(player_id_str)
  locks[(player_id + 1) % 2].release()

num_players = 0
while num_players !=2:
 threading.Thread(target = contactPlayer, args = (num_players,)).start()
 num_players = num_players + 1
locks[0].release()