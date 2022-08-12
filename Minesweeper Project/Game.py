if __name__ == "__main__":
    print("Error: you need to start the file from main_minesweeper.py")
    print("Quiting program")
    quit()


from Cell import Cell
import tkinter as tk
from tkinter import messagebox,simpledialog
from collections import defaultdict, deque
from datetime import time, date, datetime
import csv,os

class Game:
    def __init__(self, window):
        self.timer_id = None
        self.game_size = 13
        self.start_time = None
        self.cells = None
        self.window = window
        self.game_over = False

        # for keeping track of game progress
        self.total_mines = None  # mines present in the game, updated every new game
        self.clicked_count = None  # how many cells have been revealed
        self.flag_count = None  # how many flags are set
        self.correct_flag_count = None  # keeps track of only CORRECT flags, game ends when this equals total_mines

        # images of cells
        self.images = {
            "default": tk.PhotoImage(file="images/cell_default.png"),
            "mined": tk.PhotoImage(file="images/cell_mined.png"),
            "mine": tk.PhotoImage(file="images/cell_mine.png"),
            "flag": tk.PhotoImage(file="images/cell_flag.png"),
            "numbers": []
        }
        for i in range(1, 9):
            self.images["numbers"].append(tk.PhotoImage(file=f"images/cell_{i}.png"))

        # game info frame
        self.game_info_frame = tk.Frame(master=self.window, width=self.window.winfo_screenwidth() / 2,
                                   height=self.window.winfo_screenheight())
        tk.Label(master=self.game_info_frame, text="Minesweeper").place(x=self.window.winfo_screenwidth() / 5, y=75)
        tk.Label(master=self.game_info_frame, text="Left Click: Open cell ").place(x=self.window.winfo_screenwidth() / 10,
                                                                              y=180)
        tk.Label(master=self.game_info_frame, text="Right Click: Flag as dangerous").place(
            x=self.window.winfo_screenwidth() / 10, y=200)
        tk.Label(master=self.game_info_frame, text="Game is over when all the flags are in the correct spots").place(
            x=self.window.winfo_screenwidth() / 10, y=220)
        self.labels = {
            "flags": tk.Label(master=self.game_info_frame, text="Flags: 0"),
            "mines": tk.Label(master=self.game_info_frame, text="Mines: 0"),
            "time": tk.Label(master=self.game_info_frame, text="Time: 00:00:00")
        }
        self.labels["flags"].place(x=self.window.winfo_screenwidth() / 10, y=250)
        self.labels["mines"].place(x=self.window.winfo_screenwidth() / 10, y=270)
        self.labels["time"].place(x=self.window.winfo_screenwidth() / 10, y=290)
        self.game_info_frame.place(x=0, y=0)


        # leaderboards frame
        self.leaderboard_frame = tk.Frame(master=self.window, width=self.window.winfo_screenwidth() / 2, height=self.window.winfo_screenheight())
        tk.Label(master=self.leaderboard_frame, text="Leaderboard").place(x=self.window.winfo_screenwidth() / 5, y=75)
        self.leaderboard_frame.place(x=0, y=self.window.winfo_screenheight() / 2)
        
        self.get_high_scores()        
        self.setup()
        self.start_game()
        self.update_timer()

    
    def get_high_scores(self):
        '''find and display high scores of previous games that are saved in records.csv'''
        best_times=[]
        best_players=[]
        player_name_record=[]
        player_time_record=[]
        first_line=True
        
        if not(os.path.exists("records.csv")):#if file does't exist yet, create it
            f=open("records.csv","w")
            f.write("Player_name,time_taken\n")
            f.close()
        
        #read from csv file into two arrays with coresponding elements matching up
        with open ("records.csv") as csvfile:
            csv_reader=csv.reader(csvfile, delimiter=',')
            for row in csv_reader:
                if first_line==True:
                    first_line=False
                else:
                    player_name_record.append(row[0])
                    player_time_record.append(row[1])

        #search for the top scores with the best times according to n
        n=5 
        if (len(player_name_record)==0):#no records exist yet, nothing to display
            tk.Label(master=self.leaderboard_frame, text= "No records exist yet" ).place(x=self.window.winfo_screenwidth() / 8, y=120)
            return

        elif (len(player_name_record)<n):#if less than n players print them all out 
            tk.Label(master=self.leaderboard_frame, text= "Top "+ str(len(player_name_record)) +" player(s)" ).place(x=self.window.winfo_screenwidth() / 8, y=120)
            for i in range(len(player_name_record)):
                tk.Label(master=self.leaderboard_frame, text= player_name_record[i] + ": " + player_time_record[i]).place(x=self.window.winfo_screenwidth() / 8, y=140+(i*20))

        else: 
            tk.Label(master=self.leaderboard_frame, text= "Top "+ str(n) +" players" ).place(x=self.window.winfo_screenwidth() / 8, y=120)
            for i in range(n): #print out top n scores
                min_val=player_time_record[0]
                element=0
                for j in range(len(player_time_record)):#find best times and corresponding element value
                    if player_time_record[j]<min_val:
                        min_val=player_time_record[j]
                        element=j
                best_times.append(min_val)
                best_players.append(player_name_record[element])

                #remove times that have been recorded into high score list already
                player_time_record.remove(player_time_record[element])
                player_name_record.remove(player_name_record[element])

            #Change display on game screen within leaderboard_frame
            for i in range(len(best_players)):
                tk.Label(master=self.leaderboard_frame, text= best_players[i] + ": " + best_times[i]).place(x=self.window.winfo_screenwidth() / 8, y=140+(i*20))


    def setup(self):
        """Creates the cells and resets relevant variables"""
        self.flag_count = 0
        self.correct_flag_count = 0
        self.clicked_count = 0
        self.start_time = None
        
        # Create cells of the game with clickable buttons. Bind mouse click actions to each button.
        self.cells = defaultdict(dict)
        self.total_mines = 0

        # game board frame where the buttons are
        game_frame = tk.Frame(master=self.window, width=150, height=150)
        game_frame.place(x=self.window.winfo_screenwidth() / 2, y=0)
        for x in range(self.game_size):  # rows
            for y in range(self.game_size):  # columns
                self.cells[x][y] = Cell(x, y, game_frame, self)  # create the cell
                if self.cells[x][y].isMine:
                    self.total_mines += 1

        # loop again to find nearby mines and display number on tile
        for x in range(0, self.game_size):
            for y in range(0, self.game_size):
                mc = 0
                for n in self.get_neighbors(x, y):
                    mc += 1 if n.isMine else 0
                self.cells[x][y].nearby_mine_count = mc

    def get_neighbors(self, x, y):
        """Gets returns a list of cell objects next to a given cell"""
        neighbors = []
        coords = [
            (x - 1, y - 1),  # top right
            (x - 1, y),  # top middle
            (x - 1, y + 1),  # top left
            (x, y - 1),  # left
            (x, y + 1),  # right
            (x + 1, y - 1),  # bottom right
            (x + 1, y),  # bottom middle
            (x + 1, y + 1),  # bottom left
        ]
        for c in coords:
            try:
                neighbors.append(self.cells[c[0]][c[1]])
            except KeyError:  # to prevent error exception, simply don't add nonexistent cells to neighbors array
                pass
        return neighbors

    def clear_surrounding_cells(self, x, y):
        """uses a queue to clear all cells that have zero mines nearby"""
        queue = deque([(x, y)])
        while len(queue) != 0:
            x, y = queue.popleft()

            for cell in self.get_neighbors(x, y):
                cell.clear_cell(queue)

    def refresh_labels(self):
        """updated the labels for user to track their progress"""
        self.labels["flags"].config(text=f"Flags: {self.flag_count}")
        self.labels["mines"].config(text=f"Mines: {self.total_mines}")

    def update_timer(self):
        ts = "0:00:00"
        if self.start_time is not None:
            delta = datetime.now() - self.start_time
            ts = str(delta).split('.')[0]  # cleanup
        self.labels["time"].config(text=f"Time: {ts}")
        self.timer_id = self.game_info_frame.after(100, self.update_timer)
        return ts

    def start_game(self):
        """creates new game, updates UI"""
        self.setup()
        self.refresh_labels()

    def check_winner(self):
        """returns True when users create """
        if self.correct_flag_count == self.total_mines:
            self.end_game(True)

    def end_game(self, won):
        """game over screen. if passed in True, game won, otherwise the game is lost"""
        for x in range(self.game_size):
            for y in range(self.game_size):
                currCell = self.cells[x][y]
                if not currCell.isMine and currCell.state == "FLAGGED":
                    currCell.button.config(image=self.images["mined"])
                if currCell.isMine and currCell.state != "FLAGGED":
                    currCell.button.config(image=self.images["mine"])
                currCell.disable_button()  # disable all buttons

        self.game_over = True
        time_taken = self.update_timer()

        #start of data record functioanlity if you won
        if (won==True):
            
            user_input=simpledialog.askstring(title="Player Name",
                                  prompt="What's your Name?")

            data=user_input + "," + time_taken + "\n"  
            print(user_input, "has won")

            
            f=open("records.csv","a")
     
            f.write(data)
            f.close()
        #end of data record functionality
            
        msg = "Game over! You won." if won else "Hit mine, game over."
        msg += f"\nTime taken: {time_taken}" if won else ""
        msg += "\nPlay again?"
        res = tk.messagebox.askyesno("Game Over", msg)

        if res:
            self.cleanup()  # cleanup cell objects created to prevent too much memory from being used
            self.start_game()
            self.get_high_scores()
        else:
            quit()

    def cleanup(self):
        del self.cells

# end of game class
