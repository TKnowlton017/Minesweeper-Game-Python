from Game import Game
import tkinter as tk

# https://realpython.com/python-gui-tkinter/ #useful website

if __name__ == "__main__":

    print("Starting new game")
    window = tk.Tk()
    window.title("Minesweeper")
    window.state('zoomed')
    g = Game(window)
    window.mainloop()  # keeps window open and loops for events until window is closed by user
