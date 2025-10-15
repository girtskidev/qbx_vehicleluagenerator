import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

# === DEFAULT SETTINGS ===
DEFAULT_BRAND = "Generic"
DEFAULT_PRICE = 150000
# Set the desired universal custom category to lowercase
DEFAULT_CATEGORY = "custom" 
DEFAULT_TYPE = "CIV" 
OUTPUT_FILE = "vehicles.lua"
LOG_FILE = "vehicle_pack_log.lua"


def beautify_name(value: str):
    """Convert 'expol_banshee' to 'Expol Banshee'."""
    return " ".join(w.capitalize() for w in re.split(r'[_\- ]+', value))

def generate_display_name(spawn_name: str):
    """Convert 'expol_banshee' or 'ExpOl-Banshee' to 'expol banshee' or 'ExpOl Banshee'."""
    return re.sub(r'[_\- ]+', ' ', spawn_name).strip()


def read_file(path: str):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def get_handling_name(folder_path: str):
    """Extract <handlingName> from handling.meta if it exists (recursive search retained)."""
    for root, _, files in os.walk(folder_path):
        for f in files:
            if f.lower() == "handling.meta":
                text = read_file(os.path.join(root, f))
                matches = re.findall(r"<handlingName>\s*(.*?)\s*</handlingName>", text, re.IGNORECASE | re.DOTALL)
                if matches:
                    return matches[0].strip()
    return None


def get_brand_and_price(folder_path: str):
    """Extract brand, price, and primary GTA vehicle class from metadata.
       Now iterates through all files to find all possible values before returning."""
    brand = None
    price = None
    category = None
    
    for root, _, files in os.walk(folder_path): 
        for f in files:
            if not f.lower().endswith((".meta", ".xml", ".lua")):
                continue
            text = read_file(os.path.join(root, f))
            
            # Search for brand
            if not brand:
                brand_match = re.search(r"<manufacturer>\s*([\w\d_-]+)\s*</manufacturer>", text, re.IGNORECASE)
                if brand_match:
                    brand = beautify_name(brand_match.group(1))
            
            # Search for price
            if not price:
                price_match = re.search(r"price\s*=\s*(\d+)", text)
                if price_match:
                    price = int(price_match.group(1))
            
            # Search for category (vehicleClass)
            if not category:
                cat_match = re.search(r"<vehicleClass>\s*([\w\d_-]+)\s*</vehicleClass>", text, re.IGNORECASE)
                if cat_match:
                    # Keep category in the original extracted case for keyword check
                    category = cat_match.group(1) 
            
    # Return the best values found after processing all files
    return brand, price, category


def generate_vehicle_entry(spawn_name, name, brand, price, category, vtype):
    """UPDATED: Now accepts the final display name as an argument."""
    return f"""    {spawn_name} = {{
        name = '{name}',
        brand = '{brand}',
        model = '{spawn_name}',
        price = {price},
        category = '{category}',
        type = '{vtype}',
        hash = `{spawn_name}`
    }},"""


def main():
    root = tk.Tk()
    root.withdraw()
    selected_folder = filedialog.askdirectory(title="Select main vehicles folder")
    if not selected_folder:
        messagebox.showwarning("Cancelled", "No folder selected.")
        return

    vehicles = []
    total_found = 0
    pack_log = {}
    
    processed_spawns = set()

    for root_dir, subdirs, _ in os.walk(selected_folder):
        for subfolder in subdirs:
            full_path = os.path.join(root_dir, subfolder)
            pack_name = subfolder # This is the resource folder name

            if not os.path.isdir(full_path):
                continue

            spawn = get_handling_name(full_path)
            if not spawn:
                continue 

            # === DUPLICATE CHECK ===
            if spawn.lower() in processed_spawns:
                print(f"[!] Skipping duplicate entry for: {spawn} (found in {full_path})")
                continue 
            
            processed_spawns.add(spawn.lower())
            # === END DUPLICATE CHECK ===
            
            brand, price, extracted_category = get_brand_and_price(full_path) 

            brand = brand or DEFAULT_BRAND
            price = price or DEFAULT_PRICE
            
            # Generate the base display name
            display_name = generate_display_name(spawn)
            
            # =========================================================
            # === REVISED CATEGORY AND TYPE CLASSIFICATION LOGIC ===
            # =========================================================
            
            # Start with the default type and category
            category = DEFAULT_CATEGORY
            vtype = DEFAULT_TYPE
            
            is_emergency = False
            
            # Determine the target string to check for keywords
            if extracted_category:
                check_target = extracted_category.upper()
            elif spawn:
                check_target = spawn.upper()
            else:
                check_target = pack_name.upper()

            # Check for PD/Fire keywords
            if any(x in check_target for x in ["POLICE", "FIRE", "FBI", "SHERIFF", "LSPD", "PD", "EMERGENCY"]):
                # Set both type and category to 'emergency' as requested
                vtype = "emergency"
                category = "emergency"
                is_emergency = True
                
                # Append ' (PD)' to the display name
                display_name += " (PD)"
            
            # Check for EMS keywords
            elif any(x in check_target for x in ["EMS", "AMBULANCE", "MEDIC"]):
                # Set both type and category to 'emergency' as requested
                vtype = "emergency"
                category = "emergency"
                is_emergency = True
                
                # Append ' (EMS)' to the display name
                display_name += " (EMS)"
            
            # If it's a civilian car, no change to name, type, or category.
            
            # =========================================================
            # === END REVISED CLASSIFICATION LOGIC ===
            # =========================================================

            # Use the new generate_vehicle_entry with the modified display_name
            vehicles.append(generate_vehicle_entry(spawn, display_name, brand, price, category, vtype))
            total_found += 1
            print(f"[+] {spawn} ({brand}) found in pack: {pack_name} (Category: {category}, Type: {vtype}, Name: {display_name})")
            
            if pack_name not in pack_log:
                pack_log[pack_name] = []
            pack_log[pack_name].append(spawn)

    if not vehicles:
        messagebox.showerror("No Vehicles Found", "No handling.meta files with valid spawn names were found.")
        return

    # 1. Write vehicles.lua
    output_path = os.path.join(selected_folder, OUTPUT_FILE)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("return {\n")
            f.write("\n\n".join(vehicles))
            f.write("\n}\n")
    except Exception as e:
        messagebox.showerror("Write Error", f"Could not write {OUTPUT_FILE}: {e}")
        return

    # 2. Write vehicle_pack_log.lua
    log_output_path = os.path.join(selected_folder, LOG_FILE)
    try:
        with open(log_output_path, "w", encoding="utf-8") as f:
            f.write("-- This file maps vehicle spawn names to the resource folder (pack) they were found in.\n")
            f.write("return {\n")
            for pack, spawn_list in pack_log.items():
                spawns_str = ", ".join(f"'{s}'" for s in spawn_list)
                f.write(f"    ['{pack}'] = {{ {spawns_str} }},\n")
            f.write("}\n")
    except Exception as e:
        messagebox.showwarning("Log Write Warning", f"Could not write {LOG_FILE}: {e}")


    messagebox.showinfo("Success", f"✅ Generated {OUTPUT_FILE} with {total_found} unique vehicles.\nSaved to:\n{output_path}\n\nAlso created log file: {LOG_FILE}")


if __name__ == "__main__":
    main()