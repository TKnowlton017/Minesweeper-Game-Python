if __name__ == "__main__":
    print("Error: you need to start the file from main_minesweeper.py")
    print("Quiting program")
    quit()

import random
import tkinter as tk
from datetime import time, date, datetime


class Cell:
    def __init__(self, x, y, game_frame, g):
        self.x = x
        self.y = y
        self.game = g
        self.button = self.create_button(game_frame)
        self.id = f"{x}_{y}"
        self.isMine = False
        self.state = "DEFAULT"  # DEFAULT, MINED, FLAGGED are the possible states
        self.nearby_mine_count = 0  # this is set in Game because it has access to all the cells

        self.create_mine()

    def create_button(self, game_frame):
        """new button creation"""
        button_label = tk.Button(master=game_frame)

        button_label.grid(row=self.x, column=self.y)
        button_function = tk.Button(master=button_label, image=self.game.images['default'])
        button_function.bind("<Button-1>", self.open_cell)  # binds left click to open_cell() function
        button_function.bind("<Button-3>", self.mark_cell)  # binds right click to mark_cell() function
        button_function.pack()
        return button_function  # tkinter button attached to myButton attribute

    def open_cell(self, event):
        """Functionality of a left click, open the cell and determine if a mine was hit"""
        if self.game.start_time is None:  # starts the timer on the first click from user
            self.game.start_time = datetime.now()

        if self.isMine:
            self.game.end_game(False)
            return

        if self.nearby_mine_count == 0:
            self.button.config(image=self.game.images['mined'])
            self.game.clear_surrounding_cells(self.x, self.y)
        else:
            self.button.config(image=self.game.images["numbers"][self.nearby_mine_count - 1])

        self.state = 'MINED'
        self.disable_button()
        self.game.clicked_count += 1
        self.game.refresh_labels()
        self.game.check_winner()

    def clear_cell(self, queue):
        """determined if a cell is a mine or not"""
        if self.state != 'DEFAULT':
            return

        if self.nearby_mine_count == 0 and not self.isMine:
            self.button.config(image=self.game.images['mined'])
            queue.append((self.x, self.y))
        else:
            self.button.config(image=self.game.images['numbers'][self.nearby_mine_count - 1])

        self.state = 'MINED'
        self.disable_button()
        self.game.clicked_count += 1

    def disable_button(self):
        """disables buttons so that cells won't work after being opened """
        # self.button['state'] = 'disabled'
        self.button.unbind("<Button-1>")
        self.button.unbind("<Button-3>")

    def mark_cell(self, event):
        """Functionality of right click, when you right-click on a cell mark it as dangerous"""
        if self.game.start_time is None:  # starts the timer on the first click from user
            self.game.start_time = datetime.now()
        if not self.state == "FLAGGED":
            self.button.config(image=self.game.images['flag'])
            self.state = "FLAGGED"
            self.game.flag_count += 1
            self.button.unbind("<Button-1>")
            if self.isMine:
                self.game.correct_flag_count += 1
        elif self.state == "FLAGGED":
            self.button.config(image=self.game.images['default'])
            self.state = "DEFAULT"
            self.game.flag_count -= 1
            self.button.bind("<Button-1>", self.open_cell)
            if self.isMine:
                self.game.correct_flag_count -= 1
        self.game.refresh_labels()
        self.game.check_winner()

    def create_mine(self):
        """Randomly create mines, assigns true or false to isMine attribute"""
        self.isMine = (random.uniform(0.0, 1.0) < 0.1)

# end of cell class
