"""

A utility for loading a file, performing a QC check, and migrating legacy datasheets 
into an SQLite database or SQL file. The migration process includes creating a 
versioned folder hierarchy with a log and storing of the source file for reference.

It supports CSV, Excel, JSON, and XML formats, creating versioned directories, 
logging migration details, and organizing migrated files.

------------

The QC function is a placeholder that always passes, but can be expanded to include specific 
checks.

The Migrate function creates a structured folder hierarchy in the source file directory, with 
future potential to integrate database APIs for structured database directories. The Category 
dropdown is a placeholder for database integration.

The QC function performs event-handling so that only files passing the check can be migrated, unlocking the 
Migrate button if successful.

------------

Modules required:
    os         - for file and directory manipulation
    shutil     - for copying files
    csv        - for handling CSV files
    json       - for working with JSON files
    sqlite3    - for database interactions (if needed)
    pandas     - for reading and writing Excel files
    tkinter    - for creating the graphical user interface
    xml.etree  - for parsing and handling XML files
    datetime   - for timestamping the logs

Created by: Craig Kane
Date: [29-03-2025]
Version: 1.0.0

"""


# gui.py
import os
import shutil
import csv
import json
import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import xml.etree.ElementTree as ET


filepath = ""

def load_file(file_label, qc_button, migrate_button):
    global filepath
    
    filepath = filedialog.askopenfilename(title="Select a File")
    
    if filepath:
        filename = os.path.basename(filepath)
        file_label.config(text=filename) 
        qc_button.config(state="normal")
        migrate_button.config(state="disabled") 
    else:
        file_label.config(text="No file selected")
        qc_button.config(state="disabled")
        migrate_button.config(state="disabled")


def qc_check(traffic_light, migrate_button):
    # Simulate a successful QC check
    traffic_light.config(bg="green")
    migrate_button.config(state="normal")


def migrate(file_label, export_type_var, filepath):

    migration_root = os.path.join(os.path.dirname(filepath), "migrations")
    os.makedirs(migration_root, exist_ok=True)


    file_extension = export_type_var.get()
    type_folder = file_extension[1:] 
    type_folder_path = os.path.join(migration_root, type_folder)
    os.makedirs(type_folder_path, exist_ok=True)

    version_folder = "v001"
    version_folder_path = os.path.join(type_folder_path, version_folder)
    while os.path.exists(version_folder_path):
        version = int(version_folder[1:]) + 1
        version_folder = f"v{str(version).zfill(3)}"
        version_folder_path = os.path.join(type_folder_path, version_folder)
    
    os.makedirs(version_folder_path, exist_ok=True)

    data_folder = os.path.join(version_folder_path, "data")
    source_folder = os.path.join(version_folder_path, "source")
    log_folder = os.path.join(version_folder_path, "log")
    os.makedirs(data_folder, exist_ok=True)
    os.makedirs(source_folder, exist_ok=True)
    os.makedirs(log_folder, exist_ok=True)

  
    original_filename = os.path.basename(filepath)
    name_without_extension, _ = os.path.splitext(original_filename)

 
    source_file_path = os.path.join(source_folder, original_filename)
    shutil.copy(filepath, source_file_path)


    new_filename = f"{name_without_extension}_migration{file_extension}"
    new_file_path = os.path.join(data_folder, new_filename)

 
    if filepath.lower().endswith('.csv'):
        migrate_csv(filepath, new_file_path)
    elif filepath.lower().endswith('.xlsx'):
        migrate_excel(filepath, new_file_path)
    elif filepath.lower().endswith('.json'):
        migrate_json(filepath, new_file_path)
    elif filepath.lower().endswith('.xml'):
        migrate_xml(filepath, new_file_path)


    current_time = datetime.now()
    log_file_path = os.path.join(log_folder, "migration_log.txt")
    timestamp = current_time.strftime("%d-%m-%Y %H:%M:%S")
    
    with open(log_file_path, "w") as log_file:
        log_file.write(f"Migration Log - {timestamp}\n")
        log_file.write(f"Original File: {os.path.normpath(filepath)}\n")
        log_file.write(f"Source File: {os.path.normpath(source_file_path)}\n")
        log_file.write(f"Migrated File: {os.path.normpath(new_file_path)}\n")
        log_file.write("-------------------------------------------------\n")


    file_label.config(text=f"File Published")
    migrate_button.config(state="disabled")


def migrate_csv(filepath, new_file_path):
    with open(filepath, 'r') as original_file:
        reader = csv.reader(original_file)
        rows = list(reader)

        with open(new_file_path, "w") as new_file:
            columns = rows[0]
            for row in rows[1:]:
                insert_statement = f"INSERT INTO my_table ({', '.join(columns)}) VALUES ({', '.join([repr(cell) for cell in row])});\n"
                new_file.write(insert_statement)


def migrate_excel(filepath, new_file_path):
    df = pd.read_excel(filepath)
    
    with open(new_file_path, "w") as new_file:
        columns = df.columns.tolist()
        for _, row in df.iterrows():
            insert_statement = f"INSERT INTO my_table ({', '.join(columns)}) VALUES ({', '.join([repr(cell) for cell in row])});\n"
            new_file.write(insert_statement)


def migrate_json(filepath, new_file_path):
    with open(filepath, 'r') as original_file:
        data = json.load(original_file)
        
    with open(new_file_path, "w") as new_file:
        for entry in data:
            keys = entry.keys()
            values = entry.values()
            insert_statement = f"INSERT INTO my_table ({', '.join(keys)}) VALUES ({', '.join([repr(value) for value in values])});\n"
            new_file.write(insert_statement)


def migrate_xml(filepath, new_file_path):
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    with open(new_file_path, "w") as new_file:
        for item in root.findall(".//item"):
            fields = item.findall(".//*")
            keys = [field.tag for field in fields]
            values = [field.text for field in fields]
            insert_statement = f"INSERT INTO my_table ({', '.join(keys)}) VALUES ({', '.join([repr(value) for value in values])});\n"
            new_file.write(insert_statement)

            
# Set up main window
window = tk.Tk()
window.title("Migrate File to Database")
window.geometry("400x350")
window.config(bg="#F0F0F0")
window.resizable(False, False)

# Title
title_label = tk.Label(window, text="Migrate File to Database", font=("Arial", 14), bg="#F0F0F0")
title_label.pack(pady=10)

divider1 = tk.Frame(window, height=2, bg="#A0A0A0", relief="sunken")
divider1.pack(fill="x", padx=10, pady=5)

# Dropdown for Lighting, Compositing, Production
dropdown_frame = tk.Frame(window, bg="#F0F0F0")
dropdown_frame.pack(pady=5)
category_label = tk.Label(dropdown_frame, text="Category:", bg="#F0F0F0")
category_label.pack(side="left", padx=(0, 5))
category_var = tk.StringVar(window)
category_var.set("Lighting")
category_menu = tk.OptionMenu(dropdown_frame, category_var, "Lighting", "Compositing", "Production")
category_menu.config(bg="#D9D9D9", relief=tk.FLAT)
category_menu.pack(side="left")

divider2 = tk.Frame(window, height=2, bg="#A0A0A0", relief="sunken")
divider2.pack(fill="x", padx=10, pady=5)

button_frame = tk.Frame(window, bg="#F0F0F0")
button_frame.pack(pady=5)

load_button = tk.Button(button_frame, text="Load File", command=lambda: load_file(file_label, qc_button, migrate_button), relief=tk.FLAT, bg="#D9D9D9", padx=10, pady=5)
load_button.pack(side="left", padx=5)

qc_button = tk.Button(button_frame, text="QC Check", command=lambda: qc_check(traffic_light, migrate_button), state="disabled", relief=tk.FLAT, bg="#D9D9D9", padx=10, pady=5)
qc_button.pack(side="left", padx=5)

file_label = tk.Label(window, text="No file selected", bg="#F0F0F0", width=40)
file_label.pack(pady=5)

traffic_light = tk.Label(window, bg="grey", width=5, height=2, relief="sunken")
traffic_light.pack(pady=5)

dropdown_frame = tk.Frame(window, bg="#F0F0F0")
dropdown_frame.pack(pady=5)

file_type_label = tk.Label(dropdown_frame, text="File Type:", bg="#F0F0F0")
file_type_label.pack(side="left", padx=(0, 5))

export_type_var = tk.StringVar(window)
export_type_var.set(".db")
export_type_menu = tk.OptionMenu(dropdown_frame, export_type_var, ".db", ".sql")
export_type_menu.config(bg="#D9D9D9", relief=tk.FLAT)
export_type_menu.pack(side="left")

divider3 = tk.Frame(window, height=2, bg="#A0A0A0", relief="sunken")
divider3.pack(fill="x", padx=10, pady=5)

migrate_button = tk.Button(window, text="Migrate", command=lambda: migrate(file_label, export_type_var, filepath), state="disabled", relief=tk.FLAT, bg="#D9D9D9", padx=10, pady=5)
migrate_button.pack(pady=10)


window.mainloop()
