import tkinter as tk
from tkinter import simpledialog, messagebox

class Theme:
    LIGHT = {
        "bg": "white", "fg": "black",
        "button_bg": "#e0e0e0", "button_fg": "black",
        "canvas_bg": "white", "scale_trough": "#d0d0d0"
    }
    DARK = {
        "bg": "#2e2e2e", "fg": "white",
        "button_bg": "#444444", "button_fg": "white",
        "canvas_bg": "#1e1e1e", "scale_trough": "#555555"
    }

class ModeSelector(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tower of Hanoi – Select Mode")
        self.geometry("400x380")
        self.theme = Theme.LIGHT
        self.create_widgets()
        self.apply_theme()

    def create_widgets(self):
        self.title_label = tk.Label(self, text="Tower of Hanoi", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=20)

        self.mode_var = tk.StringVar(value='step')
        modes = [
            ("Step-by-Step", 'step'),
            ("Auto-Play", 'auto'),
            ("Manual (Drag & Drop)", 'manual')
        ]
        for text, val in modes:
            rb = tk.Radiobutton(self, text=text, variable=self.mode_var, value=val)
            rb.pack(anchor='w', padx=50)

        self.disk_button = tk.Button(self, text="Start Game", command=self.start_game)
        self.disk_button.pack(pady=10)

        self.theme_button = tk.Button(self, text="Toggle Dark/Light", command=self.toggle_theme)
        self.theme_button.pack(pady=5)

        self.quit_button = tk.Button(self, text="Quit", command=self.quit)
        self.quit_button.pack(pady=5)

    def apply_theme(self):
        colors = self.theme
        self.configure(bg=colors["bg"])
        self.title_label.configure(bg=colors["bg"], fg=colors["fg"])
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(
                    bg=colors["button_bg"], fg=colors["button_fg"],
                    activebackground=colors["button_bg"], activeforeground=colors["button_fg"]
                )
            elif isinstance(widget, tk.Radiobutton):
                widget.configure(
                    bg=colors["bg"], fg=colors["fg"],
                    activebackground=colors["button_bg"], activeforeground=colors["button_fg"]
                )

    def toggle_theme(self):
        self.theme = Theme.DARK if self.theme == Theme.LIGHT else Theme.LIGHT
        self.apply_theme()

    def start_game(self):
        self.withdraw()
        mode = self.mode_var.get()
        # Disk count prompt
        if self.theme == Theme.DARK:
            temp = tk.Toplevel(self)
            temp.title("Enter Disk Count")
            temp.geometry("300x150")
            temp.configure(bg=self.theme["bg"])
            label = tk.Label(temp, text="Enter number of disks (3–10):", bg=self.theme["bg"], fg=self.theme["fg"])
            label.pack(pady=10)
            entry_var = tk.StringVar()
            entry = tk.Entry(temp, textvariable=entry_var, bg=self.theme["button_bg"], fg=self.theme["button_fg"])
            entry.pack()
            def confirm():
                try:
                    val = int(entry_var.get())
                    if 3 <= val <= 10:
                        temp.destroy()
                        HanoiUI(val, self.theme, self, mode).mainloop()
                    else:
                        messagebox.showerror("Invalid", "Enter a number between 3 and 10")
                except:
                    messagebox.showerror("Invalid", "Enter a valid number")
            btn = tk.Button(temp, text="Start", command=confirm,
                            bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                            activebackground=self.theme["button_bg"], activeforeground=self.theme["button_fg"])
            btn.pack(pady=10)
            temp.protocol("WM_DELETE_WINDOW", lambda: (temp.destroy(), self.deiconify()))
        else:
            disk_count = simpledialog.askinteger("Tower of Hanoi", "Enter number of disks (3–10):", minvalue=3, maxvalue=10)
            if disk_count:
                HanoiUI(disk_count, self.theme, self, mode).mainloop()
            else:
                self.deiconify()

class HanoiUI(tk.Tk):
    def __init__(self, disk_count, theme, parent_menu, mode):
        super().__init__()
        self.title("Tower of Hanoi")
        self.geometry("1000x550")
        self.disk_count = disk_count
        self.theme = theme
        self.parent_menu = parent_menu
        self.mode = mode
        self.auto_play = False
        self.delay_ms = 500
        self.dragging_disk = None
        self.drag_start = (0, 0)

        # Canvas
        self.canvas = tk.Canvas(self, width=1000, height=400, bg=self.theme["canvas_bg"])
        self.canvas.pack()
        # Controls frame
        self.controls = tk.Frame(self, bg=self.theme["bg"])
        self.controls.pack(pady=5)

        # Buttons & slider
        self.next_btn = tk.Button(self.controls, text="Next", command=self.next_move)
        self.auto_btn = tk.Button(self.controls, text="Auto-Play", command=self.toggle_auto)
        self.speed_slider = tk.Scale(self.controls, from_=2000, to=100, resolution=100,
                                     orient="horizontal", label="Speed (ms)", command=self.update_speed,
                                     bg=self.theme["bg"], fg=self.theme["fg"], troughcolor=self.theme["scale_trough"], highlightbackground=self.theme["bg"])
        self.restart_btn = tk.Button(self.controls, text="Restart", command=self.restart)
        self.back_btn = tk.Button(self.controls, text="Back to Menu", command=self.stop)
        self.log_btn = tk.Button(self.controls, text="Show Log", command=self.show_log)

        btns = [self.next_btn, self.auto_btn, self.restart_btn, self.back_btn, self.log_btn]
        for i, b in enumerate(btns):
            b.grid(row=0, column=i, padx=5)
            b.configure(bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                        activebackground=self.theme["button_bg"], activeforeground=self.theme["button_fg"])
        self.speed_slider.grid(row=1, column=0, columnspan=5, pady=5)
        self.speed_slider.set(self.delay_ms)

        # Mode-specific controls
        if self.mode == 'step':
            self.auto_btn.grid_remove()
            self.speed_slider.grid_remove()
        elif self.mode == 'auto':
            self.next_btn.grid_remove()
        elif self.mode == 'manual':
            self.next_btn.grid_remove()
            self.auto_btn.grid_remove()
            self.speed_slider.grid_remove()
            self.enable_drag()

        # Game state
        self.rod_x = [250, 500, 750]
        self.disk_h = 20
        self.disk_w_unit = 15
        self.rods = []
        self.moves = []
        self.move_idx = 0
        self.move_log = []
        self.disk_items = {}
        self.log_window = None
        self.log_box = None

        self.init_game()

    def init_game(self):
        self.auto_play = False
        self.auto_btn.config(text="Auto-Play")
        self.canvas.configure(bg=self.theme["canvas_bg"])
        self.canvas.delete("all")
        self.moves.clear()
        self.move_log.clear()
        self.move_idx = 0
        self.disk_items.clear()
        self.rods = [[i for i in range(1, self.disk_count+1)], [], []]
        self.draw_rods()
        self.draw_disks()
        self.generate_moves(self.disk_count, 0, 2, 1)
        if self.log_box:
            self.log_box.config(state="normal")
            self.log_box.delete("1.0", tk.END)
            self.log_box.config(bg=self.theme["canvas_bg"], fg=self.theme["fg"], insertbackground=self.theme["fg"], state="disabled")

    def draw_rods(self):
        for x in self.rod_x:
            self.canvas.create_rectangle(x-5, 100, x+5, 380, fill=self.theme["button_bg"])

    def draw_disks(self):
        for r, rod in enumerate(self.rods):
            for lvl, disk in enumerate(reversed(rod)):
                x = self.rod_x[r]
                w = disk * self.disk_w_unit
                y = 380 - (lvl+1) * self.disk_h
                item = self.canvas.create_rectangle(x-w, y, x+w, y+self.disk_h,
                                                  fill="skyblue", outline="black",
                                                  tags=(f"disk{disk}", "disk"))
                self.disk_items[disk] = item

    def update_disks(self):
        for r, rod in enumerate(self.rods):
            for lvl, disk in enumerate(reversed(rod)):
                x = self.rod_x[r]
                w = disk * self.disk_w_unit
                y = 380 - (lvl+1) * self.disk_h
                self.canvas.coords(self.disk_items[disk], x-w, y, x+w, y+self.disk_h)

    def generate_moves(self, n, s, d, a):
        if n == 1:
            self.moves.append((s, d))
        else:
            self.generate_moves(n-1, s, a, d)
            self.moves.append((s, d))
            self.generate_moves(n-1, a, d, s)

    def next_move(self):
        if self.move_idx < len(self.moves):
            s, d = self.moves[self.move_idx]
            if self.rods[s]:
                disk = self.rods[s].pop(0)
                self.rods[d].insert(0, disk)
                self.update_disks()
                txt = f"Move {disk} from Rod {s+1} to Rod {d+1}"
                self.move_log.append(txt)
                self.update_log(txt)
            self.move_idx += 1
        else:
            messagebox.showinfo("Done", "All moves completed!")
            self.auto_play = False
            self.auto_btn.config(text="Auto-Play")

    def toggle_auto(self):
        self.auto_play = not self.auto_play
        self.auto_btn.config(text="Pause" if self.auto_play else "Auto-Play")
        if self.auto_play:
            self.auto_step()

    def auto_step(self):
        if self.auto_play:
            self.next_move()
            if self.move_idx < len(self.moves):
                self.after(self.delay_ms, self.auto_step)

    def update_speed(self, v):
        try:
            self.delay_ms = int(v)
        except:
            pass

    def restart(self):
        if self.log_window:
            self.log_window.destroy()
            self.log_window = None
            self.log_box = None
        self.init_game()

    def stop(self):
        if self.log_window:
            self.log_window.destroy()
            self.log_window = None
            self.log_box = None
        self.destroy()
        self.parent_menu.deiconify()

    def show_log(self):
        if self.log_window:
            self.log_window.lift()
            return
        self.log_window = tk.Toplevel(self)
        self.log_window.title("Move Log")
        self.log_window.geometry("400x400")
        self.log_window.config(bg=self.theme["bg"])
        self.log_box = tk.Text(self.log_window, wrap="word",
                                bg=self.theme["canvas_bg"], fg=self.theme["fg"], insertbackground=self.theme["fg"])
        self.log_box.pack(expand=True, fill="both")
        self.log_box.config(state="disabled")
        for line in self.move_log:
            self.update_log(line)
        self.log_window.protocol("WM_DELETE_WINDOW", self.close_log)

    def update_log(self, line):
        if self.log_box:
            self.log_box.config(state="normal")
            self.log_box.insert(tk.END, line + "\n")
            self.log_box.see(tk.END)
            self.log_box.config(state="disabled")

    def close_log(self):
        if self.log_window:
            self.log_window.destroy()
            self.log_window = None
            self.log_box = None

    def enable_drag(self):
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for itm in items:
            if "disk" in self.canvas.gettags(itm):
                disk = next((d for d, i in self.disk_items.items() if i == itm), None)
                for r, rod in enumerate(self.rods):
                    if rod and rod[0] == disk:
                        self.dragging_disk = disk
                        self.origin_rod = r
                        self.drag_start = (event.x, event.y)
                        self.canvas.tag_raise(itm)
                        return
        self.dragging_disk = None

    def on_motion(self, event):
        if self.dragging_disk:
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            itm = self.disk_items[self.dragging_disk]
            self.canvas.move(itm, dx, dy)
            self.drag_start = (event.x, event.y)

    def on_release(self, event):
        if self.dragging_disk is None:
            return
        x = event.x
        tgt = min(range(3), key=lambda i: abs(x - self.rod_x[i]))
        valid = not self.rods[tgt] or self.dragging_disk < self.rods[tgt][0]
        if valid:
            self.rods[self.origin_rod].pop(0)
            self.rods[tgt].insert(0, self.dragging_disk)
        self.update_disks()
        self.dragging_disk = None

if __name__ == "__main__":
    ModeSelector().mainloop()
