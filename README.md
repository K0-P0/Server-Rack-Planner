Website so you dont have to download this: https://serverbuild.kopo.click

# Server Rack Planner Web

A lightweight, secure, and fully client-side tool for planning server rack layouts. Visualize your homelab or enterprise setup with drag-and-drop simplicity.

[https://imgur.com/a/dfat1S8](https://imgur.com/a/dfat1S8#EbucUmr)

## ⚠️ SECURITY WARNING ⚠️

**ONLY USE TRUSTED .JSON FILES FOR THE APP AND FOR THE WEB CLIENT VERSION!!!**

This tool runs entirely in your browser. While this provides great privacy, importing malicious JSON files from untrusted sources could theoretically execute scripts in your browser. **Always verify the source of the component lists you download.**

---

## 🚀 Features

* **100% Client-Side:** No data is sent to any server. Your layout stays in your browser.
* **Drag & Drop:** Easily move components between the library and the rack.
* **Dual View:** Plan both the **Front** and **Rear** of your rack independently.
* **Capacity Planning:** Automatic calculation of total **Power (Watts)** and **Weight (kg)**.
* **Custom Libraries:** Create your own components or import bulk lists via JSON.
* **Rack Sizes:** Support for 6U, 9U, 12U, 15U, 18U, 20U, 24U, 30U, 42U, and 48U racks.
* **Export:** Save your entire project or export individual custom components to share.

## 🛠️ How to Use

### 1. Adding Components
* **Library:** Drag items from the left sidebar onto the rack.
* **Custom Items:** Click **"Create Custom Item"** to define a specific device (Name, U-Size, Color, Power, Weight).

### 2. Managing the Rack
* **Move:** Left Click + Drag an item to move it.
* **Delete:** Right Click an item to remove it.
* **Views:** Click "Switch View" to toggle between Front and Rear rails.

### 3. Importing Component Lists
You can populate your library by importing JSON files.
1.  Click **Import JSON List**.
2.  Select one or multiple `.json` files.
3.  **Pro Tip:** You can also **Drag & Drop** JSON files directly onto the "Library" sidebar.

Check the `json_libraries` folder in this repository for pre-made lists (Ubiquiti, Dell, Synology, etc.).

## 📦 How to Self-Host

Since the entire application is a single `index.html` file, it is incredibly easy to host.

### Option 1: Docker (Recommended)
Create a `docker-compose.yml` file:

```yaml
version: '3'
services:
  rack-planner:
    image: nginx:alpine
    container_name: rack_planner
    restart: unless-stopped
    volumes:
      - ./index.html:/usr/share/nginx/html/index.html:ro
    ports:
      - "8080:80"
