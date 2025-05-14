import tkinter as tk
from tkinter import simpledialog, messagebox

class HanoiUI(tk.Tk):
    def __init__(self, disk_count):
        super().__init__()
        self.title("Tower of Hanoi")
        self.geometry("1000x500")
        self.disk_count = disk_count

        self.canvas = tk.Canvas(self, width=1000, height=400, bg="white")
        self.canvas.pack()

        self.controls = tk.Frame(self)
        self.controls.pack(pady=10)

        self.next_button = tk.Button(self.controls, text="Next", command=self.next_move)
        self.next_button.grid(row=0, column=0, padx=5)

        self.restart_button = tk.Button(self.controls, text="Restart", command=self.restart)
        self.restart_button.grid(row=0, column=1, padx=5)

        self.stop_button = tk.Button(self.controls, text="Stop", command=self.stop)
        self.stop_button.grid(row=0, column=2, padx=5)

        self.log_button = tk.Button(self.controls, text="Show Log", command=self.show_log)
        self.log_button.grid(row=0, column=3, padx=5)

        self.rod_x = [250, 500, 750]
        self.disk_height = 20
        self.disk_width_unit = 15

        self.moves = []
        self.move_index = 0
        self.move_log = []
        self.disk_items = {}

        self.log_window = None
        self.log_box = None

        self.init_game()

    def init_game(self):
        self.canvas.delete("all")
        self.moves.clear()
        self.move_log.clear()
        self.move_index = 0
        self.disk_items.clear()
        self.rods = [[i for i in range(1, self.disk_count + 1)], [], []]
        self.draw_rods()
        self.draw_disks()
        self.generate_moves(self.disk_count, 0, 2, 1)
        if self.log_box:
            self.log_box.config(state="normal")
            self.log_box.delete("1.0", tk.END)
            self.log_box.config(state="disabled")

    def draw_rods(self):
        for x in self.rod_x:
            self.canvas.create_rectangle(x - 5, 100, x + 5, 380, fill="black")

    def draw_disks(self):
        for rod_index, rod in enumerate(self.rods):
            for i, disk in enumerate(reversed(rod)):
                x = self.rod_x[rod_index]
                width = disk * self.disk_width_unit
                y = 380 - (i + 1) * self.disk_height
                rect = self.canvas.create_rectangle(x - width, y, x + width, y + self.disk_height, fill="skyblue", outline="black")
                self.disk_items[disk] = rect

    def update_disks(self):
        for rod_index, rod in enumerate(self.rods):
            for i, disk in enumerate(reversed(rod)):
                x = self.rod_x[rod_index]
                width = disk * self.disk_width_unit
                y = 380 - (i + 1) * self.disk_height
                self.canvas.coords(self.disk_items[disk], x - width, y, x + width, y + self.disk_height)

    def generate_moves(self, n, source, target, auxiliary):
        if n == 1:
            self.moves.append((source, target))
        else:
            self.generate_moves(n - 1, source, auxiliary, target)
            self.moves.append((source, target))
            self.generate_moves(n - 1, auxiliary, target, source)

    def next_move(self):
        if self.move_index < len(self.moves):
            src, dst = self.moves[self.move_index]
            if self.rods[src]:
                disk = self.rods[src].pop(0)
                self.rods[dst].insert(0, disk)
                self.update_disks()
                move_text = f"Move {disk} from Rod {src + 1} to Rod {dst + 1}"
                self.move_log.append(move_text)
                self.update_log_window(move_text)
            self.move_index += 1
        else:
            messagebox.showinfo("Done", "All moves completed!")

    def restart(self):
        if self.log_window is not None:
            self.log_window.destroy()
            self.log_window = None
            self.log_box = None
        self.init_game()

    def stop(self):
        if self.log_window is not None:
            self.log_window.destroy()
            self.log_window = None
            self.log_box = None
        self.withdraw()
        new_count = simpledialog.askinteger("Tower of Hanoi", "Enter number of disks (3–10):", minvalue=3, maxvalue=10)
        if new_count:
            self.disk_count = new_count
            self.deiconify()
            self.init_game()
        else:
            self.destroy()

    def show_log(self):
        if self.log_window is not None:
            self.log_window.lift()
            return

        self.log_window = tk.Toplevel(self)
        self.log_window.title("Move Log")
        self.log_window.geometry("400x400")

        self.log_box = tk.Text(self.log_window, wrap="word")
        self.log_box.pack(expand=True, fill="both")
        self.log_box.config(state="disabled")

        for line in self.move_log:
            self.update_log_window(line)

        self.log_window.protocol("WM_DELETE_WINDOW", self.close_log)

    def update_log_window(self, line):
        if self.log_box:
            self.log_box.config(state="normal")
            self.log_box.insert(tk.END, line + "\n")
            self.log_box.see(tk.END)
            self.log_box.config(state="disabled")

    def close_log(self):
        if self.log_window is not None:
            self.log_window.destroy()
            self.log_window = None
            self.log_box = None

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    n = simpledialog.askinteger("Tower of Hanoi", "Enter number of disks (3–10):", minvalue=3, maxvalue=10)
    if n:
        app = HanoiUI(n)
        app.mainloop()
