import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
from bs4 import BeautifulSoup
import requests
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# Get started on Forge integration ... pending api approval

#open file  
def ModFiles():
    
    #creating empty mods list
    mods=[]
    username = os.getlogin()

    filenames = filedialog.askopenfilenames( #if user doesnt have a mods folder it just opens on default directory (documents)
        initialdir = os.path.join("C:\\Users", username, "AppData", "Roaming", ".minecraft", "mods"), # os.path.join creates the complete folder path by joining the individual directory parts
        title= "select mods to update",
        filetypes= [("jar files","*.jar")] 
    )

    for filename in filenames:
        mod_name = ( os.path.basename(filename))
        mods.append(mod_name)
        
# get download location of new mods
def DownloadPath():
    filepath = filedialog.askdirectory(
        title= "select download location",
    )


# gathering website data
website = "https://mcversions.net"
response = requests.get(website)

soup = BeautifulSoup(response.text, "html.parser")
elements = soup.find_all("div", class_="item flex items-center p-3 border-b border-gray-700 snap-start ncItem")
versions = [element["data-version"] for element in elements]


# creating window
root = tb.Window(themename='darkly')
root.title("Minecraft Mod Updater")
root.geometry("600x400")

# Widgets 

# Text on top for Mod selection
label = tb.Label(
    root,
    text = "Select your Mods folder",
    bootstyle = PRIMARY 
    )
label.pack(pady = 20)

# First button for mod selection
sel_button = tb.Button(   
    root,
    bootstyle = PRIMARY,
    text ="Browse:",
    command = ModFiles
    )
sel_button.pack()

#combobox for Versions
vsCombo = tb.Combobox( 
    root,
    bootstyle ="darkly",
    values= (versions)
      )   
vsCombo.pack(pady = 20)
vsCombo.current(0)

# second button for download path selection
path_button = tb.Button(   
    root,
    text ="Browse",
    command = DownloadPath
    )
path_button.pack()

#Final submit button
sub_button = tb.Button(
    root,
    text ="Find my mods",
)
sub_button.pack(pady= 10)
sub_button.configure(state="disabled") # Disabled on default until user selects all 3 catagories





# running
root.mainloop()
