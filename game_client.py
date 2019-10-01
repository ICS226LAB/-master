import socket
import pickle

HEADERSIZE = 10
BUF_SIZE = 1024
HOST = '0.0.0.0'
PORT = 12345

GAME_DATA = {
    "playerId": "",
    "map": [],
    "status": "waiting",
    "currentPlayer": None,
    "message": ""
}


def printMap():
    MAP = GAME_DATA["map"]
    if len(MAP) > 0:
        ROW = len(MAP)
        COL = len(MAP[0])

        for row in range(ROW):
            for col in range(COL):
                if col < (COL - 1):
                    print(MAP[row][col], end=' ')
                else:
                    print(MAP[row][col])
    return None


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


def printScore(playerData={}):
    print("==== SCORE ====")
    for player in playerData.values():
        print(f'Player {player["name"]}: {player["score"]}')
    print("===============")


# set up connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
print('Connected to server.')
sendData(sock, 'connect')

while True:
    data = receiveData(sock)
    GAME_DATA = data["gameData"]
    print(GAME_DATA["message"])
    printMap()

    print("Game status:", GAME_DATA["status"])

    if(GAME_DATA["status"] == "ready" and data["playerId"] == GAME_DATA["currentPlayer"]):
        print('\n\n')
        printScore(data["playerData"])
        move = input("Your move: ")
        sendData(sock, move)
    elif (GAME_DATA["status"] == "over"):
        printScore(data["playerData"])
        print("GAME OVER.")
        break
    else:
        print("Waiting other player...")

sock.close()
