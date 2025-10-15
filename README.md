Vehicle Pack Lua Generator Readme
This script automates the creation of a vehicles.lua file for FiveM/GTA V server vehicle packs. It scans your vehicle folders, extracts important data, and organizes it for your server.

⚡ How It Works
It searches the vehicle resource folders you select.

It finds the Spawn Name (from handling.meta), Brand, and Price from the vehicle files.

It automatically sets the vehicle's Category and Type:

If it finds keywords like POLICE, FIRE, or EMS, the vehicle is marked as emergency and gets  (PD) or  (EMS) added to its name.

Otherwise, it's marked as custom and CIV (Civilian).

It generates vehicles.lua and a simple log file.

🛠️ Requirements
Python 3.x

🚀 Quick Start
Save the code as a Python file (e.g., generate_vehicle_lua.py).

Run the script:

Bash

python generate_vehicle_lua.py

A window will pop up. Select the main folder that holds all your individual vehicle resource folders.

The script will finish, and two new files will appear in the folder you selected:

vehicles.lua: Your ready-to-use vehicle configuration file.

vehicle_pack_log.lua: A reference of which vehicle spawn name came from which resource folder.

Tested on folder structure:

[cars]/
└── civcars/
    ├── data/
    │   ├── vehicle1/
    │   │   ├── carcols.meta
    │   │   ├── carvariations.meta
    │   │   ├── handling.meta
    │   │   └── vehicles.meta
    │   ├── vehicle2/
    │   │   ├── carcols.meta
    │   │   ├── carvariations.meta
    │   │   ├── handling.meta
    │   │   └── vehicles.meta
    ├── stream/
    │   └── carfiles/
    │       ├── vehicle1.yft
    │       ├── vehicle1_hi.yft
    │       ├── vehicle1.ytd
    │       ├── vehicle2.yft
    │       ├── vehicle2_hi.yft
    │       └── vehicle2.ytd
    └── fxmanifest.lua
    emergencycars/
    ├── data/
    │   ├── vehicle1/
    │   │   ├── carcols.meta
    │   │   ├── carvariations.meta
    │   │   ├── handling.meta
    │   │   └── vehicles.meta
    │   ├── vehicle2/
    │   │   ├── carcols.meta
    │   │   ├── carvariations.meta
    │   │   ├── handling.meta
    │   │   └── vehicles.meta
    ├── stream/
    │   └── carfiles/
    │       ├── vehicle1.yft
    │       ├── vehicle1_hi.yft
    │       ├── vehicle1.ytd
    │       ├── vehicle2.yft
    │       ├── vehicle2_hi.yft
    │       └── vehicle2.ytd
    └── fxmanifest.lua
