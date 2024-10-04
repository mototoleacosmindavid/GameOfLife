import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
import numpy as np
import time
import rule_engine

def count_ceels(matrix):
    vii = 0
    morti = 0
    for el in matrix:
        for item in el:
            if item == 1:
                vii = vii + 1
            else:
                morti = morti + 1 
    return morti, vii
        
def count_neighbor_values(matrix, x, y):
    num_zeros = 0
    num_ones = 0
    height = len(matrix)
    width = len(matrix[0])

    h_min = max(0, x - 1)
    h_max = min(x + 2, height)
    w_min = max(0, y - 1)
    w_max = min(y + 2, width)

    for i in range(h_min, h_max):
        for j in range(w_min, w_max):
            if (i, j) != (x, y):
                if matrix[i][j] == 0:
                    num_zeros += 1
                else:
                    num_ones += 1
                    
    eu = 1 if matrix[x, y] == 1 else 0

    return num_zeros, num_ones, eu




class GameOfLife:
    def __init__(self, window, w=20, h=20, cell_size=30):
        self.window = window
        self.width = w
        self.height = h
        self.cell_size = cell_size
        board_width = w * cell_size
        board_height = h * cell_size
        self.canvas = tk.Canvas(window, width=board_width, height=board_height)
        self.canvas.pack()
        self.board = np.zeros((h, w), dtype=int)
        self.rects = []
        self.running = False
        self.draw_board()
        self.create_menu()
        self.create_info_labels()
        self.update_info_labels()
        self.canvas.bind("<Button-1>", self.modify_cell)

        control_frame = tk.Frame(window)
        control_frame.pack(side='bottom', fill='x', expand=True)

        self.next_button = tk.Button(control_frame, text="Next Step", command=self.next_generation)
        self.next_button.pack(side='left', padx=10, pady=10)
        self.start_button = tk.Button(control_frame, text="Start/Stop", command=self.start_stop)
        self.start_button.pack(side='left', padx=10, pady=10)
        self.reset_button = tk.Button(control_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side='left', padx=10, pady=10)
        window.geometry(f"{board_width+20}x{board_height+150}")


    def draw_board(self):
        self.canvas.delete("all")
        self.rects = []
        for cell1 in range(self.height):
            row = []
            for cell2 in range(self.width):
                if self.board[cell1][cell2] == 1:
                    rect = self.canvas.create_rectangle(cell2*self.cell_size, cell1*self.cell_size,
                                                        (cell2+1)*self.cell_size, (cell1+1)*self.cell_size,
                                                        fill="black")
                    row.append(rect)
                else:
                    rect = self.canvas.create_rectangle(cell2*self.cell_size, cell1*self.cell_size,
                                                        (cell2+1)*self.cell_size, (cell1+1)*self.cell_size,
                                                        fill="white")
                    row.append(rect)
            self.rects.append(row)

    def modify_cell(self, event):
        if not self.running:
            x = event.x // self.cell_size
            y = event.y // self.cell_size
            if self.board[y][x] != 1:
                self.board[y][x] = 1
            else:
                self.board[y][x] = 0
            self.draw_board()
            self.update_info_labels()

    def verify_condition(self):
        celule_vii = rule_engine.Rule(
            'vii >= 3'
        )
        dictionar2 = dict()
        morti, vii =  count_ceels(self.board)
        dictionar2["morti"] = morti
        dictionar2["vii"] = vii
        if not celule_vii.matches(dictionar2):
            return False
        else:
            return True

    def next_generation(self):
        moare1 = rule_engine.Rule(
            'vii < 2 and eu == 1' 
        )
        moare2 = rule_engine.Rule(
            'vii > 3 and eu == 1' 
        )
        traieste1 = rule_engine.Rule(
            'vii > 1 and vii < 4 and eu == 1'
        )
        traieste2 = rule_engine.Rule(
            'vii == 3 and eu == 0'
        )
        new_board = np.copy(self.board)
        height, width = new_board.shape
        dictionar = dict()
        for i in range(height):
            for j in range(width):
                zeros, ones, eu = count_neighbor_values(self.board, i, j)
                dictionar["vii"] = ones
                dictionar["morti"] = zeros
                dictionar["eu"] = eu
                if moare1.matches(dictionar) or moare2.matches(dictionar):
                    new_board[i][j] = 0
                elif traieste1.matches(dictionar) or traieste2.matches(dictionar):
                    new_board[i][j] = 1
        self.board = new_board
        self.draw_board()
        self.update_info_labels()

    def start_stop(self):
        if not self.running:
            self.running = True
            self.run_game()
        else:
            self.running = False

    def reset(self):
        self.running = False 
        self.board = np.zeros((self.height, self.width), dtype=int)
        self.draw_board()
        self.update_info_labels()


    def run_game(self):
        if self.verify_condition():
            while self.running:
                self.next_generation()
                self.window.update()
                time.sleep(0.2)
        else:
            print("Mai putin de 3 celule vii")

    def create_menu(self):
        main_menu = tk.Menu(self.window)
        self.window.config(menu=main_menu)

        size_menu = tk.Menu(main_menu, tearoff=0)
        size_menu.add_command(label="20x20", command=lambda: self.modify_dimensions(20, 20))
        size_menu.add_command(label="30x30", command=lambda: self.modify_dimensions(30, 30))
        size_menu.add_command(label="40x40", command=lambda: self.modify_dimensions(40, 40))
        main_menu.add_cascade(label="Set Dimensions", menu=size_menu)

        generate_menu = tk.Menu(main_menu, tearoff=0)
        generate_menu.add_command(label="Random Generate", command=self.get_random_input)
        main_menu.add_cascade(label="Random Generate", menu=generate_menu)

        info_menu = tk.Menu(main_menu, tearoff=0)
        info_menu.add_command(label="Explanation", command=self.explanation)
        main_menu.add_cascade(label="Explanation", menu=info_menu)

    def explanation(self):
        explanation_text = """
    Game of Life Explanation
    The Game of Life is an self played computer game invented by the mathematician John Conway.

    It consists of a table with cells which can multiply, die or live, depending of a series of mathematical rules.
    Depending on the initial conditions, the cells form various patterns throughout the course of the game.
    
    Rules
    For a space that is populated:
    - Each cell with one or no neighbors dies, as if by solitude.
    - Each cell with four or more neighbors dies, as if by overpopulation.
    - Each cell with two or three neighbors survives.

    For a space that is empty or unpopulated:
    - Each cell with three neighbors becomes populated.
    """
        messagebox.showinfo("Explanation", explanation_text)

    def get_random_input(self):
        num_live_cells = simpledialog.askinteger("Input", "Enter the number of live cells:", parent=self.window)
        if num_live_cells is not None:
            self.random_generate(num_live_cells)

    def random_generate(self, number_live_cells):
        max_alive = self.width * self.height
        number_live_cells = min(number_live_cells, max_alive)
        rand = np.random.choice(max_alive, number_live_cells, replace=False)
        self.board = np.zeros((self.height, self.width), dtype=int)
        for index in rand:
            x = index % self.width
            y = index // self.width
            self.board[y][x] = 1
        self.draw_board()
        self.update_info_labels()

    def create_info_labels(self):
        self.live_label = tk.Label(self.window, text="Live cells: 0")
        self.live_label.pack()
        self.dead_label = tk.Label(self.window, text="Dead cells: 0")
        self.dead_label.pack()

    def update_info_labels(self):
        live_count = np.count_nonzero(self.board)
        dead_count = self.width * self.height - live_count
        self.live_label.config(text=f"Live cells: {live_count}")
        self.dead_label.config(text=f"Dead cells: {dead_count}")

    def modify_dimensions(self, width, height):
        self.width = width
        self.height = height
        self.board = np.zeros((height, width), dtype=int)
        if width == 20:
            self.cell_size = 30
        elif width == 30:
            self.cell_size = 20
        elif width == 40:
            self.cell_size = 15
        self.canvas.config(width=width*self.cell_size, height=height*self.cell_size)
        self.draw_board()
        self.update_info_labels()

if __name__ == "__main__":
    root = tk.Tk()
    game = GameOfLife(root)
    root.mainloop()

    root.mainloop()