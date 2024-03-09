import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import requests
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import pyglet
from dotenv import load_dotenv
load_dotenv(".env")

pyglet.font.add_file("Minecrafter.Reg.ttf")
Minecrafter =  pyglet.font.load("Minecrafter")

versions = []
mods=[]
n_mods = []
loader = []
Api_key: str = os.getenv("API_KEY")

headers = {
  'Accept': 'application/json',
  'x-api-key': Api_key
}
r = requests.get('https://api.curseforge.com/v1/minecraft/version', headers = headers)

if r.status_code == 200:
  # Process the response data
  data = r.json()

  # Loop through each game entry and access data using schema-defined properties
  for game_entry in data["data"]:
    game_version = game_entry["versionString"]
    versions.append(game_version)
else:
  # Handle unsuccessful response
  print(f"Error retrieving data: {r.status_code}")
 

def mod_search(e):
    r = requests.get('https://api.curseforge.com/v1/mods/search', params={
    'gameId': '432',
    'gameVersion': vsCombo.get(),
    'searchFilter': n_mods
    }, headers = headers)

    print(r.json())

'''
def mod_download():
   r = requests.get('https://api.curseforge.com/v1/mods/{modId}', headers = headers)
'''



#open file  
def ModFiles():
        
    username = os.getlogin()

    filenames = filedialog.askopenfilenames( #if user doesnt have a mods folder it just opens on default directory (documents)
        initialdir = os.path.join("C:\\Users", username, "AppData", "Roaming", ".minecraft", "mods"), # os.path.join creates the complete folder path by joining the individual directory parts
        title= "select mods to update",
        filetypes= [("jar files","*.jar")] 
    )

    for filename in filenames:
        mod_name = ( os.path.basename(filename))
        mods.append(mod_name)
        for mod_name in mods:
            parts = mod_name.split("-", 1)
            if(len(parts) > 0 ):
               new_name = (parts[0])
               n_mods.append(new_name)
            else:
               None
    
    
    if "fabric" in mod_name:
       print("fabric")
    elif "forge" in mod_name:
       print("forge")
    
    path  = os.path.dirname(filename)
    path_text = (path + filename)
    path_entry.insert(0,path_text)   

    print(n_mods)


# get download location of new mods
def DownloadPath():
    filepath = filedialog.askdirectory(
        title= "select download location",
    )


# creating window
root = tb.Window(themename='darkly')
root.title("Minecraft Mod Updater")
root.geometry("500x400")


# Widgets 

# Text on top for Mod selection
title_label = tb.Label(
    root,
    text = "Select your Mods folder",
    bootstyle = "white",
    font=("Minecrafter")
    )

title_height = title_label.winfo_height()

screen_width = root.winfo_screenwidth()
x_center = int((400 / 2) - (title_height / 2))  # Use height for centering
title_label.place(x=100, y=10)

# First browse button for mod selection
sel_button = tb.Button(   
    root,
    bootstyle = PRIMARY,
    text ="Browse:",
    command = ModFiles
    )
sel_button.grid(pady= 60,padx= 35,sticky="w",row = 2, column= 2,)

# label for file path on mod selection
path_entry = tb.Entry(
    root,
    width= 50
    )
path_entry.grid(padx= 100,pady= 60,sticky="e",row = 2, column= 2,)

#combobox for Versions
vsCombo = tb.Combobox( 
    root,
    bootstyle ="darkly",
    values= (versions),
      )   
vsCombo.grid(row = 4, column= 2)
vsCombo.bind("<<ComboboxSelected>>", mod_search)
vsCombo.current(0)


# second button for download path selection
path_button = tb.Button(   
    root,
    text ="Browse",
    command = DownloadPath
    )
path_button.grid(row = 5, column= 2)

#Final submit button
sub_button = tb.Button(
    root,
    text ="Find my mods",
)
sub_button.grid(row = 6, column= 2)
sub_button.configure(state="disabled") # Disabled on default until user selects all 3 catagories



# running
root.mainloop()
