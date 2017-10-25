#!/usr/bin/python
import socket, pickle
import os.path

s = socket.socket()
host = socket.gethostname()
port = 9000
s.bind((host, port))

s.listen(5)

with open('users.txt') as f:
	credentials = [x.strip().split(':') for x in f.readlines()]

while True:
	c, addr = s.accept()
	data = c.recv(1024)
	[username,password] = pickle.loads(data)
	if [username,password] in credentials:
		c.send("Hello " + username)
	else:
		c.send("Authentication Failure!!!")
		c.close()
		continue
	filename = c.recv(1024)
	if os.path.isfile(filename):
		file_size = str(os.stat(filename).st_size)
		c.send(file_size)
		f = open(filename,"rb")
		line = f.read(1024)
		while(line):
			print("sending...")
			c.send(line)
			line = f.read(1024)
		f.close()
	else:
		c.send("File Not Found.")
	c.close

