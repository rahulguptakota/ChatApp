#!/usr/bin/python
import socket, pickle
import os.path

logged_in_users = set()

def main():
	s = socket.socket()
	host = '127.0.0.1'
	port = 9000
	s.bind((host, port))

	s.listen(5)
	with open('users.txt') as f:
		credentials = [x.strip().split(':') for x in f.readlines()]

	while True:
		c, addr = s.accept()
		data = c.recv(1024)
		[username,password] = pickle.loads(data)
		print(username,password,credentials)
		if [username,password] in credentials:
			print("Authentication sucessfull")
			logged_in_users.add(username)
			if username in logged_in_users:
				print("true")
			c.send(("Hello " + username).encode())
			c.close()
		else:
			c.send(("Authentication Failure!!!").encode())
			c.close()
			continue
	# 	filename = c.recv(1024)
	# 	if os.path.isfile(filename):
	# 		file_size = str(os.stat(filename).st_size)
	# 		c.send(file_size)
	# 		f = open(filename,"rb")
	# 		line = f.read(1024)
	# 		while(line):
	# 			print("sending...")
	# 			c.send(line)
	# 			line = f.read(1024)
	# 		f.close()
	# 	else:
	# 		c.send("File Not Found.")
	# 	c.close

if __name__ == '__main__':
    main()