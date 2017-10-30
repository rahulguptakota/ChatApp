import tkinter as tk
from tkinter import messagebox
import socket, pickle, time, threading, select
from Crypto.PublicKey import RSA
import sys

s = socket.socket()
host = '192.168.0.106'
port = 8000
s.connect((host, port))
cnt = 0
flag = 0
close = 0
publickeys = {}

objectdict = {}

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

        self.master.bind('<Return>', self.new_window)
        self.button_1 = tk.Button(top_frame, text = "Login", fg = "yellow", bg = "black", command = self.new_window)
        # button_1.bind("<Button-1>", Printname)
        self.button_2 = tk.Button(top_frame, text = "Reset")
        self.button_1.pack(side = tk.LEFT)
        self.button_2.pack(side = tk.LEFT)
        self.frame.pack()

    def new_window(self, event=None):
        # self.newWindow = tk.Toplevel(self.master)
        username = self.entry1.get()
        password = self.entry2.get()
        print(username,password)
        global s        
        global selfpublickey
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
            objectdict["whoelse"] = OnlinePeople(self.master, data[1])

        # self.frame.destroy()
        # self.app = OnlinePeople(self.master)

class OnlinePeople:
    def __init__(self, master,data={}):
        self.master = master
        self.newWindow = {}
        self.data = data
        global publickeys
        publickeys = data
        # self.parent = parent
        self.frame = tk.Frame(self.master)
        self.Lb1 = tk.Listbox(self.frame)
        i=0
        for key in self.data:
            self.Lb1.insert(i, key)
            i = i + 1

        self.Lb1.pack()
        self.chat = tk.Button(self.frame, text = 'Chat', width = 25, command = self.start_chat)
        self.chat.pack()
        self.whoelse = tk.Button(self.frame, text = 'Whoelse', width = 25, command = self.liveusers)
        self.whoelse.pack()
        self.frame.pack()
        global flag 
        flag = 1

    def liveusers(self):
        global s
        s.send("Live users list".encode())
        # self.data = pickle.loads(s.recv(1024))
        # cs=self.Lb1.curselection()
        # self.Lb1.delete(0,tk.END)
        # i=0
        # for key in self.data:
        #     self.Lb1.insert(i, key)
        #     i = i + 1
        # print(self.data) 

    def update_list(self, data):
        cs=self.Lb1.curselection()
        self.Lb1.delete(0,tk.END)
        i=0
        print("in update_list ", data)
        self.data = data
        global publickeys
        publickeys = data
        for key in data:
            self.Lb1.insert(i, key)
            i = i + 1

    def start_chat(self):
        users = list(self.data.keys())
        # print(self.Lb1.curselection()[0])
        user = users[self.Lb1.curselection()[0]]

        if(user in self.newWindow):
            # self.app = Chatbox(self.newWindow[num])
            print(self.newWindow[user].winfo_exists())
            if(not self.newWindow[user].winfo_exists()):
                self.newWindow[user] = tk.Toplevel(self.master)
                self.app = Chatbox(self.newWindow[user])
            # print ("Hallelujah")
        else:
            self.newWindow[user] = tk.Toplevel(self.master)
            objectdict[user] = Chatbox(self.newWindow[user], user, self.data[user])
        # print(self.Lb1.curselection())
        # self.frame.destroy()
        # self.app = Chatbox(self.newWindow)

        print (self.newWindow)
        
        print (user)
        # self.frame.destroy()                
        

class Chatbox:
    def __init__(self, master, otheruser, publickey):
        self.master = master
        self.otheruser = otheruser
        self.publickey = RSA.importKey(publickey.decode())
        # self.parent = parent
        self.frame = tk.Frame(self.master)
        self.chatLog = tk.Text(self.frame, bd=0, bg="white", height="8", width="50")
        self.chatLog.insert(tk.END, "Connecting to your partner..\n")
        self.chatLog.insert(tk.END, "Some more data\n")             
        #Bind a scrollbar to the Chat window
        scrollbar = tk.Scrollbar(self.frame, command=self.chatLog.yview, cursor="heart")
        self.chatLog['yscrollcommand'] = scrollbar.set
        self.chatLog.grid(row=0, columnspan = 2)
        self.entry1 = tk.Entry(self.frame)
        self.entry1.grid(row=1, columnspan = 2, sticky="news")

        #Create the Button to send message
        SendButton = tk.Button(self.frame, text="Send",
                            bd=0, bg="#FFBF00", activebackground="#FACC2E",
                            command=self.send_chat)        
        SendButton.grid(row=2, column=0, sticky="news")
        self.quit = tk.Button(self.frame, text = 'Quit', command = self.quit_chat)
        self.quit.grid(row=2, column=1, sticky="news")
        self.frame.pack()

    def send_chat(self):
        data = []
        data.append([])
        print(self.otheruser)
        data[0].append(self.otheruser)
        data.append(self.publickey.encrypt(self.entry1.get().encode('utf-8'), 16))
        data = pickle.dumps(data)
        s.send(data)
    
    def append_chat(self, data):
        print("hello in append_chat ", data)
        self.chatLog.insert(tk.END, data.decode())

    def quit_chat(self):
        self.master.destroy()


class myThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def on_closing(self):
        global close
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            close = 1
            self.root.destroy()
            exit()

    def run(self):
        self.root = tk.Tk()        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        Login(self.root)
        self.root.mainloop()


def main(): 
    tkThread = myThread()
    global s
    global selfprivatekey
    while(True):
        if(flag == 1):
            readable, writable, exceptional = select.select([s],[],[])
            for r in readable:
                data = pickle.loads(r.recv(1024))
                print("this is data\n", data)
                if data[0] == "Live users list":
                    objectdict["whoelse"].update_list(data[1])
                else:
                    decrypted_data = selfprivatekey.decrypt(data[1])
                    try:                        
                        objectdict[data[0]].append_chat(decrypted_data)
                    except KeyError:
                        objectdict["whoelse"].newWindow[data[0]] = tk.Toplevel(objectdict["whoelse"].master)
                        print(data[0])
                        objectdict[data[0]] = Chatbox(objectdict["whoelse"].newWindow[data[0]], data[0], publickeys[data[0]])
                        objectdict[data[0]].append_chat(decrypted_data)
        elif(close):
            exit()
    # root = tk.Tk()
    # app = Login(root)
    # root.mainloop()




if __name__ == '__main__':
    main()