import socket
import sys
import threading
from threading import Thread
from socketserver import ThreadingMixIn

class server_thread(Thread):
    def __init__(self,c_socket,c_client_ip,c_client_port,c_chatroom,c_client_name,hello_msg):
        Thread.__init__(self)
        self.c_socket = c_socket
        self.c_client_ip = c_client_ip
        self.c_client_port = c_client_port
        self.c_chatroom = c_chatroom
        self.c_client_name = c_client_name
        self.hello_msg = hello_msg

    def run(self):
        self.c_socket.send(self.hello_msg.encode())
        helo_reply_from_server = self.c_socket.recv(2048).decode()
        print("\n",helo_reply_from_server)

        #msg_test = input("Please enter join msg")
        msg_to_join = "JOIN_CHATROOM: "+self.c_chatroom+"\nCLIENT_IP: "+str(self.c_client_ip)+"\nPORT: "+str(self.c_client_port)+"\nCLIENT_NAME: "+self.c_client_name+"\n"
        self.c_socket.send(msg_to_join.encode())
        while True:
            message_server = self.c_socket.recv(2048).decode()
            if "DISCONNECT" in message_server:
                print(message_server)
                flag=1
                self.c_socket.close()
                sys.exit()
            else:
                if len(message_server)>0:
                    print(message_server)

                sys.stdout.write("Type a Message: ")
                sys.stdout.flush()
                message_client = sys.stdin.readline()
                self.c_socket.send(message_client.encode())

class server_reply(Thread):
    def __init__(self,c_socket):
        Thread.__init__(self)
        self.c_socket = c_socket

    def run(self):
        client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket2.connect((IP_address, Port2))
        #print("test: inside thread reply")
        while True:
            if flag==0:
                msg_from_server=client_socket2.recv(1024).decode()
                print(msg_from_server)
            if flag == 1:
                client_socket2.close()
                sys.exit()



client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print("Please provide IP address and port number")
    exit()
chatroom = input("Enter the chatroom name: ")
client_ip = 0
client_port = 0
client_name = input("Enter the client name: ")
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
client_socket.connect((IP_address, Port))
Port2 = 5050
flag=0
threads = []

helo_msg = input("Enter helo message:")


try:
    clientThread = server_thread(client_socket,client_ip,client_port,chatroom,client_name,helo_msg)
    clientThread.daemon = True
    clientThread.start()

    clientThread2 = server_reply(client_socket)
    clientThread2.daemon = True
    #clientThread2.start()
    threads.append(clientThread)
    #threads.append(clientThread2)
    while True:
        for t in threads:
            t.join(600)
            if not t.isAlive():
                break
        break
except KeyboardInterrupt:
        client_socket.send("Bye".encode())
        sys.exit()