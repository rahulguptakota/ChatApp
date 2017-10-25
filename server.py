#!/usr/bin/python
import socket, pickle, threading
import os.path

class ClientThread(threading.Thread):

	def __init__(self,ip,port,clientsocket):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.csocket = clientsocket
		print("[+] New thread started for "+ip+":"+str(port))

	def run(self):    
		print("Connection from : "+ip+":"+str(port))
		with open('users.txt') as f:
			credentials = [x.strip().split(':') for x in f.readlines()]
		data = self.csocket.recv(1024)
		[username,password] = pickle.loads(data)
		print(username,password,credentials)
		if [username,password] in credentials:
			print("Authentication sucessfull")
			self.csocket.send(("Hello " + username).encode())
		else:
			print("Authentication unsuccessfull")
			self.csocket.send(("Authentication Failure!!!").encode())
		self.csocket.close()

s = socket.socket()
host = '127.0.0.1'
port = 9000
s.bind((host, port))
s.listen(5)

while True:
	print("nListening for incoming connections...")
	(clientsock, (ip, port)) = s.accept()
	newthread = ClientThread(ip, port, clientsock)
	newthread.start()