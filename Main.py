import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import requests
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
import pyglet
from dotenv import load_dotenv
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


load_dotenv(".env")

pyglet.font.add_file("Minecrafter.Reg.ttf")
Minecrafter =  pyglet.font.load("Minecrafter")

versions = []
mods = []
n_mods = []
loader = []
url = []

end_count = 0
download_path = "" 



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

    global end_count
    end_count += 1
    print(end_count)

    if(end_count == 3):
        sub_button.config(state= "normal")


    

# WORK ON FILENAME PARSING... MAKE BETTER 


# ALSO IF THE EXACT MOD ISNT FOUND DONT GIVE THE NEXT ONE
        # TELL USER NOT AVAILABLE IN THAT VERSION OR SOMETHING...

#open file  
def ModFiles():
        
    username = os.getlogin()

    filenames = filedialog.askopenfilenames( #if user doesnt have a mods folder it just opens on default directory 
        initialdir = os.path.join("C:\\Users", username, "AppData", "Roaming", ".minecraft", "mods"), # os.path.join creates the complete folder path by joining the individual directory parts
        title= "select mods to update",
        filetypes= [("jar files","*.jar")] 
    )
    print(filenames)

    # count to get the complete filenames before starting to split
    count = 0

    for name in filenames:

        base_name = ( os.path.basename(name))
        mods.append(base_name)
        count += 1

        if count == len(filenames):
                for base_name in mods:
                    parts = parts = re.split(r"[-_]", base_name, 1)  # Split on either dash or underscore

                    if(len(parts) > 0 ):

                        new_name = (parts[0])
                        n_mods.append(new_name)

                        if "fabric" in base_name.lower():
                            loader.append("fabric")
                        elif "forge" in base_name.lower():
                            loader.append("forge")
                        else:
                            loader.append("Error")
                    else:
                        n_mods.append(base_name)  # Append original name if no split
                        loader.append("unknown")  # Indicate unknown loader

    



    path  = os.path.dirname(name)
    path_text = (path + name)
    path_entry.insert(0,path_text)   

    print("Mod names:", n_mods)
    print("Loaders:", loader)

    # establishing the end count to enable the button
    global end_count
    end_count += 1
    print(end_count)

    if(end_count == 3):
        sub_button.config(state= "normal")

    


# get download location of new mods
def DownloadPath():
    filepath = filedialog.askdirectory(
        title= "select download location",
    )
    dl_path = os.path.dirname(filepath)
    dl_path_text = (dl_path)
    dl_path_entry.insert(0,dl_path_text)
    download_path = dl_path_text
    

    global end_count
    end_count += 1
    print(end_count)

    if(end_count == 3):
        sub_button.config(state= "normal")




# sets up the driver, headless mode, ignores safe download protection to allow remote downloading
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--ignore-certificate-errors")
    #try to set default directory to user input
    options.add_experimental_option("prefs", {
    "download.default_directory": r"C:\Users\downloads",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": False})    

    driver = webdriver.Chrome(options=options)
    return driver

def download_mod(driver, url):
    try:
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        
        # Wait for and click the download button
        download_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-cta.download-cta")))
        actions = ActionChains(driver)
        actions.move_to_element(download_button).click().perform()
        
        # Wait for and click the versions dropdown
        version_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "p.dropdown-selected-item")))
        actions.move_to_element(version_button).click().perform()
        
        # Select the desired version
        version_list_elements = driver.find_elements(By.TAG_NAME, "li")
        for element in version_list_elements:
            if element.text == vsCombo.get():
                element.click()
                break
        


                # this part doesnt  work :(

        # Wait for and click the loader dropdown
        loader_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'All Mod Loaders')]/following-sibling::p")))
        actions.move_to_element(loader_button).click().perform()
        
        # Select the desired loader
        loader_list_elements = driver.find_elements(By.TAG_NAME, "li")
        for element in loader_list_elements:
            if element.text.lower() == loader[element].lower():
                element.click()
                break

        # Click the final download button
        final_download_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-cta.download-cta")))
        actions.move_to_element(final_download_button).click().perform()

        print(f"Successfully initiated download for {url}")

    except Exception as e:
        print(f"Error occurred while processing {url}: {e}")


def process_urls(url):
    driver = setup_driver()
    for link in url:
        download_mod(driver, link)
    driver.quit()

# Example usage within Tkinter callback
def modDownload():
    global end_count

    process_urls(url)

    end_count += 1
    if end_count == 3:
        sub_button.config(state= "normal")





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
vsCombo.grid(row = 3, column= 0)
vsCombo.bind("<<ComboboxSelected>>", mod_search)
vsCombo.current(0)

#Label for download path
path_label = tb.Label(
    root,
        text = "Download Location:",
        bootstyle = "white",
        font=("Minecrafter",13)
)
path_label.grid(row=4,column=0,pady=20,padx= 170, sticky= "ws")

# button for download path 
path_button = tb.Button(   
    root,
    text ="Browse",
    command = DownloadPath
    )
path_button.grid(row = 5, column= 0,padx=20,sticky="w")

#entrybox for download path
dl_path_entry = tb.Entry(
    root,
    width= 50,
)
dl_path_entry.grid(row = 5, column= 0,padx=80,sticky="nsew")


#Final submit button
sub_button = tb.Button(
    root,
    text ="Find My Mods!",
    command= modDownload,
    state= "disabled"
)
sub_button.grid(row = 6, column= 0, pady = 30)
#ToolTip(sub_button, text = "Make sure you have ")

    


# running
root.mainloop()

