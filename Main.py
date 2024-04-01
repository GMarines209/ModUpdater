import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import requests
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import pyglet
from dotenv import load_dotenv
from selenium import webdriver

load_dotenv(".env")

pyglet.font.add_file("Minecrafter.Reg.ttf")
Minecrafter =  pyglet.font.load("Minecrafter")

versions = []
mods=[]
n_mods = []
loader = []
url = []
end_count = 0

Api_key: str = os.getenv("API_KEY")

headers = {
  'Accept': 'application/json',
  'x-api-key': Api_key
}


r = requests.get('https://api.curseforge.com/v1/minecraft/version', headers = headers)
if r.status_code == 200:
     # Process the response data
    print("Response Status:", r.status_code)
    data = r.json()
    # Loop through each game entry 
    for game_entry in data["data"]:
        game_version = game_entry["versionString"]
        versions.append(game_version)
else:
    # Handle unsuccessful response
    print(f"Error retrieving data: {r.status_code}")


def mod_search(e):

    for i in range(len(n_mods)):
        r_mods = requests.get('https://api.curseforge.com/v1/mods/search', params={
        'gameId': '432',
        'gameVersion': vsCombo.get(),
        'searchFilter': n_mods[i]
        }, headers = headers)
        mod_data = r_mods.json()

        print("\n",r_mods.json(),"\n")

        mods = mod_data.get("data")

        for mod in mods:
            links = mod.get("links")  # Access the "links" object within each mod
            if links:
                website_url = links.get("websiteUrl")  # Extract the "websiteUrl"
                if website_url:
                    url.append(website_url)
            else:
                print("WARNING: 'links' key not found in a mod object.")
    print(url,"\n")
    end_count +1

    



#open file  
def ModFiles():
        
    username = os.getlogin()

    filenames = filedialog.askopenfilenames( #if user doesnt have a mods folder it just opens on default directory (documents)
        initialdir = os.path.join("C:\\Users", username, "AppData", "Roaming", ".minecraft", "mods"), # os.path.join creates the complete folder path by joining the individual directory parts
        title= "select mods to update",
        filetypes= [("jar files","*.jar")] 
    )
    print(filenames)

    count = 0

    for name in filenames:
        mod_name = ( os.path.basename(name))
        mods.append(mod_name)
        count += 1

        if count == len(filenames):
            for mod_name in mods:
                parts = mod_name.split("-", 1)
                if(len(parts) > 0 ):
                    new_name = (parts[0])
                    n_mods.append(new_name)

                    if "fabric" or "Fabric" in mod_name:
                        loader.append("fabric")
                    elif "forge" or "Forge" in mod_name:
                       loader.append("forge")
                    else:
                       loader.append("Error")
                else:
                    None

    
    path  = os.path.dirname(name)
    path_text = (path + name)
    path_entry.insert(0,path_text)   

    print(n_mods)
    print(loader)
    
    end_count + 1




# get download location of new mods
def DownloadPath():
    filepath = filedialog.askdirectory(
        title= "select download location",
    )
    dl_path = os.path.dirname(filepath)
    dl_path_text = (dl_path)
    dl_path_entry.insert(0,dl_path_text)

    end_count +1



def modDownload():
    browser = browser_Combo.get()

    if(browser == "chrome"):
        driver = webdriver.Chrome()
        for site in range(len(url)):
            driver.get(url[site])
    elif(browser == "edge"):
        print()
    elif(browser == "firefox"):
        print()
    
    end_count +1





# creating window
root = tb.Window(themename='darkly')
root.title("Minecraft Mod Updater")
root.geometry("530x430")
root.resizable(False,False)



# Widgets 


title_frame = tb.LabelFrame(
    root
)
title_frame.grid(sticky= "nesw")

# Text on top for Mod selection
title_label = tb.Label(
    title_frame,
    text = "Minecraft Mod Updater",
    bootstyle = "white",
    font=("Minecrafter",20)
    )
title_label.grid(row=0, columnspan=3, pady=10, padx= 60, sticky="new")


mod_label = tb.Label(
    root,
    text = "Choose What Mods You Want To Update:",
    bootstyle = "white",
    font=("Minecrafter",13)
)
mod_label.grid(row=1,column=0,pady=20,padx= 85, sticky= "ws")

#  browse button for mod selection
sel_button = tb.Button(   
    root,
    bootstyle = PRIMARY,
    text ="Browse:",
    command = ModFiles
    )
sel_button.grid(row = 2, column= 0,padx=20,sticky="w")

# label for file path on mod selection
path_entry = tb.Entry(
    root,
    width= 50
    )
path_entry.grid(row = 2, column= 0,padx= 85 ,sticky= "nsew")

#Label for Browser choice
browser_label = tb.Label(
    root,
    text = "Select Your Browser:",
    bootstyle = "white",
    font=("Minecrafter",10)
    )
browser_label.grid(row=3, column=0,sticky= "w" , padx= 20, pady= 20)

#combobox for browser with selinum
browser_Combo = tb.Combobox( 
    root,
    bootstyle ="darkly",
    values= ("Chrome","Edge","FireFox"),
      )   
browser_Combo.current(0)
browser_Combo.grid(row = 3, column= 0,padx= 200,pady= 20)

versions_label = tb.Label(
    root,
    text = "Desired Version:",
    bootstyle = "white",
    font=("Minecrafter",10)
    )
versions_label.grid(row=4,column=0,sticky= "w" , padx= 20, pady= 10)

#combobox for Versions
vsCombo = tb.Combobox( 
    root,
    bootstyle ="darkly",
    values= (versions),
      )   
vsCombo.grid(row = 4, column= 0)
vsCombo.bind("<<ComboboxSelected>>", mod_search)
vsCombo.current(0)

#Label for download path
path_label = tb.Label(
    root,
        text = "Download Location:",
        bootstyle = "white",
        font=("Minecrafter",13)
)
path_label.grid(row=5,column=0,pady=20,padx= 170, sticky= "ws")

# button for download path 
path_button = tb.Button(   
    root,
    text ="Browse",
    command = DownloadPath
    )
path_button.grid(row = 6, column= 0,padx=20,sticky="w")

#entrybox for download path
dl_path_entry = tb.Entry(
    root,
    width= 50,
)
dl_path_entry.grid(row = 6, column= 0,padx=80,sticky="nsew")


#Final submit button
sub_button = tb.Button(
    root,
    text ="Find My Mods!",
    command= modDownload,
)
sub_button.grid(row = 7, column= 0, pady = 30)



# running
root.mainloop()

