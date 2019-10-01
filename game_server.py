import sys
import random
import socket
import os
import pickle
import time
import threading


# set up game data

COL = 20
ROW = 10
MAP = [['_' for x in range(COL)] for y in range(ROW)]
TOTAL_TREASURE = 10

GAME_DATA = {
    "map": [],
    "status": "waiting",
    "currentPlayer": None,
    "nextPlayer": None,
    "message": "",
    "collectedTreasure": 0
}

PLAYER_DATA = {}

CONNS = {}


def generateGameData():
    for i in range(TOTAL_TREASURE):
        while True:
            tRow = random.randint(0, (ROW - 1))
            tCol = random.randint(0, (COL - 1))

            if (tRow + tCol == 0 or (tRow + tCol) == (COL + ROW - 2) or MAP[tRow][tCol] == "$"):
                continue

            MAP[tRow][tCol] = "$"
            break

    MAP[0][0] = "X"
    MAP[ROW-1][COL-1] = "Y"

    GAME_DATA["map"] = MAP
    return None


# generate initial game data
generateGameData()

# set up server

HEADERSIZE = 10
BUF_SIZE = 1024
HOST = ''
PORT = 12345


def sendData(sock, payload):
    dataBytes = pickle.dumps(payload)
    dataBytes = bytes(
        f"{len(dataBytes):<{HEADERSIZE}}", 'utf-8')+dataBytes
    sock.sendall(dataBytes)


def receiveData(sock):
    full_msg = b''
    new_msg = True
    data = {}

    while True:
        msg = sock.recv(BUF_SIZE)
        if len(msg) > 0:
            if new_msg:
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

            full_msg += msg

            if len(full_msg)-HEADERSIZE == msglen:
                data = pickle.loads(full_msg[HEADERSIZE:])
                return data
        else:
            return data


def updateMap(playerId, playerMove):
    playerData = PLAYER_DATA[playerId]
    row = playerData["r"]
    col = playerData["c"]
    newRow = row
    newCol = col

    if(playerMove):
        # find new pos
        if (playerMove == "left" and col - 1 >= 0):
            newCol = col - 1
        elif (playerMove == "right" and col + 1 <= COL-1):
            newCol = col + 1
        elif (playerMove == "up" and row - 1 >= 0):
            newRow = row - 1
        elif (playerMove == "down" and row + 1 <= ROW - 1):
            newRow = row + 1
        else:
            return "Invalid Move"

        # calculate score
        if (GAME_DATA["map"][newRow][newCol] == "$"):
            PLAYER_DATA[playerId]["score"] += 1
            GAME_DATA["collectedTreasure"] += 1

        tempP = GAME_DATA["currentPlayer"]
        GAME_DATA["currentPlayer"] = GAME_DATA["nextPlayer"]
        GAME_DATA["nextPlayer"] = tempP
        GAME_DATA["map"][row][col] = '_'
        GAME_DATA["map"][newRow][newCol] = playerData["name"]
        PLAYER_DATA[playerId]["r"] = newRow
        PLAYER_DATA[playerId]["c"] = newCol
    else:
        GAME_DATA["map"][row][col] = playerData["name"]

    return None


def handleClient(conn):
    while GAME_DATA["collectedTreasure"] != TOTAL_TREASURE:
        playerMove = receiveData(conn)
        playerId = conn.fileno()
        GAME_DATA["message"] = ""

        # data = data.decode('utf-8')
        if(GAME_DATA["status"] == "ready" and GAME_DATA["currentPlayer"] == playerId):
            errMsg = updateMap(playerId, playerMove)
            if errMsg:
                GAME_DATA["message"] = errMsg

        # broadcast
        if (GAME_DATA["collectedTreasure"] != TOTAL_TREASURE):
            for pID in CONNS:
                payload = {}
                payload["playerId"] = pID
                payload["gameData"] = GAME_DATA
                payload["playerData"] = PLAYER_DATA
                sendData(CONNS[pID], payload)

    GAME_DATA["status"] = "over"
    # broadcast game end
    for pID in CONNS:
        payload = {}
        payload["playerId"] = pID
        payload["gameData"] = GAME_DATA
        payload["playerData"] = PLAYER_DATA
        sendData(CONNS[pID], payload)

    # the connection is closed: unregister
    del CONNS[conn.fileno()]


def runListener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                    1)  # More on this later
    sock.bind((HOST, PORT))
    sock.listen(2)
    print('Server:', sock.getsockname())  # Source IP and port

    while GAME_DATA["status"] != "over":
        conn, addr = sock.accept()

        # register player
        playerId = conn.fileno()
        CONNS[playerId] = conn

        # Destination IP and port
        messsage = (f'Player {len(CONNS)}: {conn.getpeername()} connected.')
        if len(CONNS) == 1:
            messsage += ('\nWaiting for player 2...')
            GAME_DATA["currentPlayer"] = playerId
            PLAYER_DATA[playerId] = {"r": 0, "c": 0, "score": 0, "name": "X"}
        else:
            messsage += ('\nGame is ready.')
            GAME_DATA["status"] = "ready"
            GAME_DATA["nextPlayer"] = playerId
            PLAYER_DATA[playerId] = {"r": ROW-1,
                                     "c": COL-1, "score": 0, "name": "Y"}

        print(messsage)
        GAME_DATA["message"] = messsage

        threading.Thread(target=handleClient, args=(conn,)).start()


if __name__ == '__main__':
    runListener()
