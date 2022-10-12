# Import Module
from tkinter import *
import tkinter
from turtle import bgcolor
import pyftpdlib.authorizers
import pyftpdlib.handlers
import pyftpdlib.servers
from tkinter import ttk
from tkinter import filedialog
# create root window
root = Tk()

# root window title and dimension
root.title("Create Connection")
bgcolor = "#91BBE5"
root.config(background="#91BBE5")
# Set geometry(widthxheight)
root.geometry('300x145')

text_host = Label(root, text="Host:", background=bgcolor)
text_host.grid(column = 1, row = 1 )
host = Entry(root, width = 20)
host.grid(column = 3, row =1)

text_user = Label(root, text="Username:", background=bgcolor)
text_user.grid(column = 1, row = 2 )
user = Entry(root, width = 20)
user.grid(column = 3, row = 2)

text_pw = Label(root, text="Password:", background=bgcolor)
text_pw.grid(column = 1, row = 3 )
password = Entry(root, width = 20)
password.grid(column = 3, row =3)

text_port = Label(root, text="Port:", background=bgcolor)
text_port.grid(column = 1, row = 4 )
txtvar_port = tkinter.StringVar()
txtvar_port.set("21")
port = Entry(root, width= 20, textvariable = txtvar_port , state = 'disabled')
port.grid(column = 3, row = 4)
# function to display text when
# button is clicked
#Create a label and a Button to Open the dialog
def select_directory():
   path= filedialog.askdirectory(title="Select a Folder")
   txtvar_serverDirectory.set(path)
text_serverDirectory = Label(root, text="Server Directory:", background=bgcolor)
text_serverDirectory.grid(column = 1, row = 5)

txtvar_serverDirectory = tkinter.StringVar()
serverDirectory = Entry(root,textvariable= txtvar_serverDirectory, width = 20)
serverDirectory.grid(column = 3, row = 5)
btn_selectServerDir = ttk.Button(root, text="Select", command= select_directory)
btn_selectServerDir.grid(column = 5, row = 5)

def create_connection():
	#Create an authenticated user
        authorizer = pyftpdlib.authorizers.DummyAuthorizer()
        authorizer.add_user(user.get(), password.get(), serverDirectory.get(), perm='elradfmw')

        #Create a handler to manage individual connections
        handler = pyftpdlib.handlers.FTPHandler
        handler.authorizer = authorizer

        #Launch an FTP server
        server = pyftpdlib.servers.FTPServer((host.get(), port.get()), handler)
        server.serve_forever()

# button widget with red color text
# inside
btn = Button(root, text = "Create connection", fg = "black", bg = "#F4A82C" , command=create_connection)
# set Button grid
btn.grid(column = 3, row = 6)

# Execute Tkinter
root.mainloop()
