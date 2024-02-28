import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
import os
from bs4 import BeautifulSoup
import requests


#open file  
def ModFiles():

    # gettins users name for mod folder dir
    
    #creating empty mods list
    mods=[]
    username = os.getlogin()

    filenames = filedialog.askopenfilenames(
        initialdir = os.path.join("C:\\Users", username, "AppData", "Roaming", ".minecraft", "mods"), # os.path.join creates the complete folder path by joining the individual directory parts
        title= "select mods to update",
        filetypes= [("jar files","*.jar")] 
    )

    for filename in filenames:
        mod_name = ( os.path.basename(filename))
        mods.append(mod_name)
        

def DownloadPath():
    filepath = filedialog.askdirectory(
        title= "select download location",
    )



#def selected_version(version):
    


# gathering website data
website = "https://mcversions.net"
response = requests.get(website)

soup = BeautifulSoup(response.text, "html.parser")
elements = soup.find_all("div", class_="item flex items-center p-3 border-b border-gray-700 snap-start ncItem")
versions = [element["data-version"] for element in elements]


# creating window
ctk.set_appearance_mode("dark")
window = ctk.CTk()
window.title("Minecraft Mod Updater")
window.geometry("600x400")

# Widgets 
label = ctk.CTkLabel( # Text for Mod selection
    window,
      text = "Select your Mods folder", 
      fg_color="red", 
      text_color="white", # can also do hex code so like text_color = "#000" , if you want colors to change based on light or darke mode its fg_color = ("blue","red")
      corner_radius= 10)
label.pack(pady = 20)

button = ctk.CTkButton(   # First button for mod selection
    window,
    text ="Browse",
    fg_color="blue",
    text_color= "white",
    command = ModFiles
    )
button.pack()

combobox = ctk.CTkComboBox( # Combobox for all versions
    window,
    values= (versions),
    )
combobox.pack(pady = 20)

myCombo = ttk.Combobox(window, values= (versions))
myCombo.pack()



button = ctk.CTkButton(   # second button for download path selection
    window,
    text ="Browse",
    fg_color="blue",
    text_color= "white",
    command = DownloadPath
    )
button.pack()



#print(combobox.get())  this gets the current combobox value

# running
window.mainloop()
