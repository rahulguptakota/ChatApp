import tkinter as tk
from tkinter import messagebox
import socket, pickle, time, threading, select
from Crypto.PublicKey import RSA
import sys

s = ""
host = '127.0.0.1'
port = int(sys.argv[1])
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
        top_frame = tk.Frame(self.frame)
        top_frame.grid(row=3, columnspan=2)
        self.master.bind('<Return>', self.new_window)
        self.button_1 = tk.Button(top_frame, text = "Login", fg = "yellow", bg = "black", command = self.new_window)
        self.button_2 = tk.Button(top_frame, text = "Sign Up", command = self.sign_up)
        self.button_1.pack(side = tk.LEFT)
        self.button_2.pack(side = tk.LEFT)
        self.frame.pack()

    def sign_up(self, event=None):
        self.frame.destroy()                       
        objectdict["signup"] = SignUp(self.master)

    def new_window(self, event=None):
        username = self.entry1.get()
        password = self.entry2.get()
        global s        
        global selfpublickey
        s = socket.socket()
        s.connect((host, port))
        publickey = s.recv(1024)
        publickey = RSA.importKey(publickey.decode())
        username = publickey.encrypt(username.encode('utf-8'),16) #encrypt message with public key
        password = publickey.encrypt(password.encode('utf-8'),16) #encrypt message with public key
        data = {}
        data["username"] = username
        data["password"] = password
        data["pubkey"] = selfpublickey.exportKey().decode()
        data["signup"] = 0
        s.send(pickle.dumps(data))
        data = s.recv(1024)
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
            self.frame.destroy()                       
            objectdict["whoelse"] = OnlinePeople(self.master, data[1])
            myThread1()

class SignUp:
    def __init__(self, master,data={}):
        self.master = master
        self.frame = tk.Frame(self.master)
        name = tk.Label(self.frame, text = "Name")
        password = tk.Label(self.frame, text = "Password")
        confirmpassword = tk.Label(self.frame, text = "Confirm Password")
        name.grid(row=0, sticky = tk.E)
        password.grid(row=1, sticky = tk.E)
        confirmpassword.grid(row=2, sticky = tk.E)
        self.entry1 = tk.Entry(self.frame)
        self.entry2 = tk.Entry(self.frame, show="*")
        self.entry3 = tk.Entry(self.frame, show="*")
        self.entry1.grid(row=0, column=1)
        self.entry2.grid(row=1, column=1)
        self.entry3.grid(row=2, column=1)
        top_frame = tk.Frame(self.frame)
        top_frame.grid(row=3, columnspan=2)
        self.master.bind('<Return>', self.submit)
        self.button_1 = tk.Button(top_frame, text = "Back to Login", fg = "yellow", bg = "black", command = self.to_login)
        self.button_2 = tk.Button(top_frame, text = "Submit And Login", command = self.submit)
        self.button_1.pack(side = tk.LEFT)
        self.button_2.pack(side = tk.LEFT)
        self.frame.pack()

    def to_login(self):
        self.frame.destroy()
        Login(self.master)

    def submit(self):
        s = socket.socket()
        s.connect((host, port))
        username = self.entry1.get()
        password = self.entry2.get()
        if(password != self.entry3.get()):
            messagebox.showinfo("Password Entered Incorrectly","Passwords don't match")
        else:
            data = {}
            data["username"] = username
            data["password"] = password
            data["pubkey"] = selfpublickey.exportKey().decode()
            data["signup"] = 1
            s.send(pickle.dumps(data))
            data = s.recv(1024)
            if "Successfully signed up".encode() in data:
                messagebox.showinfo("Sign Up","Congrats! You are signed up.")
                self.to_login()
            elif "User already registered.".encode() in data:
                messagebox.showinfo("Sign Up","User already registered.")
            else:
                messagebox.showinfo("Sign Up","Failed. Try again.")
        s.close()

class OnlinePeople:
    def __init__(self, master,data={}):
        self.master = master
        self.newWindow = {}
        self.data = data
        self.allusers1 = []
        global publickeys
        publickeys = data
        self.frame = tk.Frame(self.master)
        self.Lb1 = tk.Listbox(self.frame)
        i=0
        for key in self.data:
            self.Lb1.insert(i, key)
            i = i + 1

        self.Lb1.pack()
        self.chat = tk.Button(self.frame, text = 'Chat', width = 25, command = self.start_chat)
        self.chat.pack()
        self.Allusers = tk.Button(self.frame, text = 'Alluser', width = 25, command = self.allusers)
        self.Allusers.pack()
        self.whoelse = tk.Button(self.frame, text = 'Whoelse', width = 25, command = self.liveusers)
        self.whoelse.pack()
        self.wholasthr = tk.Button(self.frame, text = 'Wholasthr', width = 25, command = self.lasthourusers)
        self.wholasthr.pack()
        self.broadcast = tk.Button(self.frame, text = 'Broadcast', width = 25, command = self.messageall)
        self.broadcast.pack()
        self.logout = tk.Button(self.frame, text = 'logout', width = 25, command = self.Logout)
        self.logout.pack()
        self.block = tk.Button(self.frame, text = 'block', width = 25, command = self.block_someone)
        self.block.pack()
        self.unblock = tk.Button(self.frame, text = 'Unblock', width = 25, command = self.unblock_someone)
        self.unblock.pack()
        self.asyncchat = tk.Button(self.frame, text = 'Asyncchat', width = 25, command = self.start_asyncchat)
        self.asyncchat.pack()
        self.frame.pack()
        global flag 
        flag = 1

    def block_someone(self):
        global s
        users = list(self.allusers1.keys())
        user = users[self.Lb1.curselection()[0]]
        s.send(("Block " + user).encode())

    def unblock_someone(self):
        global s
        users = list(self.allusers1.keys())
        user = users[self.Lb1.curselection()[0]]
        s.send(("Unblock " + user).encode())

    def lasthourusers(self):
        global s
        s.send("Live 1Hr users list".encode())

    def messageall(self):
        global s
        otherusers = list(self.data.keys())
        user="Broadcast"
        if(user in self.newWindow):
            if(not self.newWindow[user].winfo_exists()):
                self.newWindow[user] = tk.Toplevel(self.master)
                objectdict[user] = Chatbox(self.newWindow[user], otherusers)
        else:
            self.newWindow[user] = tk.Toplevel(self.master)
            objectdict[user] = Chatbox(self.newWindow[user], otherusers)

    def liveusers(self):
        print("live users list is called : ")
        global s
        s.send("Live users list".encode())
 
    def allusers(self):
        global s
        s.send("All users list".encode())

    def update_live_user_list(self, data):
        cs=self.Lb1.curselection()
        self.Lb1.delete(0,tk.END)
        i=0
        print("before update_live_user_list data was: ", self.data)
        print("updating live user list: ", data)
        self.data = data
        for key in data:
            self.Lb1.insert(i, key)
            i = i + 1

    def update_1hr_list(self, data):
        cs=self.Lb1.curselection()
        self.Lb1.delete(0,tk.END)
        i=0
        for key in data:
            self.Lb1.insert(i, key)
            i = i + 1

    def update_all_user_list(self, data):
        cs=self.Lb1.curselection()
        self.Lb1.delete(0,tk.END)
        i=0
        self.allusers1 = data
        global publickeys
        publickeys = data
        for key in data:
            self.Lb1.insert(i, key)
            i = i + 1

    def start_asyncchat(self):
        users = list(self.allusers1.keys())
        user = users[self.Lb1.curselection()[0]]
        if(user in self.newWindow):
            if(not self.newWindow[user].winfo_exists()):
                self.newWindow[user] = tk.Toplevel(self.master)
                objectdict[user] = Chatbox(self.newWindow[user], [user])
        else:
            self.newWindow[user] = tk.Toplevel(self.master)
            objectdict[user] = Chatbox(self.newWindow[user], [user])

    def start_chat(self):
        users = list(self.data.keys())
        user = users[self.Lb1.curselection()[0]]

        if(user in self.newWindow):
            if(not self.newWindow[user].winfo_exists()):
                self.newWindow[user] = tk.Toplevel(self.master)
                objectdict[user] = Chatbox(self.newWindow[user], [user])
        else:
            self.newWindow[user] = tk.Toplevel(self.master)
            objectdict[user] = Chatbox(self.newWindow[user], [user])

    def Logout(self):
        global s
        s.send("logout".encode())
        s.close()
        self.frame.destroy()
        Login(self.master)

class Chatbox:
    def __init__(self, master, otheruser):
        self.master = master
        self.otheruser = otheruser
        self.frame = tk.Frame(self.master)
        self.chatLog = tk.Text(self.frame, bd=0, bg="white", height="8", width="50")          
        scrollbar = tk.Scrollbar(self.frame, command=self.chatLog.yview, cursor="heart")
        self.chatLog['yscrollcommand'] = scrollbar.set
        self.chatLog.grid(row=0, columnspan = 2)
        self.entry1 = tk.Entry(self.frame)
        self.entry1.grid(row=1, columnspan = 2, sticky="news")
        SendButton = tk.Button(self.frame, text="Send",
                            bd=0, bg="#FFBF00", activebackground="#FACC2E",
                            command=self.send_chat)        
        SendButton.grid(row=2, column=0, sticky="news")
        self.quit = tk.Button(self.frame, text = 'Quit', command = self.quit_chat)
        self.quit.grid(row=2, column=1, sticky="news")
        self.frame.pack()

    def send_chat(self):
        data = {}
        global publickeys
        senddata = self.entry1.get()
        for users in self.otheruser:
            data[users] = RSA.importKey(publickeys[users]).encrypt(senddata.encode('utf-8'), 16)
        self.chatLog.insert(tk.END, "You: " + senddata+"\n")
        data = pickle.dumps(data)
        s.send(data)
    

    def append_chat(self, data, user):
        self.chatLog.insert(tk.END, user + ": " + data.decode()+"\n")

    def quit_chat(self):
        for users in self.otheruser:
            del objectdict[users]
        self.master.destroy()


class myThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def on_closing(self):
        global close
        global s
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                s.send("logout".encode())
                s.close()
            except:
                pass
            close = 1
            exit()
            self.root.destroy()

    def run(self):
        self.root = tk.Tk()        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        Login(self.root)
        self.root.mainloop()

class myThread1(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def run(self):
        global s
        global selfprivatekey
        while(True):
            if(flag == 1):
                try:
                    readable, writable, exceptional = select.select([s],[],[],0.1)
                    for r in readable:
                        data = pickle.loads(r.recv(1024))
                        if data[0] == "Live users list": 
                            print("command to update live users list recvd")
                            objectdict["whoelse"].update_live_user_list(data[1])
                        elif data[0] == "Live 1Hr users list":
                            objectdict["whoelse"].update_1hr_list(list(data[1].keys()))
                        elif data[0] == "All users list":
                            objectdict["whoelse"].update_all_user_list(data[1])
                        elif data[0] == "Blocked":
                            messagebox.showinfo("BLocked","You are blocked buddy")
                        else:
                            decrypted_data = selfprivatekey.decrypt(data[1])
                            try:    
                                objectdict[data[0]].append_chat(decrypted_data, data[0])
                            except KeyError:
                                objectdict["whoelse"].newWindow[data[0]] = tk.Toplevel(objectdict["whoelse"].master)
                                objectdict[data[0]] = Chatbox(objectdict["whoelse"].newWindow[data[0]], [data[0]])
                                objectdict[data[0]].append_chat(decrypted_data, data[0])
                except:
                    exit()
            elif(close):
                exit()

def main(): 
    tkThread = myThread()
    select = myThread1()

if __name__ == '__main__':
    main()