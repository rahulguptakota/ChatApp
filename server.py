#!/usr/bin/python
import socket, pickle, threading
import os.path
import time
import select

logged_in_users = {}

class ClientThread(threading.Thread):

	def __init__(self,ip,port,clientsocket):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.csocket = clientsocket
		print("[+] New thread started for "+ip+":"+str(port)+" this is socket: ")

	def run(self):    
		print("Connection from : "+ip+":"+str(port))	
		self.csocket.send(("Hello user").encode())	
		newdata = self.csocket.recv(1024)	
		print(newdata)
		# self.csocket.close()

s = socket.socket()
host = '127.0.0.1'
port = 9000
s.bind((host, port))
s.listen(5)
# Sockets from which we expect to read
inputs = [ ]
# Sockets to which we expect to write
outputs = [ ]
# Outgoing message queues (socket:Queue)
message_queues = {}
with open('users.txt') as f:
		credentials = [x.strip().split(':') for x in f.readlines()]

while True:
	print("nListening for incoming connections...")
	readable, writable, exceptional = select.select(inputs, outputs, inputs)
	(clientsock, (ip, port)) = s.accept()
	clientsock.setblocking(0)
    inputs.append(clientsock)
	outputs.append(clientsock)
    message_queues[connection] = Queue.Queue()
	data = clientsock.recv(1024)
	[username,password] = pickle.loads(data)
	print(username,password,credentials)
	if [username,password] in credentials:
		print("Authentication sucessfull")			
		if username in logged_in_users:				
			print(username," already logged in.")
			clientsock.close()
		logged_in_users[username] = [clientsock, time.time()]
	else:
		print("Authentication unsuccessfull")
		clientsock.send(("Authentication Failure!!!").encode())
		clientsock.close()
	newthread = ClientThread(ip, port, clientsock)
	newthread.start()