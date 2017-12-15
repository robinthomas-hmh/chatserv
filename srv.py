import socket
import threading
import sys
from threading import Thread
import queue
import re

class client(Thread):
    def __init__(self,client_socket,client_ip,client_port):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_ip = client_ip
        self.client_port = client_port
        self.chatroom = []
        self.chatroom_id = []
        self.client_id = 0
        self.client_name = ""

    def run(self):
        chatroom_id_local = 0
        chatroom_local = ""

        while True:
            try:
                client_message = self.client_socket.recv(2048).decode()

                client_msg_helo = client_message
                if "HELO" in client_msg_helo:
                    inp_helo = client_msg_helo+"IP:"+host+"\n Port:"+str(port)+"\nStudentID:17309389\n"
                    self.client_socket.send(inp_helo.encode())

                elif "KILL_SERVICE" in client_message:
                    server_socket.shutdown(socket.SHUT_RDWR)
                    server_socket.close()
                    break;

                elif "DISCONNECT" in client_message.split(':')[0]:
                    try:
                        disconnect_msg_1 = self.client_name+" has left this chatroom.\n\n"
                        for i in self.chatroom_id:
                            disconnect_msg = "CHAT: "+str(i)+"\n CLIENT_NAME: "+self.client_name+"\nMESSAGE: "+disconnect_msg_1
                            chatroom_members = self.getChatroomMembers(i)
                            fileno_arr = []
                            for item in chatroom_members:
                                fileno_arr.append(socket_fileno[(item,i)])

                            thread_lock.acquire()
                            for key in s_queue.keys():
                                if key in fileno_arr:
                                    q = s_queue[key]
                                    q.put(disconnect_msg)
                            thread_lock.release()
                            for f_no in fileno_arr:
                                self.broadcast(f_no)
                            self.decrementCountClientChatroom()
                            self.deassignChatroom(i)
                            self.removeFileno(i)
                        self.chatroom_id = []


                    except:
                        error_msg = "ERROR_CODE: 1\nERROR_DESCRIPTION: "+str(sys.exc_info()[0])
                        self.client_socket.send(error_msg.encode())



                elif "JOIN_CHATROOM" in client_message:
                    try:
                        client_msg_to_join = client_message
                        print("\nin join",client_msg_to_join+"\n")
                        client_msg_to_join_split = re.findall(r"[\w']+",client_msg_to_join)
                        self.chatroom.append(client_msg_to_join_split[1])
                        chatroom_local = client_msg_to_join_split[1]
                        chatroom_id_local = self.getRoomId(chatroom_local);
                        self.client_name = client_msg_to_join_split[7]
                        self.getClientId()

                        self.setFileno(chatroom_id_local)
                        self.incrementCountClientChatroom()
                        self.assignChatroom(chatroom_id_local)

                        msg_joined = "JOINED_CHATROOM: "+chatroom_local+"\nSERVER_IP: "+host+"\nPORT: "+str(port)+"\nROOM_REF: "+str(chatroom_id_local)+"\nJOIN_ID: "+str(self.client_id)+"\n"
                        print(msg_joined)
                        self.client_socket.send(msg_joined.encode())

                        client_joined_msg_to_chatroom = "CHAT: "+str(chatroom_id_local)+"\nCLIENT_NAME: "+self.client_name+"\nMESSAGE: "+self.client_name + " has joined this chatroom.\n\n"
                        chatroom_members = self.getChatroomMembers(chatroom_id_local)
                        print(chatroom_members)
                        fileno_arr = []
                        for item in chatroom_members:
                            fileno_arr.append(socket_fileno[(item,chatroom_id_local)])
                        thread_lock.acquire()
                        for key in s_queue.keys():
                            if key in fileno_arr:
                                q = s_queue[key]
                                q.put(client_joined_msg_to_chatroom)
                        thread_lock.release()

                        for f_no in fileno_arr:
                            self.broadcast(f_no)

                        print("complete")
                    except:
                        error_msg = "ERROR_CODE: 1\nERROR_DESCRIPTION: "+str(sys.exc_info()[0])
                        #print(error_msg)
                        self.client_socket.send(error_msg.encode())



                elif "LEAVE_CHATROOM" in client_message:
                    try:
                        print(client_message)
                        client_msg_to_leave_split = re.findall(r"[\w']+",client_message)
                        chatroom_id_local = client_msg_to_leave_split[1]
                        chatroom_id_local = int(chatroom_id_local)

                        left_chatroom_msg = "LEFT_CHATROOM: "+str(chatroom_id_local)+"\nJOIN_ID: "+str(self.client_id)+"\n"
                        print(left_chatroom_msg)
                        self.client_socket.send(left_chatroom_msg.encode())

                        if len(s_queue.values())>1:
                            msg_to_broadcast = "CHAT: "+str(chatroom_id_local)+"\nCLIENT_NAME: "+self.client_name+"\nMESSAGE: "+self.client_name+" has left this chatroom.\n\n"

                            chatroom_members = self.getChatroomMembers(chatroom_id_local)
                            fileno_arr = []
                            for item in chatroom_members:
                                fileno_arr.append(socket_fileno[(item,chatroom_id_local)])

                            thread_lock.acquire()
                            for key in s_queue.keys():
                                #print(s_queue)
                                if key in fileno_arr:
                                    q = s_queue[key]
                                    q.put(msg_to_broadcast)
                            thread_lock.release()
                            for f_no in fileno_arr:
                                self.broadcast(f_no)

                            self.decrementCountClientChatroom()
                            self.deassignChatroom(chatroom_id_local)
                            self.removeFileno(chatroom_id_local)
                        else:
                            self.decrementCountClientChatroom()
                            self.deassignChatroom(chatroom_id_local)
                            self.removeFileno(chatroom_id_local)
                            thread_lock.acquire()
                            thread_lock.release()
                        self.chatroom_id.remove(chatroom_id_local)

                    except:
                        error_msg = "ERROR_CODE: 1\nERROR_DESCRIPTION: "+str(sys.exc_info()[0])
                        self.client_socket.send(error_msg.encode())


                else:
                    try:
                        if len(client_message)>0:
                            client_msg_to_chat_split = re.findall(r"[\w']+",client_message)

                            if client_msg_to_chat_split[0] == "CHAT":
                                chatroom_id_local = client_msg_to_chat_split[1]
                                chatroom_id_local = int(chatroom_id_local)

                                if chatroom_id_local in self.chatroom_id:
                                    msg_to_chat_split = client_message.split(':')
                                    msg_to_chat = msg_to_chat_split[len(msg_to_chat_split)-1]
                                    print(msg_to_chat)
                                    chat_msg = "CHAT: "+str(chatroom_id_local)+"\nCLIENT_NAME: "+self.client_name+"\nMESSAGE:"+msg_to_chat
                                    if len(s_queue.values())>1:

                                        chatroom_members = self.getChatroomMembers(chatroom_id_local)
                                        print(chatroom_members)
                                        fileno_arr = []
                                        for item in chatroom_members:
                                            fileno_arr.append(socket_fileno[(item,chatroom_id_local)])
                                        thread_lock.acquire()

                                        for key in s_queue.keys():
                                            if key in fileno_arr:
                                                q = s_queue[key]
                                                q.put(chat_msg)
                                        thread_lock.release()
                                        for f_no in fileno_arr:
                                            self.broadcast(f_no)

                                    else:
                                        msg_to_send = chat_msg
                                        self.client_socket.send(msg_to_send.encode())

                                else:
                                    msg_to_send = "CHAT: "+str(chatroom_id_local)+"\nCLIENT_NAME: "+self.client_name+"\n"+self.client_name+" has left this chatroom."
                                    self.client_socket.send(msg_to_send.encode())
                    except:
                        error_msg = "ERROR_CODE: 1\nERROR_DESCRIPTION: "+str(sys.exc_info()[0])
                        #print(error_msg)
                        self.client_socket.send(error_msg.encode())

            except:
                pass

    def getRoomId(self,chatroom_local):
        flag = 0;
        for key in chatroom_dict:
            if key == chatroom_local.lower():
                flag = 1
                break
        if flag == 0:
            chatroom_dict[chatroom_local.lower()] = len(chatroom_dict)+1
        self.chatroom_id.append(chatroom_dict[chatroom_local.lower()])
        chatroom_id_local = chatroom_dict[chatroom_local.lower()]
        return chatroom_id_local

    def getClientId(self):
        flag = 0
        for key in client_dict:
            if key == self.client_name.lower():
                flag = 1
        if flag == 0:
            client_dict[self.client_name.lower()] = len(client_dict)+1
        self.client_id = client_dict[self.client_name.lower()]

    def incrementCountClientChatroom(self):
        flag = 0
        for key in client_chatroom_number:
            if key == self.client_id:
                client_chatroom_number[self.client_id] = client_chatroom_number[self.client_id] + 1
                flag = 1
        if flag == 0:
            client_chatroom_number[self.client_id] = 1
        #print("\ncount: ",client_chatroom_number)

    def decrementCountClientChatroom(self):
        client_chatroom_number[self.client_id] = client_chatroom_number[self.client_id] - 1
        if client_chatroom_number[self.client_id] <= 0:
            del client_chatroom_number[self.client_id]
        #print("\ncount: ",client_chatroom_number)

    def assignChatroom(self,chatroom_id_local):
        flag = 0
        for key in chatroom_details:
            if key == chatroom_id_local:
                chatroom_details[chatroom_id_local].append(self.client_id)
                flag = 1
        if flag == 0:
            chatroom_details[chatroom_id_local] = [self.client_id]
        #print("\nchatroom: ",chatroom_details)

    def deassignChatroom(self,chatroom_id_local):
        chatroom_details[chatroom_id_local].remove(self.client_id)
        if len(chatroom_details[chatroom_id_local]) == 0:
            del chatroom_details[chatroom_id_local]
        #print("\nchatroom: ",chatroom_details)

    def getChatroomMembers(self,chatroom_id_local):
        #print(chatroom_details)
        return chatroom_details[chatroom_id_local]

    def setFileno(self,chatroom_id_local):
        socket_fileno[(self.client_id,chatroom_id_local)] = self.client_socket.fileno()

    def removeFileno(self,chatroom_id_local):
        del socket_fileno[(self.client_id,chatroom_id_local)]

    def broadcast(self,f_no):
        for sock in socket_connections:
            if sock.fileno()==f_no:
                try:
                    msg = s_queue[sock.fileno()].get(False)
                    print(msg)
                    sock.send(msg.encode())
                except queue.Empty:
                    pass

chatroom_dict = {}
client_dict = {}
chatroom_details = {}
client_chatroom_number = {}
socket_fileno = {}
socket_connections = []


thread_lock = threading.Lock()
s_queue = {}
#Creating a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
if len(sys.argv) != 2:
    print("Please provide port number")
    exit()
host = socket.gethostbyname(socket.gethostname())
port = int(sys.argv[1])

server_socket.bind(('',port))
server_socket.listen(5)


while True:
    print("Server is ready and listening...")
    try:
        (client_socket,(client_ip,client_port)) = server_socket.accept()
        socket_connections.append(client_socket)
    except (OSError):
        sys.exit()
    q = queue.Queue()
    thread_lock.acquire()

    s_queue[client_socket.fileno()] = q
    thread_lock.release()

    client_thread = client(client_socket,client_ip,client_port)
    client_thread.daemon = True
    client_thread.start()
