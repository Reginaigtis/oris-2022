import socket as Socket

game_field = [['' for k in range(4)] for i in range(4)]


def is_win():
    win = ['XXXX', '0000']
    combination = ''
    for i in range(len(game_field)):
        combination += game_field[i][i]
    if combination in win:
        return True
    combination = ''
    for i in range(len(game_field)):
        combination += game_field[i][len(game_field) - 1 - i]
    if combination in win:
        return True
    for i in range(len(game_field)):
        combination = ''
        combination2 = ''
        for k in range(len(game_field[i])):
            combination += game_field[i][k]
            combination2 += game_field[k][i]
        if combination in win or combination2 in win:
            return True
    return False


def is_draw():
    for i in game_field:
        for k in i:
            if not k:
                return False
    return True


with Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM) as socket:
    socket.bind(('localhost', 2000))
    socket.listen()
    conn1, addr1 = socket.accept()
    conn2, addr2 = socket.accept()
    conn1.sendall('cross'.encode('utf-8'))
    conn2.sendall('zero'.encode('utf-8'))
    while True:
        data = conn1.recv(1024)
        if not data:
            break
        coordinates = data.decode('utf-8')
        game_field[int(coordinates[0])][int(coordinates[1])] = 'X'
        conn2.sendall(data)
        if is_win():
            conn1.sendall('win'.encode('utf-8'))
            conn2.sendall('lose'.encode('utf-8'))
            break
        data = conn2.recv(1024)
        if not data:
            break
        coordinates = data.decode('utf-8')
        game_field[int(coordinates[0])][int(coordinates[1])] = '0'
        conn1.sendall(data)
        if is_win():
            conn2.sendall('win'.encode('utf-8'))
            conn1.sendall('lose'.encode('utf-8'))
            break
        if is_draw():
            conn2.sendall('draw'.encode('utf-8'))
            conn1.sendall('draw'.encode('utf-8'))
            break