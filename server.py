#!/usr/bin/python
import socket, pickle, threading
import os.path
import time
import select
from queue import Queue

logged_in_users = {}
message_queues = {}

class ClientThread(threading.Thread):

	def __init__(self,ip,port,username,clientsocket):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.username = username
		self.clientsocket = clientsocket
		print("[+] New thread started for "+ip+":"+str(port)+" this is socket: ")

	def run(self):
		global message_queues
		global logged_in_users    
		print("Connection from : "+ip+":"+str(port))	
		self.clientsocket.send(("Hello user").encode())
		while(True):
			readable, writable, exceptional = select.select([self.clientsocket],logged_in_users[self.username][-1],[self.clientsocket],0.1)
			print("logged in user list for {} is {}".format(self.username,logged_in_users[self.username][-1]))
			for r in readable:
				print("something")
				try:
					data = pickle.loads(r.recv(1024))
					if data:
						for user in data[0]:
							print("Send {} to {} from {}".format(data[1],user,self.username))
							message_queues[user].put(data[1])
							if logged_in_users[user][-2] not in logged_in_users[user][-1]:
								logged_in_users[user][-1].append(logged_in_users[user][-2])
					else:
						print("No data is send by the user")
				except:
					print("Clossing connection for {}".format(self.username))
					self.clientsocket.close()
					del logged_in_users[self.username]
					exit()
			for s in writable:
				temp = 1
				while temp:
					try:
						print(self.username);
						next_msg = message_queues[self.username].get_nowait()
						s.send(next_msg.encode())
					except:
						print("time to remove ", self.username)
						if s in logged_in_users[self.username][-1]:
							print("in if")
							logged_in_users[self.username][-1].remove(s)
						print("There is no message to send")
						temp = 0
				

s = socket.socket()
host = '127.0.0.1'
port = 8000
s.bind((host, port))
s.listen(5)
# Sockets from which we expect to read
inputs = [ ]
# Sockets to which we expect to write
outputs = [ ]
# Outgoing message queues (socket:Queue)
with open('users.txt') as f:
		credentials = [x.strip().split(':') for x in f.readlines()]

while True:
	print("nListening for incoming connections...")
	(clientsock, (ip, port)) = s.accept()
	clientsock.setblocking(0)
	inputs.append(clientsock)
	outputs.append(clientsock)	
	data = clientsock.recv(1024)
	[username,password] = pickle.loads(data)
	message_queues[username] = Queue()
	print(username,password,credentials)
	if [username,password] in credentials:
		print("Authentication sucessfull")			
		if username in logged_in_users:				
			print(username," already logged in.")
			clientsock.close()
			continue
		logged_in_users[username] = [clientsock, time.time(),clientsock,[]]
		newthread = ClientThread(ip, port, username,clientsock)
		newthread.start()
	else:
		print("Authentication unsuccessfull")
		clientsock.send(("Authentication Failure!!!").encode())
		clientsock.close()