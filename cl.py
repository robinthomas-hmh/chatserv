import socket
import sys
import threading
from threading import Thread
from socketserver import ThreadingMixIn

class server_thread(Thread):

    def run(self):
        self.c_socket.send(self.hello_msg.encode())
        srv_helo_rep = self.c_socket.recv(2048).decode()
        print("\n",srv_helo_rep)

        #msg_test = input("Please enter join msg")
        msg_to_join = "JOIN_CHATROOM: "+self.cl_chatroom+"\nCLIENT_IP: "+str(self.cl_client_ip)+"\nPORT: "+str(self.cl_client_port)+"\nCLIENT_NAME: "+self.cl_client_name+"\n"
        self.cl_socket.send(msg_to_join.encode())
        while True:
            message_server = self.cl_socket.recv(2048).decode()
            if "DISCONNECT" in message_server:
                print(message_server)
                flag=1
                self.cl_socket.close()
                sys.exit()
            else:
                if len(message_server)>0:
                    print(message_server)

                sys.stdout.write("Type a Message: ")
                sys.stdout.flush()
                message_client = sys.stdin.readline()
                self.cl_socket.send(message_client.encode())
				
    def __init__(self,cl_socket,cl_client_ip,cl_client_port,cl_chatroom,cl_client_name,hello_msg):
        Thread.__init__(self)
        self.cl_socket = cl_socket
        self.cl_client_ip = cl_client_ip
        self.cl_client_port = cl_client_port
        self.cl_chatroom = cl_chatroom
        self.cl_client_name = cl_client_name
        self.hello_msg = hello_msg

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
    print("Enter IP address and port number")
    exit()
chatroom = input("Enter the name of the chatroom: ")
client_ip = 0
client_port = 0
client_name = input("Please enter the name of the client : ")
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
client_socket.connect((IP_address, Port))
Port2 = 5050
flag=0
threads = []

helo_msg = input("Enter helo:")


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