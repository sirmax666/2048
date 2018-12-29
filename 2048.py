from pynput.keyboard import Key, Listener
import sys
import random
import os
import time
from threading import Thread

class Slot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.value = ''
        self.immutable = False
        self.neighbors = {
            "up": None,
            "down": None,
            "left": None,
            "right": None
        }

class Mover(Thread):
    def __init__(self, grid, column, direction, col_nb):
        Thread.__init__(self)
        self.grid = grid
        self.column = column
        self.direction = direction
        self.col_nb = col_nb
    
    def run(self):
        print('COLUMN # {}'.format(self.col_nb))
        for slot in self.column:
            if slot.value:
                current = slot
                next_slot = current.neighbors[self.direction]
                while True:
                    if next_slot == 'LIMIT':
                        break
                    elif next_slot.value == '':
                        self.grid.matrix[next_slot.y][next_slot.x].value = current.value
                        self.grid.matrix[current.y][current.x].value = ''
                        self.grid.print_matrix()
                        time.sleep(0.025)
                    elif next_slot.value == current.value and not next_slot.immutable and not current.immutable:
                        self.grid.matrix[next_slot.y][next_slot.x].value = current.value * 2
                        self.grid.matrix[next_slot.y][next_slot.x].immutable = True
                        self.grid.matrix[current.y][current.x].value = ''
                        self.grid.print_matrix()
                        time.sleep(0.025)
                    current = self.grid.matrix[next_slot.y][next_slot.x]
                    next_slot = current.neighbors[self.direction]
        self.grid._Grid__reset_immutables()


class Grid:
    def __init__(self, size):
        self.size = size
        self.matrix = self.__init_matrix()
    
    def __cls(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def __init_matrix(self):
        matrix = []
        for y in range(self.size):
            line = []
            for x in range(self.size):
                line.append(Slot(x, y))
            matrix.append(line)
        return matrix
    
    def __reset_neighbors(self):
        for y in range(self.size):
            for x in range(self.size):
                if 0 <= (y - 1) < self.size:
                    self.matrix[y][x].neighbors['up'] = self.matrix[y - 1][x]
                else:
                    self.matrix[y][x].neighbors['up'] = 'LIMIT'
                if 0 <= (y + 1) < self.size:
                    self.matrix[y][x].neighbors['down'] = self.matrix[y + 1][x]
                else:
                    self.matrix[y][x].neighbors['down'] = 'LIMIT'
                if 0 <= (x - 1) < self.size:
                    self.matrix[y][x].neighbors['left'] = self.matrix[y][x - 1]
                else:
                    self.matrix[y][x].neighbors['left'] = 'LIMIT'
                if 0 <= (x + 1) < self.size:
                    self.matrix[y][x].neighbors['right'] = self.matrix[y][x + 1]
                else:
                    self.matrix[y][x].neighbors['right'] = 'LIMIT'
    
    def print_matrix(self):
        self.__cls()
        sep = '-' * (self.size * 5 + 1)
        print(sep)
        for line in self.matrix:
            for e in line:
                sys.stdout.write('|' + str(e.value).rjust(4))
            sys.stdout.write('|\n')
            print(sep)
    
    def print_matrix_coord(self):
        sep = '-' * (self.size * 5 + 1)
        print(sep)
        for line in self.matrix:
            for e in line:
                sys.stdout.write('|' + str(e.value).rjust(4))
                sys.stdout.write('|' + "({},{})".format(e.y, e.x))
            sys.stdout.write('|\n')
            print(sep)
    
    def move(self, direction):
        self.__reset_neighbors()
        slot_list = []
        for i in range(self.size):
            if direction in ['up', 'down']:
                slots = self.__extract_column(i)
            else:
                slots = self.__extract_row(i)
            if direction in ['down', 'right']:
                slots.reverse()
            slot_list.append(slots)
        
        thread_1 = Mover(self, slot_list[0], direction, 0)
        thread_2 = Mover(self, slot_list[1], direction, 1)
        thread_3 = Mover(self, slot_list[2], direction, 2)
        thread_4 = Mover(self, slot_list[3], direction, 3)
        print("Starting threads")
        thread_1.start()
        thread_2.start()
        thread_3.start()
        thread_4.start()
        
        thread_1.join()
        thread_2.join()
        thread_3.join()
        thread_4.join()
        
        self.__add_random_number()
    
    def __add_random_number(self):
        # Locate all empty slots
        empty_slots = []
        for line in self.matrix:
            for slot in line:
                if not slot.value:
                    empty_slots.append(slot)
        if empty_slots:
            slot = random.choice(empty_slots)
            number = random.choice([2, 4])
            slot.value = number
    
    def __switch(self, a, b):
        self.matrix[a[0]][a[1]] = self.matrix[b[0]][b[1]]
        self.matrix[b[0]][b[1]] = ''
    
    def __extract_column(self, col_nb):
        return [line[col_nb] for line in self.matrix]
    
    def __extract_row(self, row_nb):
        return [e for e in self.matrix[row_nb]]
    
    def __reset_immutables(self):
        for x in range(self.size):
            for y in range(self.size):
                self.matrix[y][x].immutable = False


def on_press(key):
    return None


def on_release(key):
    global g
    if key == Key.esc:
        # Stop listener
        return False
    elif key == Key.up:
        g.move('up')
        g.print_matrix()
    elif key == Key.down:
        g.move('down')
        g.print_matrix()
    elif key == Key.left:
        g.move('left')
        g.print_matrix()
    elif key == Key.right:
        g.move('right')
        g.print_matrix()


g = Grid(4)
g.print_matrix()

with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

