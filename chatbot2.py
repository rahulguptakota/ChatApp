import tkinter as tk
from tkinter import messagebox
import socket, pickle, time
from Crypto.PublicKey import RSA

s = socket.socket()
host = '127.0.0.1'
port = 6000
cnt = 0

with open('publickeys.txt') as f:
	selfpublickey = RSA.importKey(f.read())
	f.close()

with open('privatekey.txt') as f:
	selfprivatekey = RSA.importKey(f.read())
	f.close()

def raise_frame(frame):
    frame.tkraise()

class Login:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)

        name = tk.Label(self.frame, text = "name")
        password = tk.Label(self.frame, text = "password")
        name.grid(row=0, sticky = tk.E)
        password.grid(row=1, sticky = tk.E)
        self.entry1 = tk.Entry(self.frame)
        self.entry2 = tk.Entry(self.frame, show="*")
        self.entry1.grid(row=0, column=1)
        self.entry2.grid(row=1, column=1)
        self.c = tk.Checkbutton(self.frame, text = "keep me logged in")
        self.c.grid(row=2, columnspan=2)
        # self.button1 = tk.Button(self.frame, text = 'New Window', width = 25, command = self.new_window)
        # self.button1.grid(row=3, sticky = tk.E)
        top_frame = tk.Frame(self.frame)
        top_frame.grid(row=3, columnspan=2)

        self.master.bind('<Return>', self.new_window2)
        self.button_1 = tk.Button(top_frame, text = "Login", fg = "yellow", bg = "black", command = self.new_window)
        # button_1.bind("<Button-1>", Printname)
        self.button_2 = tk.Button(top_frame, text = "Reset")
        self.button_1.pack(side = tk.LEFT)
        self.button_2.pack(side = tk.LEFT)
        self.frame.pack()

    def new_window2(self , event):
        # self.newWindow = tk.Toplevel(self.master)
        username = self.entry1.get()
        password = self.entry2.get()
        print(username,password)
        # s = socket.socket()
        # s.connect((host, port))
        # s.send(pickle.dumps([username,password]))
        # data = s.recv(1024)
        # data = "Authentication Failure!!!".encode()
        data = "success".encode()
        print(data)
        if ("Authentication Failure!!!").encode() in data:
            global cnt
            cnt = cnt + 1
            if(cnt%3 == 0):
                self.button_1.config(state = tk.DISABLED)
                messagebox.showinfo("3 wrong attempts","You have been locked for 10s")
                time.sleep(10)
                self.button_1.config(state = tk.NORMAL)
            s.close()
        else:
            self.frame.destroy()
            self.app = OnlinePeople(self.master)

        # self.frame.destroy()
        # self.app = OnlinePeople(self.master)

    def new_window(self):
        # self.newWindow = tk.Toplevel(self.master)
        username = self.entry1.get()
        password = self.entry2.get()
        print(username,password)
        s = socket.socket()
        s.connect((host, port))
        publickey = s.recv(1024)
        print(publickey)
        publickey = RSA.importKey(publickey.decode())
        username = publickey.encrypt(username.encode('utf-8'),16) #encrypt message with public key
        # print(str(username))
        password = publickey.encrypt(password.encode('utf-8'),16) #encrypt message with public key
        s.send(pickle.dumps([username,password,selfpublickey.exportKey()]))
        data = s.recv(1024)
        # data = "Authentication Failure!!!".encode()
        # data = "success".encode()
        print(data)
        if ("Authentication Failure!!!").encode() in data:
        	global cnt
        	cnt = cnt + 1
        	if(cnt%3 == 0):
        		self.button_1.config(state = tk.DISABLED)
        		messagebox.showinfo("3 wrong attempts","You have been locked for 10s")
        		time.sleep(10)
        		self.button_1.config(state = tk.NORMAL)
        	s.close()
        else:
            data = pickle.loads(data)
            print(data)
            self.frame.destroy()
            self.app = OnlinePeople(self.master)

        # self.frame.destroy()
        # self.app = OnlinePeople(self.master)

class OnlinePeople:
    def __init__(self, master):
        self.master = master
        # self.parent = parent
        self.frame = tk.Frame(self.master)
        self.Lb1 = tk.Listbox(self.frame)
        self.Lb1.insert(1, "Python")
        self.Lb1.insert(2, "Perl")
        self.Lb1.insert(3, "C")
        self.Lb1.insert(4, "PHP")
        self.Lb1.insert(5, "JSP")
        self.Lb1.insert(6, "Ruby")

        self.Lb1.pack()
        self.chat = tk.Button(self.frame, text = 'Chat', width = 25, command = self.start_chat)
        self.chat.pack()
        self.frame.pack()

    def start_chat(self):
        self.newWindow = tk.Toplevel(self.master)
        print(self.Lb1.curselection())
        # self.frame.destroy()
        self.app = Chatbox(self.newWindow)

class Chatbox:
    def __init__(self, master):
        self.master = master
        # self.parent = parent
        self.frame = tk.Frame(self.master)
        ChatLog = tk.Text(self.frame, bd=0, bg="white", height="8", width="50")
        ChatLog.insert(tk.END, "Connecting to your partner..\n")
        ChatLog.config(state=tk.DISABLED)

        #Bind a scrollbar to the Chat window
        scrollbar = tk.Scrollbar(self.frame, command=ChatLog.yview, cursor="heart")
        ChatLog['yscrollcommand'] = scrollbar.set
        ChatLog.grid(row=0, columnspan = 2)
        #Create the Button to send message
        SendButton = tk.Button(self.frame, text="Send",
                            bd=0, bg="#FFBF00", activebackground="#FACC2E",
                            command=self.start_chat)        
        SendButton.grid(row=1, column=0, sticky="news")
        self.quit = tk.Button(self.frame, text = 'Quit', command = self.quit_chat)
        self.quit.grid(row=1, column=1, sticky="news")
        self.frame.pack()

    def start_chat(self):
        pass
    
    def quit_chat(self):
        self.master.destroy()
        

def main(): 
    root = tk.Tk()
    app = Login(root)
    root.mainloop()

if __name__ == '__main__':
    main()