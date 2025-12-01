<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ServerRack Planner Web</title>
    <style>
        :root {
            --bg-color: #2e2e2e;
            --panel-color: #3c3c3c;
            --text-color: #ffffff;
            --accent-color: #2196f3;
            --link-color: #64b5f6;
        }

        body {
            margin: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* --- LAYOUT --- */
        #palette {
            width: 260px;
            background-color: var(--panel-color);
            display: flex;
            flex-direction: column;
            border-right: 1px solid #555;
            padding: 15px;
            transition: background-color 0.3s;
            position: relative;
        }

        #palette.highlight {
            background-color: #3d4c3d;
            border-right: 2px dashed #4CAF50;
        }
        #palette.highlight::after {
            content: "Drop JSON Files Here";
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            color: #fff;
            font-weight: bold;
            font-size: 1.2em;
            pointer-events: none;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }

        #main-area {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            overflow-y: auto;
            padding: 30px;
            background-color: #1e1e1e;
        }

        #controls {
            width: 240px;
            background-color: var(--panel-color);
            border-left: 1px solid #555;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        /* --- PALETTE ITEMS --- */
        .category-header {
            color: #4FC3F7;
            font-weight: 700;
            margin-top: 20px;
            margin-bottom: 8px;
            text-transform: uppercase;
            font-size: 0.8em;
            letter-spacing: 1px;
            border-bottom: 1px solid #555;
            padding-bottom: 4px;
        }
        
        .palette-item {
            background-color: #505050;
            padding: 10px;
            margin-bottom: 6px;
            border-radius: 6px;
            cursor: grab;
            user-select: none;
            font-size: 0.9em;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.1s, background-color 0.2s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        .palette-item:hover { background-color: #606060; transform: translateX(2px); }
        .palette-item:active { cursor: grabbing; transform: scale(0.98); }

        #search-bar {
            background: #2b2b2b;
            border: 1px solid #555;
            padding: 10px;
            color: white;
            border-radius: 6px;
            width: 100%;
            margin-bottom: 10px;
            box-sizing: border-box;
            font-size: 0.95em;
        }
        #search-bar:focus { outline: 2px solid var(--accent-color); border-color: transparent; }

        /* --- CANVAS --- */
        #rack-container {
            position: relative;
            margin-top: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border-radius: 4px;
            overflow: hidden;
        }

        canvas {
            display: block;
            background-color: #282828;
        }

        /* --- BUTTONS --- */
        button, .btn-link {
            padding: 12px;
            border: none;
            border-radius: 6px;
            color: white;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 0.9em;
            box-sizing: border-box;
            width: 100%;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        button:hover, .btn-link:hover { filter: brightness(1.15); transform: translateY(-1px); }
        button:active { transform: translateY(1px); }
        
        .btn-purple { background-color: #7E57C2; }
        .btn-green { background-color: #66BB6A; }
        .btn-orange { background-color: #FFA726; color: #333; }
        .btn-red { background-color: #EF5350; }
        .btn-blue { background-color: #42A5F5; }
        .btn-dark { background-color: #424242; border: 1px solid #666; }
        .btn-paypal { background-color: #0070BA; }

        .helper-link {
            font-size: 0.8em;
            color: var(--link-color);
            text-align: center;
            margin-top: 15px; 
            margin-bottom: 5px;
            cursor: pointer;
            text-decoration: underline;
            display: block;
        }
        .helper-link:hover { color: #90CAF9; }

        /* --- STATS --- */
        .stats-box {
            background-color: #252525;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 12px;
            margin-top: auto; 
        }
        .stat-line { margin: 6px 0; font-size: 0.9em; display: flex; justify-content: space-between; }

        /* --- MODALS --- */
        .modal {
            display: none; 
            position: fixed; 
            z-index: 1000; 
            left: 0;
            top: 0;
            width: 100%; 
            height: 100%; 
            background-color: rgba(0,0,0,0.8); 
            backdrop-filter: blur(4px);
        }
        .modal-content {
            background-color: #333;
            margin: 5% auto; 
            padding: 25px;
            border: 1px solid #555;
            width: 500px;
            max-width: 90%;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.6);
            position: relative;
            animation: modalFadeIn 0.3s;
        }
        @keyframes modalFadeIn { from {opacity: 0; transform: translateY(-20px);} to {opacity: 1; transform: translateY(0);} }

        .close-btn {
            color: #aaa;
            float: right;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
            transition: color 0.2s;
        }
        .close-btn:hover { color: white; }
        
        .modal h2 { margin-top: 0; color: var(--accent-color); border-bottom: 1px solid #555; padding-bottom: 10px; }
        .modal h3 { color: #eee; margin-bottom: 5px; font-size: 1.1em; }
        
        .modal label { display: block; margin-top: 15px; font-size: 0.9em; color: #ccc; }
        .modal input[type="text"], .modal input[type="number"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            background: #222;
            border: 1px solid #555;
            color: white;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .modal input[type="color"] {
            width: 100%;
            height: 40px;
            border: none;
            margin-top: 5px;
            cursor: pointer;
            border-radius: 4px;
        }
        
        .modal-actions {
            margin-top: 25px;
            display: flex;
            gap: 15px;
        }

        .shortcut-list {
            list-style: none;
            padding: 0;
        }
        .shortcut-list li {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #444;
        }
        .shortcut-list li:last-child { border-bottom: none; }
        .key-badge {
            background: #555;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.9em;
            border: 1px solid #777;
        }

        .github-box {
            background: #222;
            border: 1px solid #444;
            padding: 15px;
            border-radius: 6px;
            margin-top: 15px;
            text-align: center;
        }
        .github-box p { margin: 0 0 10px 0; color: #ccc; font-size: 0.9em; }

        /* Credits Footer Link */
        .credits-link {
            text-align: center; 
            margin-top: 15px; 
            font-size: 0.8em; 
            color: #666;
            cursor: pointer;
            transition: color 0.2s;
        }
        .credits-link:hover { color: #999; text-decoration: underline; }

    </style>
</head>
<body>

    <div id="palette">
        <h3 style="margin-top:0;">Library</h3>
        <input type="text" id="search-bar" placeholder="Search components..." oninput="app.filterPalette()">
        
        <div style="font-size:0.8em; color:#888; text-align:center; margin-bottom:15px; margin-top: 5px;">
            Drag & Drop JSON files here
        </div>
        
        <div id="palette-list" style="overflow-y: auto; flex-grow: 1; padding-right: 5px;"></div>
    </div>

    <div id="main-area">
        <h2 id="view-label" style="color:#ddd; margin-top:0;">Rack View: Front</h2>
        <div id="rack-container">
            <canvas id="rackCanvas" width="360" height="600" oncontextmenu="return false;"></canvas>
        </div>
    </div>

    <div id="controls">
        <div>
            <label style="font-size:0.85em; color:#aaa; font-weight:bold;">RACK HEIGHT</label>
            <select id="rack-size-select" onchange="app.resizeRack()" style="width:100%; padding:8px; margin-top:5px; background:#2b2b2b; color:white; border:1px solid #555; border-radius:4px;">
                <option value="9">9U</option>
                <option value="12" selected>12U</option>
                <option value="15">15U</option>
                <option value="18">18U</option>
                <option value="20">20U</option>
                <option value="24">24U</option>
                <option value="28">28U</option>
                <option value="30">30U</option>
                <option value="32">32U</option>
                <option value="34">34U</option>
                <option value="38">38U</option>
                <option value="40">40U</option>
                <option value="42">42U</option>
            </select>
        </div>

        <button class="btn-purple" onclick="app.toggleView()">Switch View (Front/Rear)</button>
        
        <div style="height:1px; background:#444; margin: 5px 0;"></div>
        
        <button class="btn-blue" onclick="app.openCreator()">➕ Create Custom Item</button>
        
        <div>
            <button class="btn-green" onclick="document.getElementById('file-input').click()">Import JSON List</button>
            <div class="helper-link" onclick="window.open('https://github.com/K0-P0/Server-Rack-Planner', '_blank')">
                Need parts? Get them on GitHub ↗
            </div>
        </div>
        <input type="file" id="file-input" style="display: none;" accept=".json" multiple onchange="app.importCustomList(this)">
        
        <button class="btn-orange" onclick="app.saveProject()">Save Project</button>
        <button class="btn-orange" onclick="document.getElementById('project-input').click()">Load Project</button>
        <input type="file" id="project-input" style="display: none;" accept=".json" onchange="app.loadProject(this)">
        
        <button class="btn-red" onclick="app.clearRack()">Clear Rack</button>
        
        <div class="stats-box">
            <div class="stat-line"><span style="color:#aaa">Used:</span> <span id="stat-used" style="font-weight:bold;">0 U</span></div>
            <div class="stat-line"><span style="color:#aaa">Power:</span> <span id="stat-power" style="color:#FFD54F; font-weight:bold;">0 W</span></div>
            <div class="stat-line"><span style="color:#aaa">Weight:</span> <span id="stat-weight" style="color:#81C784; font-weight:bold;">0 kg</span></div>
        </div>

        <button class="btn-dark" onclick="app.openHelp()">❓ Help & Shortcuts</button>
        
        <div class="credits-link" onclick="app.openAbout()">
            Built by KOPO
        </div>
    </div>

    <div id="createModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="app.closeCreator()">&times;</span>
            <h2>Create Custom Component</h2>
            
            <label>Component Name</label>
            <input type="text" id="new-name" placeholder="e.g. Custom Server">
            
            <div style="display:flex; gap:15px;">
                <div style="flex:1">
                    <label>Size (U)</label>
                    <input type="number" id="new-size" value="1" min="1" max="42">
                </div>
                <div style="flex:1">
                    <label>Color</label>
                    <input type="color" id="new-color" value="#2196f3">
                </div>
            </div>
            
            <div style="display:flex; gap:15px;">
                <div style="flex:1">
                    <label>Power (W)</label>
                    <input type="number" id="new-watts" value="0">
                </div>
                <div style="flex:1">
                    <label>Weight (kg)</label>
                    <input type="number" id="new-weight" value="0">
                </div>
            </div>

            <div class="modal-actions">
                <button class="btn-green" onclick="app.saveCustomItem()">Add to Library</button>
                <button class="btn-purple" onclick="app.exportSingleItem()">Export as JSON</button>
            </div>
        </div>
    </div>

    <div id="helpModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="app.closeHelp()">&times;</span>
            <h2>Help & Resources</h2>
            
            <div class="github-box">
                <p>Looking for component lists?</p>
                <button class="btn-dark" onclick="window.open('https://github.com/K0-P0/Server-Rack-Planner', '_blank')">
                    🐱 Download JSON Files from GitHub
                </button>
            </div>

            <h3>Controls</h3>
            <ul class="shortcut-list">
                <li><span>Move Item</span> <span class="key-badge">Left Click + Drag</span></li>
                <li><span>Delete Item</span> <span class="key-badge">Right Click</span></li>
                <li><span>Import Files</span> <span class="key-badge">Drag & Drop JSON</span></li>
            </ul>

            <h3>Tips</h3>
            <ul style="color:#ccc; font-size:0.9em; padding-left:20px;">
                <li>You can select multiple files at once when importing.</li>
                <li>Items in the "Front" view are separate from the "Rear" view.</li>
                <li>Projects save everything: your rack, your views, and your imported libraries.</li>
            </ul>

            <div style="margin-top: 20px; text-align: center; border-top: 1px solid #444; padding-top: 15px;">
                <p style="color:#aaa; font-size:0.9em; margin-bottom:10px;">Find this tool useful?</p>
                <a href="https://paypal.me/DekodaCaldwell" target="_blank" class="btn-link btn-paypal">
                    💙 Donate via PayPal
                </a>
            </div>
        </div>
    </div>

    <div id="aboutModal" class="modal">
        <div class="modal-content" style="text-align:center;">
            <span class="close-btn" onclick="app.closeAbout()">&times;</span>
            <h2 style="border:none; margin-bottom:10px;">ServerRack Planner</h2>
            <p style="font-size:1.1em; color:#ddd;">Built with ❤️ by <strong>KOPO</strong></p>
            <p style="color:#aaa; font-size:0.9em; margin-bottom:20px;">A lightweight, secure tool for homelab enthusiasts.</p>
            
            <button class="btn-dark" style="width:auto; padding:10px 30px;" onclick="window.open('https://github.com/K0-P0', '_blank')">
                Check out my GitHub
            </button>
        </div>
    </div>

<script>
/**
 * RACK PLANNER WEB - Final Polished
 */

const U_PIXELS = 40;
const RACK_LEFT_MARGIN = 40;
const RACK_RIGHT_MARGIN = 320; 
const CANVAS_WIDTH = 360;

// Default Data
const defaultCategories = {
    "Networking": {
        "UDM Pro": {size: 1, color: "#e0e0e0", watts: 50, weight: 4},
        "Switch 24 PoE": {size: 1, color: "#e0e0e0", watts: 250, weight: 3},
        "Patch Panel": {size: 1, color: "#333333", watts: 0, weight: 1}
    },
    "Servers": {
        "Dell R740 (2U)": {size: 2, color: "#212121", watts: 750, weight: 28},
        "1U Generic Server": {size: 1, color: "#4CAF50", watts: 300, weight: 15}
    },
    "Power": {
        "UPS 1500VA": {size: 2, color: "#3e2723", watts: 50, weight: 25},
        "PDU": {size: 1, color: "#F44336", watts: 0, weight: 2}
    },
    "Custom": {} 
};

class RackApp {
    constructor() {
        this.canvas = document.getElementById('rackCanvas');
        this.ctx = this.canvas.getContext('2d');
        
        this.rackHeight = 12; 
        this.categories = JSON.parse(JSON.stringify(defaultCategories));
        
        this.views = { "Front": [], "Rear": [] };
        this.currentView = "Front";
        
        this.isDragging = false;
        this.draggedItem = null; 
        
        this.setupCanvasEvents();
        this.setupDragAndDrop();
        this.renderPalette();
        this.draw();

        window.onclick = (event) => {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = "none";
            }
        }
    }

    draw() {
        this.canvas.height = this.rackHeight * U_PIXELS;
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        ctx.fillStyle = "#282828";
        ctx.fillRect(0, 0, w, h);

        ctx.lineWidth = 1;
        ctx.strokeStyle = "#444";
        ctx.fillStyle = "#888";
        ctx.font = "12px Segoe UI, Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        const labelX = (this.currentView === "Front") ? 20 : 340;

        for (let i = 0; i < this.rackHeight; i++) {
            let y = i * U_PIXELS;
            
            ctx.beginPath(); ctx.moveTo(RACK_LEFT_MARGIN, y); ctx.lineTo(RACK_RIGHT_MARGIN, y); ctx.stroke();
            let uNum = this.rackHeight - i;
            ctx.fillText(uNum + "U", labelX, y + U_PIXELS/2);

            ctx.fillStyle = "#111";
            for(let j=1; j<=3; j++) {
                let hy = y + (j * U_PIXELS / 4);
                ctx.beginPath(); ctx.arc(RACK_LEFT_MARGIN + 6, hy, 2, 0, Math.PI*2); ctx.fill();
                ctx.beginPath(); ctx.arc(RACK_RIGHT_MARGIN - 6, hy, 2, 0, Math.PI*2); ctx.fill();
            }
            ctx.fillStyle = "#888"; 
        }

        ctx.strokeStyle = "#555";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(RACK_LEFT_MARGIN, 0); ctx.lineTo(RACK_LEFT_MARGIN, h);
        ctx.moveTo(RACK_RIGHT_MARGIN, 0); ctx.lineTo(RACK_RIGHT_MARGIN, h);
        ctx.stroke();

        this.views[this.currentView].forEach(comp => this.drawComponent(comp));

        if (this.isDragging && this.draggedItem && this.draggedItem.currentSlot) {
            this.drawGhost(this.draggedItem);
        }

        this.updateStats();
    }

    drawComponent(comp) {
        let topIndex = this.rackHeight - (comp.startU + comp.size - 1);
        let y = topIndex * U_PIXELS;
        let height = comp.size * U_PIXELS;
        let width = RACK_RIGHT_MARGIN - RACK_LEFT_MARGIN;

        this.ctx.fillStyle = comp.color;
        this.ctx.fillRect(RACK_LEFT_MARGIN + 2, y + 1, width - 4, height - 2);
        this.ctx.strokeStyle = "#333";
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(RACK_LEFT_MARGIN + 2, y + 1, width - 4, height - 2);

        this.ctx.fillStyle = this.getContrastColor(comp.color);
        this.ctx.font = "bold 12px Segoe UI, Arial";
        this.ctx.fillText(comp.name, (RACK_LEFT_MARGIN + RACK_RIGHT_MARGIN)/2, y + height/2);
    }

    drawGhost(item) {
        let topIndex = this.rackHeight - (item.currentSlot + item.size - 1);
        let y = topIndex * U_PIXELS;
        let height = item.size * U_PIXELS;
        let width = RACK_RIGHT_MARGIN - RACK_LEFT_MARGIN;

        this.ctx.globalAlpha = 0.5;
        this.ctx.fillStyle = item.color;
        this.ctx.fillRect(RACK_LEFT_MARGIN, y, width, height);
        this.ctx.globalAlpha = 1.0;
        
        let isValid = this.checkAvailability(item.currentSlot, item.size);
        this.ctx.strokeStyle = isValid ? "#00FF00" : "#FF0000";
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(RACK_LEFT_MARGIN, y, width, height);
    }

    checkAvailability(startU, size) {
        if(startU < 1) return false;
        if(startU + size - 1 > this.rackHeight) return false;

        for(let comp of this.views[this.currentView]) {
            let sA = startU; 
            let eA = startU + size - 1;
            let sB = comp.startU; 
            let eB = comp.startU + comp.size - 1;
            if(sA <= eB && eA >= sB) return false;
        }
        return true;
    }

    // --- EVENTS ---

    setupCanvasEvents() {
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        window.addEventListener('mousemove', (e) => this.onMouseMove(e));
        window.addEventListener('mouseup', (e) => this.onMouseUp(e));
    }

    setupDragAndDrop() {
        const palette = document.getElementById('palette');
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            palette.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });
        palette.addEventListener('dragover', () => palette.classList.add('highlight'), false);
        palette.addEventListener('dragleave', () => palette.classList.remove('highlight'), false);
        palette.addEventListener('drop', (e) => {
            palette.classList.remove('highlight');
            const dt = e.dataTransfer;
            const files = dt.files;
            this.handleFiles(files);
        }, false);
    }

    startDragFromPalette(name, size, color, watts, weight) {
        this.isDragging = true;
        this.draggedItem = { 
            name, size, color, watts, weight, 
            isNew: true, 
            currentSlot: null,
            originalSlot: null
        };
    }

    onMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        if(x < RACK_LEFT_MARGIN || x > RACK_RIGHT_MARGIN) return;

        const clickedIndex = this.views[this.currentView].findIndex(c => {
             let topIndex = this.rackHeight - (c.startU + c.size - 1);
             let cy = topIndex * U_PIXELS;
             let ch = c.size * U_PIXELS;
             return (y >= cy && y <= cy + ch);
        });

        if(clickedIndex !== -1) {
            const clickedItem = this.views[this.currentView][clickedIndex];
            if(e.button === 2) { 
                if(confirm(`Remove ${clickedItem.name}?`)) {
                    this.views[this.currentView].splice(clickedIndex, 1);
                    this.draw();
                }
                return;
            }
            if(e.button === 0) { 
                this.views[this.currentView].splice(clickedIndex, 1);
                this.isDragging = true;
                this.draggedItem = {
                    ...clickedItem,
                    isNew: false,
                    originalSlot: clickedItem.startU,
                    currentSlot: clickedItem.startU
                };
                this.draw();
            }
        }
    }

    onMouseMove(e) {
        if(!this.isDragging) return;
        const rect = this.canvas.getBoundingClientRect();
        const y = e.clientY - rect.top;

        if(y >= 0 && y <= rect.height) {
            let indexTop = Math.floor(y / U_PIXELS);
            let potentialStartU = this.rackHeight - (indexTop + this.draggedItem.size - 1);
            this.draggedItem.currentSlot = potentialStartU;
            this.draw();
        } else {
            this.draggedItem.currentSlot = null;
            this.draw();
        }
    }

    onMouseUp(e) {
        if(!this.isDragging) return;
        let dropped = false;

        if(this.draggedItem && this.draggedItem.currentSlot) {
            const slot = this.draggedItem.currentSlot;
            const size = this.draggedItem.size;
            if(this.checkAvailability(slot, size)) {
                this.views[this.currentView].push({
                    name: this.draggedItem.name,
                    size: this.draggedItem.size,
                    color: this.draggedItem.color,
                    watts: this.draggedItem.watts,
                    weight: this.draggedItem.weight,
                    startU: slot
                });
                dropped = true;
            }
        }
        if(!dropped && !this.draggedItem.isNew) {
            this.views[this.currentView].push({
                name: this.draggedItem.name,
                size: this.draggedItem.size,
                color: this.draggedItem.color,
                watts: this.draggedItem.watts,
                weight: this.draggedItem.weight,
                startU: this.draggedItem.originalSlot
            });
        }
        
        this.isDragging = false;
        this.draggedItem = null;
        this.draw();
    }

    // --- UI HELPERS ---

    renderPalette() {
        const list = document.getElementById('palette-list');
        list.innerHTML = "";
        const search = document.getElementById('search-bar').value.toLowerCase();

        for (const [catName, items] of Object.entries(this.categories)) {
            if (Object.keys(items).length === 0 && catName !== "Custom") continue; 

            const matches = Object.entries(items).filter(([name]) => name.toLowerCase().includes(search));
            if(matches.length === 0 && catName !== "Custom") continue;

            const header = document.createElement('div');
            header.className = 'category-header';
            header.innerText = catName;
            list.appendChild(header);

            matches.forEach(([name, data]) => {
                const div = document.createElement('div');
                div.className = 'palette-item';
                div.style.borderLeft = `4px solid ${data.color}`;
                div.innerHTML = `<span>${name}</span> <span>${data.size}U</span>`;
                div.addEventListener('mousedown', (e) => {
                    e.preventDefault(); 
                    this.startDragFromPalette(name, data.size, data.color, data.watts, data.weight);
                });
                list.appendChild(div);
            });
        }
    }

    filterPalette() { this.renderPalette(); }

    toggleView() {
        this.currentView = (this.currentView === "Front") ? "Rear" : "Front";
        document.getElementById('view-label').innerText = `Rack View: ${this.currentView}`;
        this.draw();
    }

    resizeRack() {
        this.rackHeight = parseInt(document.getElementById('rack-size-select').value);
        this.draw();
    }

    clearRack() {
        if(confirm("Clear current view?")) {
            this.views[this.currentView] = [];
            this.draw();
        }
    }

    updateStats() {
        let occupied = new Set();
        this.views[this.currentView].forEach(c => {
            for(let i=0; i<c.size; i++) occupied.add(c.startU + i);
        });
        document.getElementById('stat-used').innerText = `${occupied.size} U`;

        let w = 0, kg = 0;
        Object.values(this.views).flat().forEach(c => {
            w += (c.watts || 0);
            kg += (c.weight || 0);
        });
        document.getElementById('stat-power').innerText = `${w} W`;
        document.getElementById('stat-weight').innerText = `${kg.toFixed(1)} kg`;
    }

    getContrastColor(hex) {
        if(!hex) return 'black';
        hex = hex.replace("#", "");
        var r = parseInt(hex.substr(0,2),16);
        var g = parseInt(hex.substr(2,2),16);
        var b = parseInt(hex.substr(4,2),16);
        var yiq = ((r*299)+(g*587)+(b*114))/1000;
        return (yiq >= 128) ? 'black' : 'white';
    }

    // --- CREATOR ---
    openCreator() { document.getElementById('createModal').style.display = "block"; }
    closeCreator() { document.getElementById('createModal').style.display = "none"; }

    saveCustomItem() {
        const name = document.getElementById('new-name').value.trim();
        const size = parseInt(document.getElementById('new-size').value);
        const color = document.getElementById('new-color').value;
        const watts = parseInt(document.getElementById('new-watts').value) || 0;
        const weight = parseFloat(document.getElementById('new-weight').value) || 0;

        if(!name) { alert("Please enter a name"); return; }
        if(!this.categories["Custom"]) this.categories["Custom"] = {};

        this.categories["Custom"][name] = { size, color, watts, weight };
        this.renderPalette();
        this.closeCreator();
        
        document.getElementById('new-name').value = "";
        document.getElementById('new-watts').value = 0;
        document.getElementById('new-weight').value = 0;
    }

    exportSingleItem() {
        const name = document.getElementById('new-name').value.trim();
        if(!name) { alert("Please enter a name to export"); return; }
        const size = parseInt(document.getElementById('new-size').value);
        const color = document.getElementById('new-color').value;
        const watts = parseInt(document.getElementById('new-watts').value) || 0;
        const weight = parseFloat(document.getElementById('new-weight').value) || 0;
        const data = { [name]: { size, color, watts, weight } };
        const blob = new Blob([JSON.stringify(data, null, 2)], {type: "application/json"});
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `${name}.json`;
        link.click();
    }

    // --- IMPORT/EXPORT ---
    importCustomList(input) {
        const files = input.files;
        this.handleFiles(files);
        input.value = ''; 
    }

    handleFiles(files) {
        if(!files || files.length === 0) return;
        let loadedCount = 0;
        Array.from(files).forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const json = JSON.parse(e.target.result);
                    const name = file.name.replace(".json", "");
                    this.categories[name] = json;
                    loadedCount++;
                    if(loadedCount === files.length) {
                        this.renderPalette();
                    }
                } catch(err) { console.error("Bad JSON", file.name); }
            };
            reader.readAsText(file);
        });
    }

    saveProject() {
        const data = {
            version: "Web-1.0",
            rackHeight: this.rackHeight,
            views: this.views,
            categories: this.categories
        };
        const blob = new Blob([JSON.stringify(data, null, 2)], {type: "application/json"});
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "my-rack-project.json";
        link.click();
    }

    loadProject(input) {
        const file = input.files[0];
        if(!file) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                this.rackHeight = data.rackHeight || 12;
                this.views = data.views || {Front:[], Rear:[]};
                if(data.categories) this.categories = data.categories;
                document.getElementById('rack-size-select').value = this.rackHeight;
                this.currentView = "Front"; 
                document.getElementById('view-label').innerText = "Rack View: Front";
                this.renderPalette();
                this.draw();
            } catch(err) { alert("Error loading project"); }
        };
        reader.readAsText(file);
    }

    // Modal Logic
    openHelp() { document.getElementById('helpModal').style.display = "block"; }
    closeHelp() { document.getElementById('helpModal').style.display = "none"; }
    openAbout() { document.getElementById('aboutModal').style.display = "block"; }
    closeAbout() { document.getElementById('aboutModal').style.display = "none"; }
    openCreator() { document.getElementById('createModal').style.display = "block"; }
    closeCreator() { document.getElementById('createModal').style.display = "none"; }
}

try {
    const app = new RackApp();
    window.app = app; 
} catch (e) {
    alert("Error initializing App: " + e);
}

</script>
</body>
</html>
