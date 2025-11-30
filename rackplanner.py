#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog, colorchooser
import json
import copy
import os
from PIL import ImageGrab, Image

U_HEIGHT = 40
DEFAULT_U = 12
RACK_WIDTH_PX = 280
RACK_LEFT_MARGIN = 30
RACK_RIGHT_MARGIN = RACK_LEFT_MARGIN + RACK_WIDTH_PX
PALETTE_WIDTH_PX = 230

class RackPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RackPlanner Pro")
        self.root.configure(bg='#2e2e2e')
        
        self.rack_height = DEFAULT_U
        self.rack_items = [None] * self.rack_height
        
        self.views = {
            "Front": [],
            "Rear": []
        }
        self.current_view = "Front"
        self.placed_components_data = self.views[self.current_view]

        self._dragging_component = None
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._drag_highlight_rects = []
        self._ghost_rect_id = None
        self._ghost_text_id = None

        self._history = []
        self._history_index = -1
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_palette_filtered)

        self.default_categories = {
            "Networking": {
                "UDM Pro": {"size": 1, "color": "#FFC107", "watts": 50, "weight": 4},
                "Router": {"size": 1, "color": "#FFC107", "watts": 30, "weight": 2},
                "Managed Switch": {"size": 1, "color": "#FFC107", "watts": 60, "weight": 4},
                "PoE Switch": {"size": 1, "color": "#FFC107", "watts": 350, "weight": 5}
            },
            "Servers": {
                "1U Server": {"size": 1, "color": "#4CAF50", "watts": 250, "weight": 15},
                "2U Server": {"size": 2, "color": "#4CAF50", "watts": 500, "weight": 25},
                "4U Server": {"size": 4, "color": "#4CAF50", "watts": 900, "weight": 45}
            },
            "Storage": {
                "Disk Shelf": {"size": 3, "color": "#9E9E9E", "watts": 300, "weight": 30},
                "NAS Appliance": {"size": 2, "color": "#9E9E9E", "watts": 100, "weight": 10}
            },
            "Power": {
                "UPS": {"size": 2, "color": "#F44336", "watts": 50, "weight": 30},
                "PDU": {"size": 1, "color": "#F44336", "watts": 0, "weight": 2}
            },
            "Accessories": {
                "Patch Panel": {"size": 1, "color": "#8BC34A", "watts": 0, "weight": 1},
                "Cable Management": {"size": 1, "color": "#8BC34A", "watts": 0, "weight": 0.5},
                "2U Shelf": {"size": 2, "color": "#8BC34A", "watts": 0, "weight": 3}
            },
            "Cooling": {
                "Fan Unit": {"size": 1, "color": "#00BCD4", "watts": 40, "weight": 2}
            },
            "Custom": {}
        }
        
        self.component_categories = copy.deepcopy(self.default_categories)

        self.setup_ui()
        self._draw_rack_and_components()
        self._record_current_state()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#2e2e2e')
        main_frame.pack(fill=tk.BOTH, expand=True)

        palette_frame = tk.Frame(main_frame, bg='#3c3c3c', width=PALETTE_WIDTH_PX)
        palette_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        
        palette_label = tk.Label(palette_frame, text="Library", bg='#3c3c3c', fg='white', font=('Arial', 10, 'bold'))
        palette_label.pack(pady=(5,2))

        search_frame = tk.Frame(palette_frame, bg='#3c3c3c')
        search_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        tk.Label(search_frame, text="🔍", bg='#3c3c3c', fg='#aaaaaa').pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg='#555555', fg='white', insertbackground='white', relief=tk.FLAT)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.palette_scrollbar = tk.Scrollbar(palette_frame, orient="vertical")
        self.palette_scrollbar.pack(side="right", fill="y")

        self.palette_canvas = tk.Canvas(palette_frame, bg='#3c3c3c', highlightthickness=0, yscrollcommand=self.palette_scrollbar.set)
        self.palette_canvas.pack(fill=tk.BOTH, expand=True)
        self.palette_scrollbar.config(command=self.palette_canvas.yview)
        
        self.palette_inner_frame = tk.Frame(self.palette_canvas, bg='#3c3c3c')
        self.palette_canvas.create_window((0, 0), window=self.palette_inner_frame, anchor="nw", width=PALETTE_WIDTH_PX-20)
        self.palette_inner_frame.bind("<Configure>", lambda e: self.palette_canvas.configure(scrollregion = self.palette_canvas.bbox("all")))

        self.palette_canvas.bind("<Button-4>", self._on_palette_mousewheel)
        self.palette_canvas.bind("<Button-5>", self._on_palette_mousewheel)
        self.palette_canvas.bind("<MouseWheel>", self._on_palette_mousewheel)

        canvas_container = tk.Frame(main_frame, bg='#1e1e1e')
        canvas_container.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.view_label = tk.Label(canvas_container, text=f"Rack View: {self.current_view}", bg='#1e1e1e', fg='#cccccc', font=('Arial', 12, 'bold'))
        self.view_label.pack(pady=(5,0))

        self.canvas = tk.Canvas(canvas_container, width=RACK_RIGHT_MARGIN + 40, bg='#1e1e1e', highlightthickness=0)
        self.canvas.pack(pady=10, expand=True)
        
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self._drop)

        controls = tk.Frame(main_frame, bg='#2e2e2e', width=200)
        controls.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        tk.Label(controls, text="Rack Size:", bg='#2e2e2e', fg='white').pack(anchor='w')
        self.rack_size_var = tk.IntVar(value=DEFAULT_U)
        size_options = [4, 6, 9, 12, 15, 18, 20, 24, 26, 30, 32, 34, 38, 42, 45, 48]
        self.rack_size_menu = ttk.Combobox(controls, textvariable=self.rack_size_var, values=size_options, state='readonly')
        self.rack_size_menu.pack(fill=tk.X, pady=(0, 10))
        self.rack_size_menu.bind("<<ComboboxSelected>>", self.change_rack_size)

        self.view_btn = tk.Button(controls, text="Switch View (Front/Rear)", command=self.toggle_view, bg='#673AB7', fg='white')
        self.view_btn.pack(fill=tk.X, pady=(0, 10))

        tk.Button(controls, text="New Custom Item", command=self.add_custom_component, bg='#2196f3', fg='white').pack(fill=tk.X, pady=5)
        tk.Button(controls, text="Import List as Folder", command=self.import_custom_list, bg='#4CAF50', fg='white').pack(fill=tk.X, pady=2)
        
        tk.Frame(controls, height=5, bg='#2e2e2e').pack()

        tk.Button(controls, text="Clear Current View", command=self.clear_rack, bg='#f44336', fg='white').pack(fill=tk.X, pady=5)
        
        undo_redo_frame = tk.Frame(controls, bg='#2e2e2e')
        undo_redo_frame.pack(fill=tk.X, pady=5)
        self.undo_btn = tk.Button(undo_redo_frame, text="Undo", command=self.undo, bg='#607D8B', fg='white')
        self.undo_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,2))
        self.redo_btn = tk.Button(undo_redo_frame, text="Redo", command=self.redo, bg='#607D8B', fg='white')
        self.redo_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2,0))

        tk.Frame(controls, height=5, bg='#2e2e2e').pack()

        tk.Button(controls, text="Save Project", command=self.save_rack_config, bg='#ff9800', fg='white').pack(fill=tk.X, pady=5)
        tk.Button(controls, text="Load Project", command=self.load_rack_config, bg='#ff9800', fg='white').pack(fill=tk.X, pady=5)
        tk.Button(controls, text="Export Image", command=self.export_canvas_as_image, bg='#009688', fg='white').pack(fill=tk.X, pady=5)

        tk.Frame(controls, height=10, bg='#2e2e2e').pack()

        stats_frame = tk.LabelFrame(controls, text="Stats", bg='#2e2e2e', fg='white')
        stats_frame.pack(fill=tk.X, pady=10)
        self.used_u_label = tk.Label(stats_frame, text="Used: 0", bg='#2e2e2e', fg='white', anchor='w')
        self.used_u_label.pack(fill=tk.X, padx=5, pady=2)
        self.power_label = tk.Label(stats_frame, text="Power: 0 W", bg='#2e2e2e', fg='#FFD54F', anchor='w', font=('Arial', 9, 'bold'))
        self.power_label.pack(fill=tk.X, padx=5, pady=2)
        self.weight_label = tk.Label(stats_frame, text="Weight: 0 kg", bg='#2e2e2e', fg='#81C784', anchor='w', font=('Arial', 9, 'bold'))
        self.weight_label.pack(fill=tk.X, padx=5, pady=2)

        self.update_palette()
        self._update_undo_redo_buttons()

    def toggle_view(self):
        if self.current_view == "Front":
            self.current_view = "Rear"
        else:
            self.current_view = "Front"
        self.placed_components_data = self.views[self.current_view]
        self.view_label.config(text=f"Rack View: {self.current_view}")
        self._draw_rack_and_components()

    def update_palette_filtered(self, *args):
        self.update_palette()

    def update_palette(self):
        search_term = self.search_var.get().lower()

        for widget in self.palette_inner_frame.winfo_children():
            widget.destroy()

        for category_name, category_items in self.component_categories.items():
            matching_items = {k: v for k, v in category_items.items() if search_term in k.lower()}
            
            if not matching_items and search_term not in category_name.lower():
                continue
            
            items_to_show = matching_items if search_term else category_items
            if search_term and search_term in category_name.lower():
                items_to_show = category_items

            if items_to_show:
                header_fg = '#4FC3F7' if category_name not in self.default_categories else 'white'
                ttk.Label(self.palette_inner_frame, text=f"-- {category_name} --", foreground=header_fg) \
                    .pack(fill=tk.X, pady=(10,2))
                
                for comp_name, comp_info in items_to_show.items():
                    comp_size = comp_info['size']
                    comp_color = comp_info['color']
                    
                    palette_item_frame = tk.Frame(self.palette_inner_frame, bd=1, relief="solid", bg=comp_color)
                    palette_item_frame.pack(fill=tk.X, padx=5, pady=2)
                    
                    palette_label = tk.Label(palette_item_frame, text=f"{comp_name} ({comp_size}U)", 
                                             bg=comp_color, fg='black', font=('Arial', 9))
                    palette_label.pack(side=tk.LEFT, padx=5, pady=2)

                    handler = lambda e, n=comp_name, s=comp_size, c=comp_color, i=comp_info: \
                              self._place_component_from_palette(n, s, c, i)
                    
                    palette_item_frame.bind("<Button-1>", handler)
                    palette_label.bind("<Button-1>", handler)

        self.palette_inner_frame.update_idletasks()
        self.palette_canvas.configure(scrollregion=self.palette_canvas.bbox("all"))

    def _place_component_from_palette(self, comp_name, comp_size, comp_color, comp_info):
        placed = False
        self._sync_rack_items()
        
        for start_u_slot in range(1, self.rack_height - comp_size + 2):
            if self.is_slot_available(start_u_slot, comp_size):
                new_comp_data = {
                    'name': comp_name,
                    'start_u_slot': start_u_slot,
                    'size_u': comp_size,
                    'color': comp_color,
                    'watts': comp_info.get('watts', 0),
                    'weight': comp_info.get('weight', 0)
                }
                self.placed_components_data.append(new_comp_data)
                self._render_single_component(new_comp_data)
                self._sync_rack_items()
                self.update_stats()
                self._record_current_state()
                placed = True
                break
        
        if not placed:
            messagebox.showerror("No Space", f"Cannot place '{comp_name}' ({comp_size}U). No space available.")

    def _draw_rack_and_components(self):
        self.canvas.delete("all")
        self.rack_items = [None] * self.rack_height

        total_h = U_HEIGHT * self.rack_height
        self.canvas.config(height=total_h)

        self.canvas.create_rectangle(RACK_LEFT_MARGIN, 0, RACK_RIGHT_MARGIN, total_h, fill='#282828', outline='#555555', width=0)

        for i in range(self.rack_height):
            y = i * U_HEIGHT
            self.canvas.create_line(RACK_LEFT_MARGIN, y, RACK_RIGHT_MARGIN, y, fill='#444444', width=1)
            self.canvas.create_text(15, y + U_HEIGHT // 2, anchor='center', fill='#888888', text=f"{self.rack_height - i}")
            
            for j in [1, 2, 3]:
                hole_y = y + (j * U_HEIGHT / 4)
                self.canvas.create_oval(RACK_LEFT_MARGIN + 5, hole_y - 2, RACK_LEFT_MARGIN + 9, hole_y + 2, fill="#111111", outline="")
                self.canvas.create_oval(RACK_RIGHT_MARGIN - 9, hole_y - 2, RACK_RIGHT_MARGIN - 5, hole_y + 2, fill="#111111", outline="")

        self.canvas.create_line(RACK_LEFT_MARGIN, 0, RACK_LEFT_MARGIN, total_h, fill='#555555', width=2)
        self.canvas.create_line(RACK_RIGHT_MARGIN, 0, RACK_RIGHT_MARGIN, total_h, fill='#555555', width=2)
        self.canvas.create_line(RACK_LEFT_MARGIN, total_h, RACK_RIGHT_MARGIN, total_h, fill='#555555', width=1)

        for comp_data in self.placed_components_data:
            self._render_single_component(comp_data)
        
        self._sync_rack_items()
        self.update_stats()

    def _render_single_component(self, comp_data):
        start_index_0_based_top = self.rack_height - (comp_data['start_u_slot'] + comp_data['size_u'] - 1)
        y1 = start_index_0_based_top * U_HEIGHT
        y2 = y1 + comp_data['size_u'] * U_HEIGHT
        
        color_hex = comp_data.get('color', 'skyblue')
        
        if len(color_hex) == 7:
            r, g, b = int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16)
            text_color = 'white' if (0.299*r + 0.587*g + 0.114*b)/255 < 0.5 else 'black'
        else:
            text_color = 'black'

        rect = self.canvas.create_rectangle(RACK_LEFT_MARGIN + 2, y1 + 1, RACK_RIGHT_MARGIN - 2, y2 - 1, 
                                            fill=color_hex, outline='#333333', width=1, tags="component_item")
        text = self.canvas.create_text(RACK_LEFT_MARGIN + RACK_WIDTH_PX // 2, (y1 + y2) // 2, 
                                        fill=text_color, font=('Arial', 9, 'bold'), text=comp_data['name'], tags="component_item")

        comp_data['rect_id'] = rect
        comp_data['text_id'] = text

        self.canvas.tag_bind(rect, '<Button-3>', lambda e, data=comp_data: self.delete_component_on_click(e, data))
        self.canvas.tag_bind(text, '<Button-3>', lambda e, data=comp_data: self.delete_component_on_click(e, data))

    def _sync_rack_items(self):
        self.rack_items = [None] * self.rack_height
        for comp_data in self.placed_components_data:
            start_index_0_based_top = self.rack_height - (comp_data['start_u_slot'] + comp_data['size_u'] - 1)
            for i in range(start_index_0_based_top, start_index_0_based_top + comp_data['size_u']):
                if 0 <= i < self.rack_height:
                    self.rack_items[i] = comp_data['name']

    def update_stats(self):
        occupied_slots = set()
        for comp in self.placed_components_data:
            start_index_0_based_top = self.rack_height - (comp['start_u_slot'] + comp['size_u'] - 1)
            for i in range(start_index_0_based_top, start_index_0_based_top + comp['size_u']):
                if 0 <= i < self.rack_height:
                    occupied_slots.add(i)
        
        self.used_u_label.config(text=f"Used: {len(occupied_slots)}")
        
        total_watts = 0
        total_weight = 0
        for comp in self.views["Front"] + self.views["Rear"]:
            total_watts += comp.get('watts', 0)
            total_weight += comp.get('weight', 0)

        self.power_label.config(text=f"Power: {total_watts} W")
        self.weight_label.config(text=f"Weight: {total_weight} kg")

    def _record_current_state(self):
        current_state = {
            'rack_height': self.rack_height,
            'views': copy.deepcopy(self.views),
            'current_view_name': self.current_view
        }
        self._history = self._history[:self._history_index + 1]
        self._history.append(current_state)
        self._history_index = len(self._history) - 1
        self._update_undo_redo_buttons()

    def _load_state_from_history(self, state_data):
        self.rack_height = state_data['rack_height']
        self.rack_size_var.set(self.rack_height)
        self.views = copy.deepcopy(state_data['views'])
        self.current_view = state_data.get('current_view_name', 'Front')
        self.placed_components_data = self.views[self.current_view]
        self.view_label.config(text=f"Rack View: {self.current_view}")
        self._draw_rack_and_components()
        self._update_undo_redo_buttons()

    def _update_undo_redo_buttons(self):
        self.undo_btn.config(state=tk.NORMAL if self._history_index > 0 else tk.DISABLED)
        self.redo_btn.config(state=tk.NORMAL if self._history_index < len(self._history) - 1 else tk.DISABLED)

    def undo(self):
        if self._history_index > 0:
            self._history_index -= 1
            self._load_state_from_history(self._history[self._history_index])
    def redo(self):
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self._load_state_from_history(self._history[self._history_index])

    def _start_drag(self, event):
        self._dragging_component = None
        self._clear_highlights()
        self._clear_ghost()

        if event.widget == self.canvas:
            closest_item_ids = self.canvas.find_closest(event.x, event.y)
            if not closest_item_ids: return

            clicked_item_id = closest_item_ids[0]
            for comp_data in self.placed_components_data:
                if comp_data.get('rect_id') == clicked_item_id or comp_data.get('text_id') == clicked_item_id:
                    self._dragging_component = comp_data
                    
                    start_index_0_based_top = self.rack_height - (self._dragging_component['start_u_slot'] + self._dragging_component['size_u'] - 1)
                    for i in range(start_index_0_based_top, start_index_0_based_top + self._dragging_component['size_u']):
                        if 0 <= i < self.rack_height: self.rack_items[i] = None
                    
                    self.canvas.itemconfig(self._dragging_component['rect_id'], state='hidden')
                    self.canvas.itemconfig(self._dragging_component['text_id'], state='hidden')

                    original_coords = self.canvas.coords(comp_data['rect_id'])
                    x1, y1, x2, y2 = original_coords

                    self._ghost_rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=self._dragging_component['color'], outline='gray', stipple='gray50', width=2)
                    self._ghost_text_id = self.canvas.create_text((x1+x2)/2, (y1+y2)/2, fill='black', font=('Arial', 10, 'bold'), text=self._dragging_component['name'])
                    break
        
        if self._dragging_component:
            self._drag_start_x = event.x 
            self._drag_start_y = event.y

    def _drag_motion(self, event):
        if self._dragging_component:
            self._clear_highlights()
            target_u = int(event.y / U_HEIGHT)
            size_u = self._dragging_component['size_u']
            start_u = self.rack_height - (target_u + size_u - 1)
            start_u = max(1, min(start_u, self.rack_height - size_u + 1))
            
            is_valid = self.is_slot_available(start_u, size_u)

            snapped_top_y = (self.rack_height - (start_u + size_u - 1)) * U_HEIGHT
            self.canvas.coords(self._ghost_rect_id, RACK_LEFT_MARGIN, snapped_top_y, RACK_RIGHT_MARGIN, snapped_top_y + size_u * U_HEIGHT)
            self.canvas.coords(self._ghost_text_id, RACK_LEFT_MARGIN + RACK_WIDTH_PX // 2, snapped_top_y + (size_u * U_HEIGHT)/2)
            self._highlight_slots(start_u, size_u, is_valid)

    def _drop(self, event):
        if self._dragging_component:
            if not self._ghost_rect_id:
                self._cancel_drag()
                return

            ghost_y = self.canvas.coords(self._ghost_rect_id)[1]
            size_u = self._dragging_component['size_u']
            start_u = self.rack_height - (int(ghost_y / U_HEIGHT) + size_u - 1)
            start_u = max(1, min(start_u, self.rack_height - size_u + 1))

            if self.is_slot_available(start_u, size_u):
                self._dragging_component['start_u_slot'] = start_u
                self._draw_rack_and_components()
                self._record_current_state()
            else:
                self._cancel_drag()
            
            self._clear_highlights()
            self._clear_ghost()
            self._dragging_component = None

    def _cancel_drag(self):
        if self._dragging_component:
            self.canvas.itemconfig(self._dragging_component['rect_id'], state='normal')
            self.canvas.itemconfig(self._dragging_component['text_id'], state='normal')
            self._sync_rack_items()
            self._clear_highlights()
            self._clear_ghost()
            self._dragging_component = None

    def is_slot_available(self, start_u_slot, size_u):
        start_index = self.rack_height - (start_u_slot + size_u - 1)
        if start_index < 0 or start_index + size_u > self.rack_height: return False
        for i in range(start_index, start_index + size_u):
            if self.rack_items[i] is not None: return False
        return True
    
    def _highlight_slots(self, start_u_slot, size_u, is_valid):
        self._clear_highlights()
        color = '#A5D6A7' if is_valid else '#EF9A9A'
        start_index = max(0, self.rack_height - (start_u_slot + size_u - 1))
        end_index = min(self.rack_height, start_index + size_u)

        for i in range(start_index, end_index):
            y1 = i * U_HEIGHT
            self._drag_highlight_rects.append(self.canvas.create_rectangle(RACK_LEFT_MARGIN, y1, RACK_RIGHT_MARGIN, y1 + U_HEIGHT, fill=color, stipple='gray50', outline=color))
        if self._ghost_rect_id: self.canvas.tag_raise(self._ghost_rect_id); self.canvas.tag_raise(self._ghost_text_id)

    def _clear_highlights(self):
        for rect_id in self._drag_highlight_rects: self.canvas.delete(rect_id)
        self._drag_highlight_rects = []
    
    def _clear_ghost(self):
        if self._ghost_rect_id: self.canvas.delete(self._ghost_rect_id); self._ghost_rect_id = None
        if self._ghost_text_id: self.canvas.delete(self._ghost_text_id); self._ghost_text_id = None

    def _on_palette_mousewheel(self, event):
        if event.num == 4 or event.delta > 0: self.palette_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0: self.palette_canvas.yview_scroll(1, "units")

    def add_custom_component(self):
        name = simpledialog.askstring("New", "Component Name:")
        if not name: return
        size = simpledialog.askinteger("New", "Size (U):", minvalue=1, maxvalue=self.rack_height)
        if not size: return
        watts = simpledialog.askinteger("New", "Power (W):", minvalue=0, initialvalue=0) or 0
        weight = simpledialog.askfloat("New", "Weight (kg):", minvalue=0.0, initialvalue=0.0) or 0
        color = colorchooser.askcolor()[1] or 'skyblue'

        self.component_categories["Custom"][name] = {"size": size, "color": color, "watts": watts, "weight": weight}
        self.update_palette()

    def import_custom_list(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path: return

        category_name = os.path.splitext(os.path.basename(file_path))[0]

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                raise ValueError("JSON must be a dictionary.")

            self.component_categories[category_name] = data
            self.update_palette()
            messagebox.showinfo("Imported", f"Created new palette folder: {category_name}")
            
        except Exception as e:
            messagebox.showerror("Import Error", f"{e}")

    def save_rack_config(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path: return

        save_data = {
            "version": "3.0",
            "rack_height": self.rack_height,
            "views": self.views,
            "component_categories": self.component_categories
        }
        
        for view in save_data['views'].values():
            for c in view: c.pop('rect_id', None); c.pop('text_id', None)

        try:
            with open(file_path, 'w') as f: json.dump(save_data, f, indent=4)
            messagebox.showinfo("Saved", "Project saved.")
        except Exception as e: messagebox.showerror("Error", f"{e}")

    def load_rack_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path: return

        try:
            with open(file_path, 'r') as f: data = json.load(f)

            self.rack_height = data.get("rack_height", DEFAULT_U)
            self.rack_size_var.set(self.rack_height)
            
            if "component_categories" in data:
                self.component_categories = data["component_categories"]
            else:
                self.component_categories = copy.deepcopy(self.default_categories)
                if "custom_components" in data:
                    self.component_categories["Custom"] = data["custom_components"]

            self.update_palette()

            if "views" in data:
                self.views = data["views"]
            else:
                self.views = {"Front": data.get("placed_components", []), "Rear": []}
            
            self.current_view = "Front"
            self.placed_components_data = self.views[self.current_view]
            self.view_label.config(text=f"Rack View: {self.current_view}")
            
            self._draw_rack_and_components()
            self._record_current_state()
            messagebox.showinfo("Loaded", "Project loaded.")
        except Exception as e: messagebox.showerror("Error", f"{e}")

    def delete_component_on_click(self, event, component_data):
        if messagebox.askyesno("Delete", f"Delete '{component_data['name']}'?"):
            self.canvas.delete(component_data['rect_id'])
            self.canvas.delete(component_data['text_id'])
            self.placed_components_data.remove(component_data)
            self._draw_rack_and_components()
            self._record_current_state()

    def clear_rack(self):
        if messagebox.askyesno("Clear", f"Clear {self.current_view} view?"):
            self.placed_components_data.clear()
            self._draw_rack_and_components()
            self._record_current_state()

    def change_rack_size(self, event=None):
        new_height = self.rack_size_var.get()
        if new_height < self.rack_height:
             if not messagebox.askyesno("Warning", "Shrinking rack may remove items."):
                 self.rack_size_var.set(self.rack_height); return
        self.rack_height = new_height
        for view in self.views.values():
            view[:] = [c for c in view if c['start_u_slot'] + c['size_u'] - 1 <= self.rack_height]
        self._draw_rack_and_components()
        self._record_current_state()

    def export_canvas_as_image(self):
        self.canvas.update_idletasks()
        x = self.root.winfo_x() + self.canvas.winfo_x() + 20
        y = self.root.winfo_y() + self.canvas.winfo_y() + 50
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            try: ImageGrab.grab(bbox=(x, y, x + self.canvas.winfo_width(), y + self.canvas.winfo_height())).save(file_path); messagebox.showinfo("Saved", f"Image saved.")
            except Exception as e: messagebox.showerror("Error", f"{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RackPlannerApp(root)
    root.mainloop()
