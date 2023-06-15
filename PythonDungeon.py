import numpy as np
import random

class GridObject:
    def Create(self, Rows, Columns):
        self.Rows = Rows
        self.Columns = Columns
        Grid = []
        for y in range(Rows, 0, -1):
            Row = []
            for x in range(1, Columns + 1):
                Row.append(0)
            Grid.append(Row)
        self.Grid = Grid
                

    def Get(self, X, Y):
        return self.Grid[self.Rows - Y][X - 1]

    def Set(self, X, Y, ID):
        self.Grid[self.Rows - Y][X - 1] = ID

        #if ID equals 2 (=Opening) store Coordinates of Opening with method StoreOpenings
        if ID == 2:
            self.StoreOpening(X, Y)

    def StoreOpening(self, X, Y):
        if not hasattr(self, 'Openings'):
            self.Openings = []
        self.Openings.append((X, Y))

GridWidth = 10
GridHeight = 5
Grid = GridObject()
Grid.Create(GridHeight, GridWidth)

Icon = {
    0: '0',  #Floor block
    1: '#',  #Wall block
    2: '[]'  #Opening block
}

def AddOpenings():
    for Wall in range(1, 5):
        if(Wall == 1):
            Y = 1
            X = random.randint(2, GridWidth - 1)
        elif(Wall == 2):
            X = GridWidth
            Y = random.randint(2, GridHeight - 1)
        elif(Wall == 3):
            Y = GridHeight
            X = random.randint(2, GridWidth - 1)
        elif(Wall == 4):
            X = 1
            Y = random.randint(2, GridHeight - 1)

        if Grid.Get(X, Y) == 1:
            Grid.Set(X, Y, 2)

def CreateWalls():
    for x in range(1, GridWidth + 1):
        for y in range(1, GridHeight + 1):
            if x == 1 or x == GridWidth or y == 1 or y == GridHeight:
                Grid.Set(x, y, 1)

def CreateRoom():
    CreateWalls()
    AddOpenings()

def UpdateScreen():
    global Icon
    for Row in Grid.Grid:
        RowString = ''.join([Icon[ID] for ID in Row])
        print(RowString)

def DebugScreen():
    for Row in Grid.Grid:
        RowString = ''.join([str(ID) for ID in Row])
        print(RowString)

CreateRoom()
UpdateScreen()
print(Grid.Openings)
#DebugScreen()
