import socket
import argparse
import threading
import select
import errno


# opcodes
NAM = 1  # initial username message / login 
MES = 2  # message data 
PER = 3  # permisson from server to send messages to chat / connection successful
END = 4  # signal to end connetcion

MSG_SIZE = 1024  # message size

FORMAT = "utf-8"


# send message to each client
def send_to_clietns(message):
    _, ready_for_writing, _ = select.select([], clients.keys(), [])  # get client sockets that are ready for writing
    for client in ready_for_writing:
        if client != server_socket:
            client.send(message)

# method to handle the incoming messages
def handle_client(connection):
    msg = connection.recv(MSG_SIZE)

    if len(msg) == 0:
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        print(clients[connection], 'disconnected')
        sockets.remove(connection)
        del clients[connection]
        return

    elif msg[0] == END:
        connection.send(bytes([END]))
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        print(clients[connection], 'disconnected')
        sockets.remove(connection)
        del clients[connection]
        return

    elif msg[0] == NAM:
        client_name = msg[1:].decode(FORMAT)

        print('new client:', client_name)

        # append the name and client_socket to the respective lists
        clients[connection] = client_name
        sockets.append(connection)

        msg = bytes([PER]) + msg[1:] + bytearray(' has joined chat!'.encode(FORMAT))
        send_to_clietns(msg)

    elif msg[0] == MES:
        reply = bytes([MES]) + clients[connection].encode(FORMAT) + bytes([0]) + msg[1:] + bytes([0])
        send_to_clietns(reply)


# command line arguments parser
parser = argparse.ArgumentParser(description='Chat server')
parser.add_argument("--ip", default='0.0.0.0', type=str, help='server IP address')
parser.add_argument("--port", default=1234, type=int, help='server port')
args = parser.parse_args()
server_ip = args.ip
server_port = args.port

server_address = (server_ip, server_port)
print('Server is starting at', server_ip,':', server_port)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setblocking(False) 
server_socket.bind(server_address)
server_socket.listen() 

# lists that will contain all the client sockets connected to the server and client's names.
sockets = [server_socket]
clients = {}

try:
    while True:
        ready_for_reading, _, _ = select.select(sockets, [], [])  # get sockets that are ready for reading from clients and server sockets
        for sock in ready_for_reading:
            if sock == server_socket:
                # accept connection (returns a new socket for the client and the address bound to it)
                connection, address = server_socket.accept()  # connection == socket for client connection
                handle_client(connection)

            else:
                handle_client(sock)

except KeyboardInterrupt:
    pass
finally:
    server_socket.shutdown(socket.SHUT_RDWR)
    server_socket.close()
    print("\nserver socket closed")
