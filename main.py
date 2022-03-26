from tkinter import Tk, Button, Frame, Canvas, Label, LabelFrame
from tkinter import messagebox
from tkinter import CENTER, GROOVE, DISABLED, FLAT, LEFT, RIGHT

from functools import partial

import pickle

import random
import time

WIN_MIN_SIZE = (900, 600)

class Grid:
	def __init__(self):
		self.state = 0
		self.change = 1
		self.grid = []
		self.difficulty = None

	def get_time(self):
		s = str(int(str(time.time()).split(".")[0]) - self.start_time)
		if len(s) < 2:
			s = "00"+s
		elif len(s) < 3:
			s = "0"+s
		return s

	def setup(self, template):
		"""
		Setup a new grid with new bomb placements according to a template
		
		Args:
		    template (list): Rules to generate a new grid: [Size of the grid in X, Size of the grid in Y, Number of bombs on the map]
		"""
		# Reset the grid
		del self.grid
		self.grid = []

		# Generate the bomb placements
		bombs = []
		while not len(bombs) == template[2]: 
			for y in range(template[1]):
				for x in range(template[0]):
					if len(bombs) == template[2]:
						break

					if not [y, x] in bombs:
						random.seed(random.random())
						z = random.randint(1, 100)
						if z > 99:
							bombs.append([y, x])

				
		# Create the grid with the bombs
		for row in range(template[1]):
			self.grid.append([])
			for column in range(template[0]):
				if [row, column] in bombs:
					self.grid[-1].append(['b', 0, 0])
				else:
					self.grid[-1].append(['n', -1, 0])


		# Every place which is not a bomb is given a number corresponding to the number of bombs around it
		for row in range(template[1]):
			for column in range(template[0]):
				if self.grid[row][column][0] == 'b':
					continue
				else:
					z = 0 
					for x in range(-1, 2, 1):
						for y in range(-1, 2, 1):
							if (not row+y < 0) and (not row+y > len(self.grid)-1) and  (not column+x < 0) and (not column+x > len(self.grid[0])-1):
								n = self.grid[row+y][column+x]
							else:
								n = ['n']

							if not n[0] == 'n':
								z += 1

					self.grid[row][column][1] = z

		self.change = 1
		self.state = 1
		self.difficulty = template[3]
		self.start_time = int(str(time.time()).split(".")[0])

	def dig(self, x, y):
		if self.state == 1:
			if self.grid[y][x][0] == 'b':
				self.state = 3
			else:
				self.grid[y][x][2] = 1
				self.already_checked = []
				self.check_around(x, y)

	def check_around(self, column, row):
		self.already_checked.append([column, row])
		for x in range(-1, 2, 1):
			for y in range(-1, 2, 1):
				if (not row+y < 0) and (not row+y > len(self.grid)-1) and  (not column+x < 0) and (not column+x > len(self.grid[0])-1):
					if not self.grid[row+y][column+x][0] == 'b':
						self.grid[row+y][column+x][2] = 1
						if self.grid[row][column][1] == 0 and not [column+x, row+y] in self.already_checked:
							self.check_around(column+x, row+y)

	def check_full(self):
		errors = 0
		for row in self.grid:
			for column in row:
				if column[2] == 0:
					return
				elif column[2] == 2 and column[0] == "n":
					errors += 1
		if errors == 0:
			self.state = 4

	def mark(self, x, y):
		if self.state == 1:
			if self.grid[y][x][2] == 2:
				self.grid[y][x][2] = 0
			else:
				self.grid[y][x][2] = 2

	def state_nothing(self, e=False):
		self.grid = []
		self.change = 1
		self.state = 0 

def save(data):
	f = open("stats.data", "wb") 
	pickle.dump(data, f)
	f.close()

def get_data():
	f = open("stats.data", "rb")
	data = pickle.load(f)
	return data

def change_data(key, value):
	data = get_data()
	data[key] = value
	save(data)


class GUI(Tk):
	def __init__(self, grid):
		super().__init__()
		self.grid = grid

		self.mode = 0
		self.modes = [["DIG", "white", "#74e66e", 5], ["MARK", "white", "#ff5c5c", 5]]

		self.geometry(f"{WIN_MIN_SIZE[0]}x{WIN_MIN_SIZE[1]}")
		self.minsize(WIN_MIN_SIZE[0], WIN_MIN_SIZE[1])
		self.config(bg="#c9c9c9")
		self.title("Minesweeper ©Elouan COSSEC")
		self.bind("<Button-3>", self.change_mode)
		self.bind("<Escape>", self.grid.state_nothing)
		self.update_idletasks()

		self.menuframe = Frame(self, width=self.winfo_width(), height=self.winfo_height(), bg="#c9c9c9")

		self.gameframe = Frame(self, width=self.winfo_width(), height=self.winfo_height(), bg="#c9c9c9")

	def change_mode(self, e=False):
		if self.mode == 0:
			self.mode = 1
		else:
			self.mode = 0

	def change_btn(self, x, y):
		if self.mode == 1:
			self.grid.mark(x, y)
		else:
			self.grid.dig(x, y)

		self.check_all()
		self.grid.check_full()

	def check_all(self):
		for y in range(len(self.grid.grid)):
			for x in range(len(self.grid.grid[y])):
				if self.grid.grid[y][x][2] == 1:
					self.btns[y][x][0].config(text=str(self.grid.grid[y][x][1]), background="#c6c9c5", state=DISABLED)
				elif self.grid.grid[y][x][2] == 2:
					self.btns[y][x][0].config(background="#c9afaf")
				else:
					self.btns[y][x][0].config(background="#bec9bb")

	def get_stats_label(self):
		return str(self.grid.get_time())+"s"

	def draw(self):
		if self.grid.state == 4:
			change_data("totalgamesplayed", self.data["totalgamesplayed"]+1)
			change_data("totalwongames", self.data["totalwongames"]+1)

			if self.grid.difficulty == EASY[3] and (self.data["besttimeeasy"] == None or int(self.grid.get_time()) < self.data["besttimeeasy"]):
				change_data("besttimeeasy",  int(self.grid.get_time()))
			if self.grid.difficulty == MEDIUM[3] and (self.data["besttimeeasy"] == None or int(self.grid.get_time()) < self.data["besttimemedium"]):
				change_data("besttimemedium",  int(self.grid.get_time()))
			if self.grid.difficulty == HARD[3] and (self.data["besttimeeasy"] == None or int(self.grid.get_time()) < self.data["besttimehard"]):
				change_data("besttimehard",  int(self.grid.get_time()))

			messagebox.showinfo("WIN", "It took you {t} to win !".format(t=self.get_stats_label()))
			self.grid.state_nothing()
			
		if self.grid.state == 3:
			change_data("totalgamesplayed", self.data["totalgamesplayed"]+1)
			messagebox.showerror("LOSE", "You lost !")
			self.grid.state_nothing()

		if self.grid.state == 0:
			if self.grid.change:
				self.data = get_data()
				try:
					for l in self.btns:
						for btn in l:
							btn[0].destroy()
				except:
					pass

				try:
					self.gameframe.place_forget()
					self.topbtn.destroy()
					self.stats.destroy()
				except:
					pass

				self.easy_btn = Button(self.menuframe, text="EASY", width=int(self.winfo_width()*0.03), height=int(self.winfo_height()*0.01), command=lambda: self.grid.setup(EASY))
				self.medium_btn = Button(self.menuframe, text="MEDIUM", width=int(self.winfo_width()*0.03), height=int(self.winfo_height()*0.01), command=lambda: self.grid.setup(MEDIUM))
				self.hard_btn = Button(self.menuframe, text="HARD", width=int(self.winfo_width()*0.03), height=int(self.winfo_height()*0.01), command=lambda: self.grid.setup(HARD))

				self.stats_frame = LabelFrame(self.menuframe, text="Statistics", bg="#c9c9c9")

				self.gamesplayed = Label(self.stats_frame, text="Games won: "+str(self.data["totalwongames"])+"\n\nTotal games played: "+str(self.data["totalgamesplayed"]), justify=LEFT, bg="#c9c9c9", pady=10)
				self.besttimes_ = Label(self.stats_frame, text="<== Best times: ==>\n\nEasy: "+str(self.data["besttimeeasy"])+"\nMedium: "+str(self.data["besttimemedium"])+"\nHard: "+str(self.data["besttimehard"]), bg="#c9c9c9", pady=7)

				self.grid.change = 0


			self.gamesplayed.config(pady=int(self.winfo_height()*0.01), padx=int(self.winfo_width()*0.01))
			self.besttimes_.config(pady=int(self.winfo_height()*0.01), padx=int(self.winfo_width()*0.01))

			self.easy_btn.config(width=int(self.winfo_width()*0.03), height=int(self.winfo_height()*0.01))
			self.medium_btn.config(width=int(self.winfo_width()*0.03), height=int(self.winfo_height()*0.01))
			self.hard_btn.config(width=int(self.winfo_width()*0.03), height=int(self.winfo_height()*0.01))

			self.gamesplayed.pack()
			self.besttimes_.pack()
			self.stats_frame.pack(side=LEFT, padx=20)

			self.easy_btn.pack(pady=6)
			self.medium_btn.pack(pady=6)
			self.hard_btn.pack(pady=6)

			self.menuframe.place(anchor=CENTER, relx=0.5, rely=0.5)

		if self.grid.state == 1:
			if self.grid.change == 1:
				try:
					self.menuframe.place_forget()
					self.stats_frame.destroy()
					self.easy_btn.destroy()
					self.medium_btn.destroy()
					self.hard_btn.destroy()
				except:
					pass

				self.btns = []
				for row in range(len(self.grid.grid)):
					self.btns.append([])
					for column in range(len(self.grid.grid[row])):
						self.btns[-1].append([Button(self.gameframe, text="  ", bg="#bec9bb", relief=GROOVE, command=partial(self.change_btn, column, row)), column, row])
				self.topbtn = Label(self.gameframe, text=self.modes[self.mode][0], fg=self.modes[self.mode][1], bg=self.modes[self.mode][2], width=len(self.btns[0])*self.modes[self.mode][3])
				self.stats = Label(self.gameframe, text=self.get_stats_label(), bg="#c9c9c9")
				self.grid.change = 0

			self.topbtn.config(text=self.modes[self.mode][0], fg=self.modes[self.mode][1], bg=self.modes[self.mode][2])
			self.stats.config(text=self.get_stats_label())
			self.topbtn.grid(row=0, column=0, columnspan=len(self.btns[0]), pady=5)#,  ipadx=len(self.btns[0])*self.modes[self.mode][3], sticky="W")
			self.stats.grid(row=1, column=0, columnspan=len(self.btns[0]), pady=(2, 5))
			for line in self.btns:
				for btn in line:
					btn[0].grid(row=btn[1]+2, column=btn[2], ipadx=10, ipady=5)

			self.gameframe.place(anchor=CENTER, relx=0.5, rely=0.5)
		self.after(50, self.draw)

	def run(self):
		self.after(50, self.draw)
		self.mainloop()

EASY = [8, 8, 15, "easy"]
MEDIUM = [10, 10, 30, "medium"]
HARD = [15, 15, 90, "hard"]

GRID = Grid()

gui = GUI(grid=GRID)
gui.run()