#!/usr/bin/python
import socket, pickle, threading
import os.path
import time
import select
from queue import Queue
import os
from Crypto.PublicKey import RSA
import json

logged_in_users = {}
logged_in_users_pub = {}
users_pub = {}
message_queues = {}
recently_connected = {}
credentials = {}
blocked = {}

with open('publickeys.txt') as f:
    publickey = RSA.importKey(f.read())
    f.close()

privatekey = ""
with open('privatekey.txt') as f:
    privatekey = RSA.importKey(f.read())
    f.close()

with open('users.txt','r') as f:
    credentials = json.load(f)
    f.close()
    print(credentials)

for user in credentials.keys():
    users_pub[user] = credentials[user]["pubkey"]
    blocked[user] = []
    message_queues[user] = Queue()

class ClientThread(threading.Thread):

    def __init__(self,ip,port,clientsocket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.username = ""
        self.clientsocket = clientsocket
        print("[+] New thread started for "+ip+":"+str(port)+" this is socket: ")

    def run(self):
        global message_queues
        global logged_in_users
        global users_pub
        global credentials
        global blocked         
        # for [u,p,c] in credentials:
        #     users_pub[u] = c        
        print("Connection from : "+ip+":"+str(port))
        self.clientsocket.send(publickey.exportKey())	
        data = self.clientsocket.recv(1024)
        data = pickle.loads(data)
        print(data)
        signup = data["signup"]
        username = data["username"]
        password = data["password"]
        clientpublickey = data["pubkey"]
        if signup == 1:
            if username in credentials.keys():
                self.clientsocket.send("User already registered.".encode())
            else:
                with open("users.txt", "w") as myfile:
                    print(username,password)
                    del data["signup"]
                    credentials[username] = data
                    users_pub[user] = credentials[user]["pubkey"]
                    json.dump(credentials,myfile)
                    myfile.close()
                self.clientsocket.send("Successfully signed up".encode())
                blocked[username] = []
                message_queues[username] = Queue()
            self.clientsocket.close()
            exit()
        username = privatekey.decrypt(username).decode()
        password =privatekey.decrypt(password).decode()
        # print(username,password,clientpublickey,credentials)
        if username == credentials[username]["username"] and password == credentials[username]["password"]:
            print("Authentication sucessfull")			
            if username in logged_in_users:				
                print(username," already logged in.")
                self.clientsocket.close()
                exit()
            else:
                print("hurray!! new login")
                self.username = username
                logged_in_users[self.username] = [self.clientsocket,[]]
                logged_in_users_pub[self.username] = clientpublickey
                recently_connected[self.username] = time.time()
                if not message_queues[self.username].empty():
                    print("yes! i have got messages")
                    if logged_in_users[self.username][0] not in logged_in_users[self.username][-1]:
                        print("yeah, i am adding socket to writable")
                        logged_in_users[self.username][-1].append(logged_in_users[self.username][0])
        else:
            print("Authentication unsuccessfull")
            self.clientsocket.send(("Authentication Failure!!!").encode())
            self.clientsocket.close()
            exit()
        data = []
        data.append("Live users list")
        data.append(logged_in_users_pub)
        self.clientsocket.send(pickle.dumps(data))
        # self.clientsocket.setblocking(0)
        while(True):
            readable, writable, exceptional = select.select([self.clientsocket],logged_in_users[self.username][-1],[self.clientsocket],0.5)
            # print([self.clientsocket],logged_in_users[self.username][-1],[self.clientsocket])
            # print(readable,writable,exceptional)
            # print("logged in user list for {} is {}".format(self.username,logged_in_users[self.username][-1]))
            for r in readable:
                # try:
                data = r.recv(1024)
                print(data)
                print("Hey")
                # print(data.decode().split(' ')[0])
                if data == "Live users list".encode():
                    data = []
                    data.append("Live users list")
                    data.append(logged_in_users_pub)
                    self.clientsocket.send(pickle.dumps(data))
                elif data == "Live 1Hr users list".encode():
                    for item in recently_connected.keys():
                        if(time.time() - recently_connected[item] > 3600):
                            del recently_connected[item]
                    data = []
                    data.append("Live 1Hr users list")
                    print(recently_connected)
                    data.append(recently_connected)
                    self.clientsocket.send(pickle.dumps(data))
                elif data == "All users list".encode():
                    data = []
                    data.append("All users list")
                    data.append(users_pub)
                    print("in all users list ", users_pub)
                    self.clientsocket.send(pickle.dumps(data))
                elif "Block".encode() in data:
                    print("Heyyyyyyyyy", data.decode().split(' ')[1] , data.decode())
                    if(data.decode().split(' ')[1] not in blocked[self.username]):
                        blocked[self.username].append(data.decode().split(' ')[1])
                elif "Unblock".encode() in data:
                    if(data.decode().split(' ')[1] in blocked[self.username]):
                        blocked[self.username].remove(data.decode().split(' ')[1])
                elif data == "logout".encode():
                    self.clientsocket.close()
                    exit()
                else:
                    # try:
                    data =  pickle.loads(data)
                    print(data)
                    # global privatekey
                    # print(privatekey.decrypt(data[1]))
                    for user in data.keys():
                        print("Sending {} to {} from {}".format(data[user],user,self.username))
                        message = []
                        message.append(self.username)
                        message.append(data[user])
                        if self.username not in blocked[user]:
                            message_queues[user].put(message)                        
                        else:
                            message = []
                            message.append("Blocked")
                            message_queues[self.username].put(message)
                            print("in blocked for user: ", user, " ")
                            if logged_in_users[self.username][0] not in logged_in_users[self.username][-1]:
                                logged_in_users[self.username][-1].append(logged_in_users[self.username][0])
                        if user not in logged_in_users :
                            pass
                        elif logged_in_users[user][0] not in logged_in_users[user][-1]:
                            logged_in_users[user][-1].append(logged_in_users[user][0])
                    # except:
                    #     print("Clossing connection for {}".format(self.username))
                    #     self.clientsocket.close()
                    #     del logged_in_users[self.username]
                    #     del logged_in_users_pub[self.username]
                    #     exit()
            for s in writable:
                temp = 1
                while temp:
                    try:
                        print(self.username)
                        # print(message_queues[self.username].get())
                        next_msg = message_queues[self.username].get()
                        print("in queue: ", next_msg)
                        s.send(pickle.dumps(next_msg))
                    except Queue.Empty :
                        print("time to remove ", self.username)
                        if s in logged_in_users[self.username][-1]:
                            print("in if")
                            logged_in_users[self.username][-1].remove(s)
                        print("There is no message to send")
                        temp = 0

s = socket.socket()
host = '0.0.0.0'
port = 8000
s.bind((host, port))
s.listen(5)
# Sockets from which we expect to read
inputs = [ ]
# Sockets to which we expect to write
outputs = [ ]
# Outgoing message queues (socket:Queue)

while True:
    print("nListening for incoming connections...")
    # print(publickey.exportKey())
    # print(privatekey.exportKey())
    (clientsock, (ip, port)) = s.accept()
    inputs.append(clientsock)
    outputs.append(clientsock)
    newthread = ClientThread(ip, port,clientsock)
    newthread.start()