import os
import re
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox

import requests
import pyglet
import ttkbootstrap as tb
from ttkbootstrap.constants import PRIMARY
from dotenv import load_dotenv

# --- ENVIRONMENT & API SETUP ---
load_dotenv(".env")
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("CURSEFORGE API_KEY not set in .env")

CURSEFORGE_BASE = "https://api.curseforge.com/v1"
HEADERS = {
    'Accept': 'application/json',
    'X-Api-Key': API_KEY
}
GAME_ID = 432  # Minecraft game ID for CurseForge

# --- GLOBAL STATE ---
versions = []
selected_mods = []  # Store mod info
mod_urls = []
download_path = None

isModFileSelected = False
isVersionChosen = False
isDownloadPathSet = False

# --- LOAD CUSTOM FONT ---
font_file = "Minecrafter.Reg.ttf"
custom_font = "Minecrafter"
if os.path.isfile(font_file):
    try:
        pyglet.font.add_file(font_file)
        pyglet.font.load("Minecrafter")
    except Exception as e:
        print(f"Failed to load custom font: {e}")
        custom_font = "Arial"  # Fallback font
else:
    print("WARNING! Font file not found:", font_file)
    custom_font = "Arial"  # Fallback font

# --- UTILITY FUNCTIONS ---
def load_versions():
    """Fetch Minecraft versions once and cache."""
    if versions:
        return versions
    try:
        resp = requests.get(f"{CURSEFORGE_BASE}/minecraft/version", headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        for entry in data:
            if entry.get("versionString"):
                versions.append(entry["versionString"])
        # Sort versions in reverse order (newest first)
        versions.sort(key=lambda x: [int(i) for i in x.split('.')] if x.replace('.', '').isdigit() else [0], reverse=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load Minecraft versions:\n{e}")
    return versions

def check_all_conditions():
    """Enable submit button only when all three steps are done."""
    if isModFileSelected and isVersionChosen and isDownloadPathSet:
        sub_button.config(state="normal")
    else:
        sub_button.config(state="disabled")

def update_status(message, is_error=False):
    """Update status label with message."""
    if is_error:
        status_label.config(text=message, bootstyle="danger")
    else:
        status_label.config(text=message, bootstyle="info")
    root.update_idletasks()

# --- STEP 1: SELECT & PARSE MOD FILES ---
def ModFiles():
    global isModFileSelected, selected_mods
    
    # Default to Minecraft mods folder
    default_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", ".minecraft", "mods")
    if not os.path.exists(default_dir):
        default_dir = os.path.expanduser("~")
    
    filenames = filedialog.askopenfilenames(
        initialdir=default_dir,
        title="Select mods to update",
        filetypes=[("JAR files", "*.jar"), ("All files", "*.*")]
    )
    
    if not filenames:
        return

    selected_mods.clear()
    
    for fullpath in filenames:
        base = os.path.basename(fullpath)
        # More sophisticated slug extraction
        slug = extract_mod_slug(base)
        
        # Detect loader from filename
        detected_loader = detect_loader(base)
        
        selected_mods.append({
            'filename': base,
            'slug': slug,
            'loader': detected_loader,
            'path': fullpath
        })

    isModFileSelected = True
    
    # Update UI
    path_entry.delete(0, tk.END)
    path_entry.insert(0, f"{len(selected_mods)} mod(s) selected")
    
    update_status(f"Selected {len(selected_mods)} mod(s)")
    check_all_conditions()

def extract_mod_slug(filename):
    """Extract mod slug from filename, handling various naming patterns."""
    base = os.path.splitext(filename)[0]
    
    # Common patterns to remove version info
    patterns = [
        r'^(.+?)[-_]v?\d+\.\d+.*$',  # name-1.0.0
        r'^(.+?)[-_]\d+\.\d+.*$',   # name_1.0.0
        r'^(.+?)[-_]mc\d+\.\d+.*$', # name-mc1.19.2
        r'^(.+?)[-_]\[.*?\].*$',    # name-[1.19.2]
        r'^(.+?)[-_]\(.*?\).*$',    # name-(forge)
    ]
    
    for pattern in patterns:
        match = re.match(pattern, base, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return base

def detect_loader(filename):
    """Detect mod loader from filename."""
    filename_lower = filename.lower()
    if "fabric" in filename_lower:
        return "fabric"
    elif "forge" in filename_lower:
        return "forge"
    elif "quilt" in filename_lower:
        return "quilt"
    else:
        return "unknown"

# --- STEP 2: CHOOSE VERSION & SEARCH IN BACKGROUND ---
def mod_search(event):
    if not selected_mods:
        return
    version = vsCombo.get()
    if not version:
        return
        
    update_status("Searching for mods...")
    threading.Thread(target=_mod_search_worker, args=(version,), daemon=True).start()

def _mod_search_worker(version):
    global isVersionChosen, mod_urls
    
    mod_urls.clear()
    found_count = 0
    
    for mod_info in selected_mods:
        try:
            # Search for mod by slug
            params = {
                'gameId': GAME_ID,
                'gameVersion': version,
                'searchFilter': mod_info['slug'],
                'sortField': 6,  # Sort by downloads
                'sortOrder': 'desc'
            }
            
            resp = requests.get(f"{CURSEFORGE_BASE}/mods/search", params=params, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            
            data = resp.json().get("data", [])
            
            # Find best match
            best_match = None
            for mod in data:
                mod_slug = mod.get("slug", "").lower()
                search_slug = mod_info['slug'].lower()
                
                # Exact match or contains match
                if mod_slug == search_slug or search_slug in mod_slug or mod_slug in search_slug:
                    best_match = mod
                    break
            
            if not best_match and data:
                best_match = data[0]  # Fallback to first result
            
            if best_match:
                mod_urls.append({
                    'mod_id': best_match['id'],
                    'name': best_match['name'],
                    'slug': best_match['slug'],
                    'website_url': best_match.get('links', {}).get('websiteUrl', ''),
                    'original_mod': mod_info
                })
                found_count += 1
            else:
                print(f"No results found for: {mod_info['slug']}")
                
        except Exception as e:
            print(f"Search failed for {mod_info['slug']}: {e}")

    isVersionChosen = True
    root.after(0, lambda: [
        update_status(f"Found {found_count}/{len(selected_mods)} mods"),
        check_all_conditions()
    ])

# --- STEP 3: SELECT DOWNLOAD PATH ---
def DownloadPath():
    global isDownloadPathSet, download_path
    
    # Default to Minecraft mods folder
    default_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", ".minecraft", "mods")
    if not os.path.exists(default_dir):
        default_dir = os.path.expanduser("~")
    
    folder = filedialog.askdirectory(
        title="Select download location",
        initialdir=default_dir
    )
    
    if not folder:
        return

    isDownloadPathSet = True
    download_path = folder

    dl_path_entry.delete(0, tk.END)
    dl_path_entry.insert(0, download_path)
    
    update_status(f"Download path set: {os.path.basename(download_path)}")
    check_all_conditions()

# --- STEP 4: DOWNLOAD MODS ---
def download_mod_file(mod_info, version, dest_dir):
    """Download the latest compatible file for a mod."""
    try:
        mod_id = mod_info['mod_id']
        original_mod = mod_info['original_mod']
        
        # Get mod files
        resp = requests.get(
            f"{CURSEFORGE_BASE}/mods/{mod_id}/files",
            params={'gameVersion': version},
            headers=HEADERS,
            timeout=15
        )
        resp.raise_for_status()
        
        files = resp.json().get("data", [])
        if not files:
            print(f"No files found for mod: {mod_info['name']}")
            return False
        
        # Filter files by game version and loader compatibility
        compatible_files = []
        for file in files:
            game_versions = [gv.lower() for gv in file.get("gameVersions", [])]
            
            # Check if file supports the target version
            if version.lower() in game_versions:
                # Check loader compatibility
                if original_mod['loader'] == 'unknown':
                    compatible_files.append(file)
                else:
                    # Look for loader in game versions or dependencies
                    loader_found = any(original_mod['loader'].lower() in gv.lower() for gv in game_versions)
                    if loader_found or original_mod['loader'] == 'unknown':
                        compatible_files.append(file)
        
        if not compatible_files:
            print(f"No compatible files for {mod_info['name']} @ {version}")
            return False
        
        # Sort by file date (newest first) and pick the first one
        compatible_files.sort(key=lambda f: f.get('fileDate', ''), reverse=True)
        file_to_download = compatible_files[0]
        
        download_url = file_to_download.get("downloadUrl")
        if not download_url:
            print(f"No download URL for {mod_info['name']}")
            return False
        
        filename = file_to_download.get("fileName", f"{mod_info['slug']}.jar")
        
        # Download the file
        print(f"Downloading {filename}...")
        file_resp = requests.get(download_url, timeout=30)
        file_resp.raise_for_status()
        
        output_path = os.path.join(dest_dir, filename)
        with open(output_path, "wb") as f:
            f.write(file_resp.content)
        
        print(f"Downloaded: {filename}")
        return True
        
    except Exception as e:
        print(f"Download failed for {mod_info['name']}: {e}")
        return False

def process_downloads():
    """Download all found mods."""
    if not mod_urls or not download_path:
        messagebox.showerror("Error", "No mods to download or download path not set")
        return
    
    version = vsCombo.get()
    if not version:
        messagebox.showerror("Error", "No version selected")
        return
     
    success_count = 0
    total_count = len(mod_urls)
    
    for i, mod_info in enumerate(mod_urls, 1):
        root.after(0, lambda: update_status(f"Downloading {i}/{total_count}: {mod_info['name']}"))
        
        if download_mod_file(mod_info, version, download_path):
            success_count += 1
    
    root.after(0, lambda: [
        update_status(f"Downloaded {success_count}/{total_count} mods successfully", 
                     is_error=success_count < total_count),
        messagebox.showinfo("Download Complete", 
                          f"Downloaded {success_count} out of {total_count} mods.\n"
                          f"Files saved to: {download_path}")
    ])

def modDownload():
    """Start download process in background thread."""
    if not mod_urls:
        messagebox.showwarning("Warning", "No mods found. Please select mods and choose a version first.")
        return
    
    # Disable button during download
    sub_button.config(state="disabled")
    threading.Thread(target=lambda: [
        process_downloads(),
        root.after(0, lambda: sub_button.config(state="normal"))
    ], daemon=True).start()

# --- UI SETUP ---
root = tb.Window(themename='darkly')
root.title("Minecraft Mod Updater")
root.geometry("600x500")
root.resizable(False, False)

# Main container
main_frame = tb.Frame(root)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Header
header_label = tb.Label(
    main_frame, 
    text="Minecraft Mod Updater",
    bootstyle="white", 
    font=(custom_font, 20)
)
header_label.pack(pady=(0, 20))

# Step 1: Mod Selection
step1_frame = tb.LabelFrame(main_frame, text="Step 1: Select Mods", padding=10)
step1_frame.pack(fill="x", pady=(0, 10))

sel_button = tb.Button(
    step1_frame, 
    text="Browse for Mods...", 
    command=ModFiles,
    bootstyle=PRIMARY
)
sel_button.pack(side="left", padx=(0, 10))

path_entry = tb.Entry(step1_frame, width=50)
path_entry.pack(side="left", fill="x", expand=True)

# Step 2: Version Selection
step2_frame = tb.LabelFrame(main_frame, text="Step 2: Choose Minecraft Version", padding=10)
step2_frame.pack(fill="x", pady=(0, 10))

version_label = tb.Label(step2_frame, text="Version:")
version_label.pack(side="left", padx=(0, 10))

vsCombo = tb.Combobox(step2_frame, bootstyle="darkly", values=load_versions(), width=20)
vsCombo.pack(side="left")

if versions:
    vsCombo.set(versions[0])  # Set to latest version
vsCombo.bind("<<ComboboxSelected>>", mod_search)

# Step 3: Download Location
step3_frame = tb.LabelFrame(main_frame, text="Step 3: Download Location", padding=10)
step3_frame.pack(fill="x", pady=(0, 10))

path_button = tb.Button(
    step3_frame, 
    text="Browse...", 
    command=DownloadPath
)
path_button.pack(side="left", padx=(0, 10))

dl_path_entry = tb.Entry(step3_frame, width=50)
dl_path_entry.pack(side="left", fill="x", expand=True)

# Submit Button
button_frame = tb.Frame(main_frame)
button_frame.pack(pady=20)

sub_button = tb.Button(
    button_frame, 
    text="Download Updated Mods!", 
    command=modDownload, 
    state="disabled",
    bootstyle="success"
)
sub_button.pack()

# Status Label
status_label = tb.Label(main_frame, text="Ready", bootstyle="info")
status_label.pack(pady=(10, 0))

# Initialize
check_all_conditions()

if __name__ == "__main__":
    root.mainloop()