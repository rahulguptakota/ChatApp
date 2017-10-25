#!/usr/bin/python

import socket, pickle
import getpass

s = socket.socket()
host = ''
port = 9000

s.connect((host, port))
username = input("Please enter your username: ")
password = getpass.getpass("Please enter your password: ")
s.send(pickle.dumps([username,password]))
data = s.recv(1024)
print(data)
if "Authentication Failure!!!" in data:
	s.close 
	exit()
filename = raw_input("Please enter the name of file you want to retrive: ")
s.send(filename)
ack = s.recv(1024)
if "File Not Found" in ack:
	print(ack)
	s.close
	exit()
file_size = int(ack)
f = open("filename","wb")
while file_size > 0:
	print("Receiving...")
	line = s.recv(1024)
	f.write(line)
	file_size = file_size - len(line)
f.close()
s.close
