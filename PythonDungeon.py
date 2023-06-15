import pygame
import numpy as np
import random
import math

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
        if 1 <= X <= self.Columns and 1 <= Y <= self.Rows:
            return self.Grid[self.Rows - Y][X - 1]
        else:
            return None

    def Set(self, X, Y, ID):
        self.Grid[self.Rows - Y][X - 1] = ID

        # if ID equals 2 (=Opening) store Coordinates of Opening with method StoreOpenings
        if ID == 2:
            self.StoreOpening(X, Y)

    def StoreOpening(self, X, Y):
        if not hasattr(self, 'Openings'):
            self.Openings = []
        self.Openings.append((X, Y))


Debug = 0
GridWidth = 30
GridHeight = 20
GridScaling = 20
RubbleCount = GridWidth * GridHeight // 4

Grid = GridObject()
Grid.Create(GridHeight, GridWidth)

Icon = {
    0: (200, 200, 200),  # Floor block (light grey)
    1: (100, 100, 100),  # Wall block (dark grey)
    2: (255, 255, 255),  # Opening block (white)
    'P': (255, 0, 0)     # Player block (red)
}

PlayerPosition = (GridWidth // 2, GridHeight // 2)  # Initial player position


def CreateWalls():
    for X in range(1, GridWidth + 1):
        for Y in range(1, GridHeight + 1):
            if X == 1 or X == GridWidth or Y == 1 or Y == GridHeight:
                Grid.Set(X, Y, 1)


def AddOpenings():
    for Wall in range(1, 5):
        if Wall == 1:
            Y = 1
            X = random.randint(2, GridWidth - 1)
        elif Wall == 2:
            X = GridWidth
            Y = random.randint(2, GridHeight - 1)
        elif Wall == 3:
            Y = GridHeight
            X = random.randint(2, GridWidth - 1)
        elif Wall == 4:
            X = 1
            Y = random.randint(2, GridHeight - 1)

        if Grid.Get(X, Y) == 1:
            Grid.Set(X, Y, 2)


def AddRubble():
    count = 0  # Counter to keep track of added rubble

    while count < RubbleCount:
        # Generate a random line segment within the grid
        if random.random() < 0.5:
            # Horizontal line
            X = random.randint(2, GridWidth - 1)
            Y = random.randint(2, GridHeight - 1)
            Length = random.randint(1, GridWidth // 2)
            DeltaX = 1
            DeltaY = 0
        else:
            # Vertical line
            X = random.randint(2, GridWidth - 1)
            Y = random.randint(2, GridHeight - 1)
            Length = random.randint(1, GridHeight // 2)
            DeltaX = 0
            DeltaY = 1

        # Check if the line segment intersects with any openings or rooms
        is_valid = True

        for _ in range(Length):
            if Grid.Get(X, Y) != 0 and Grid.Get(X, Y) != 1:
                is_valid = False
                break
            X += DeltaX
            Y += DeltaY

        if is_valid:
            # Add the line segment as walls
            X = X - DeltaX
            Y = Y - DeltaY

            for _ in range(Length):
                Grid.Set(X, Y, 1)
                count += 1
                X -= DeltaX
                Y -= DeltaY

        if count >= RubbleCount:
            return  # Exit the function if the desired RubbleCount is reached


def CreateLevel():
    CreateWalls()
    AddOpenings()
    AddRubble()


def PlacePlayer():
    global PlayerPosition
    EmptyBlocks = []

    # Collect all empty blocks as potential starting positions
    for X in range(1, GridWidth + 1):
        for Y in range(1, GridHeight + 1):
            if Grid.Get(X, Y) == 0:
                EmptyBlocks.append((X, Y))

    # Choose a random empty block from the available options
    if EmptyBlocks:
        PlayerPosition = random.choice(EmptyBlocks)

    # Set the chosen position as the player's starting point
    X, Y = PlayerPosition
    Grid.Set(X, Y, 'P')


def DebugScreen():
    for Row in Grid.Grid:
        RowString = ''.join([str(ID) for ID in Row])
        print(RowString)


def DrawPlayer(Screen, X, Y):
    PlayerColor = (255, 0, 0)  # Red color
    EyeColor = (0, 0, 0)  # Black eye color
    MouthColor = (0, 0, 0)  # Black mouth color

    # Draw the player body (red square)
    body_rect = pygame.Rect(X * GridScaling, Y * GridScaling, GridScaling, GridScaling)
    pygame.draw.rect(Screen, PlayerColor, body_rect)

    # Calculate the positions for the eyes and mouth
    EyeRadius = GridScaling // 5
    EyeY = Y * GridScaling + GridScaling // 3
    EyeLeftX = X * GridScaling + GridScaling // 4
    EyeRightX = X * GridScaling + GridScaling // 4 * 3
    mouth_y = Y * GridScaling + GridScaling // 2 + GridScaling // 4

    # Draw the eyes (black circles)
    pygame.draw.circle(Screen, EyeColor, (EyeLeftX, EyeY), EyeRadius)
    pygame.draw.circle(Screen, EyeColor, (EyeRightX, EyeY), EyeRadius)

    # Draw the mouth (black line)
    MouthStartX = X * GridScaling + GridScaling // 4
    MouthEndX = X * GridScaling + GridScaling // 4 * 3
    pygame.draw.line(Screen, MouthColor, (MouthStartX, mouth_y), (MouthEndX, mouth_y), 2)


def MovePlayer(DeltaX, DeltaY):
    global PlayerPosition
    X, Y = PlayerPosition
    NewX = X + DeltaX
    NewY = Y + DeltaY

    if Grid.Get(NewX, NewY) == 0:
        Grid.Set(X, Y, 0)
        Grid.Set(NewX, NewY, 'P')
        PlayerPosition = (NewX, NewY)


def UpdateScreen():
    pygame.init()
    ScreenWidth = GridWidth * GridScaling
    ScreenHeight = GridHeight * GridScaling
    Screen = pygame.display.set_mode((ScreenWidth, ScreenHeight))
    Clock = pygame.time.Clock()

    if Debug == 1:
        DebugScreen()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    MovePlayer(0, 1)
                elif event.key == pygame.K_DOWN:
                    MovePlayer(0, -1)
                elif event.key == pygame.K_LEFT:
                    MovePlayer(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    MovePlayer(1, 0)
                if Debug == 1:
                    DebugScreen()

        Screen.fill((0, 0, 0))

        for Y, Row in enumerate(Grid.Grid):
            for X, ID in enumerate(Row):
                if ID == 'P':
                    DrawPlayer(Screen, X, Y)
                else:
                    Square = pygame.Rect(X * GridScaling, Y * GridScaling, GridScaling, GridScaling)
                    pygame.draw.rect(Screen, Icon[ID], Square)

        pygame.display.flip()
        Clock.tick(60)


CreateLevel()
PlacePlayer()
UpdateScreen()
