#!/usr/bin/python
import socket, pickle, threading
import os.path
import time
import select
from queue import Queue
import os
from Crypto.PublicKey import RSA

logged_in_users = {}
logged_in_users_pub = {}
message_queues = {}
with open('users.txt') as f:
	credentials = [x.strip().split(':') for x in f.readlines()]
	f.close()

with open('publickeys.txt') as f:
	publickey = RSA.importKey(f.read())
	f.close()

with open('privatekey.txt') as f:
	privatekey = RSA.importKey(f.read())
	f.close()

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
		print("Connection from : "+ip+":"+str(port))
		self.clientsocket.send(publickey.exportKey())	
		data = self.clientsocket.recv(1024)
		[username,password,clientpublickey] = pickle.loads(data)
		username = privatekey.decrypt(username).decode()
		password =privatekey.decrypt(password).decode()
		message_queues[username] = Queue()
		print(username,password,clientpublickey,credentials)
		if [username,password] in credentials:
			print("Authentication sucessfull")			
			if username in logged_in_users:				
				print(username," already logged in.")
				self.clientsocket.close()
				exit()
			else:
				self.username = username
				logged_in_users[self.username] = [self.clientsocket, time.time(),[]]
				logged_in_users_pub[self.username] = clientpublickey
		else:
			print("Authentication unsuccessfull")
			self.clientsocket.send(("Authentication Failure!!!").encode())
			self.clientsocket.close()
			exit()

		self.clientsocket.send(pickle.dumps(logged_in_users_pub))
		# self.clientsocket.setblocking(0)
		while(True):
			readable, writable, exceptional = select.select([self.clientsocket],logged_in_users[self.username][-1],[self.clientsocket],0.1)
			print([self.clientsocket],logged_in_users[self.username][-1],[self.clientsocket])
			print(readable,writable,exceptional)
			print("logged in user list for {} is {}".format(self.username,logged_in_users[self.username][-1]))
			for r in readable:
				print("something")
				try:
					data = r.recv(1024)
					print(data)		
					data = pickle.load(data)									
					for user in data[0]:
						print("Send {} to {} from {}".format(data[1],user,self.username))
						message_queues[user].put(data[1])
						if logged_in_users[user][0] not in logged_in_users[user][-1]:
							logged_in_users[user][-1].append(logged_in_users[user][0])
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

while True:
	print("nListening for incoming connections...")
	print(publickey.exportKey())
	print(privatekey.exportKey())
	(clientsock, (ip, port)) = s.accept()
	inputs.append(clientsock)
	outputs.append(clientsock)
	newthread = ClientThread(ip, port,clientsock)
	newthread.start()