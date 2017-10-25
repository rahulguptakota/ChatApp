#!/usr/bin/python
import socket, pickle, threading
import os.path
import time

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

while True:
	print("nListening for incoming connections...")
	(clientsock, (ip, port)) = s.accept()
	with open('users.txt') as f:
		credentials = [x.strip().split(':') for x in f.readlines()]
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