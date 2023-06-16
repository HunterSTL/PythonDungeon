import pygame
import random

class Block:
    def __init__(self, ID, Name, X, Y, Mineability, Collision, Storage, Color):
        self.ID = ID
        self.Name = Name
        self.X = X
        self.Y = Y
        self.Mineability = Mineability
        self.Collision = Collision
        self.Storage = Storage
        self.Color = Color

    @classmethod
    def Create(cls, Blockname, X, Y):
        BlockDictionary = Blocks[Blockname]

        if BlockDictionary is not None:
            _Block = cls(BlockDictionary.ID, Blockname, X, Y, BlockDictionary.Mineability, BlockDictionary.Collision, BlockDictionary.Storage, BlockDictionary.Color)
            return _Block

    def Set(self, X, Y):
        self.X = X
        self.Y = Y

class Level:
    def Create(self, Rows, Columns):
        self.Rows = Rows
        self.Columns = Columns
        Grid = []
        for Y in range(Rows, 0, -1):
            Row = []
            for X in range(1, Columns + 1):
                _Block = Block.Create('Floor', X, Y)
                Row.append(_Block)
            Grid.append(Row)
        self.Grid = Grid

    def Get(self, X, Y):
        if 1 <= X <= self.Columns and 1 <= Y <= self.Rows:
            return self.Grid[self.Rows - Y][X - 1]
        else:
            return None

    def Set(self, X, Y, Blockname):
        #Create Instance of Block
        _Block = Block.Create(Blockname, X, Y)
        #Fill Coordinates on Block
        _Block.Set(X, Y)
        #Insert Block into Grid
        self.Grid[self.Rows - Y][X - 1] = _Block

        if Blockname == 'Opening':
            self.StoreOpening(_Block)

    def StoreOpening(self, Block):
        if not hasattr(self, 'Openings'):
            self.Openings = []
        self.Openings.append(Block)


Blocks = {
    'Player': Block('P', 'Player', None, None, 0, 0, 0, (255, 0, 0)),
    'Floor': Block(0, 'Floor', None, None, 0, 0, 0, (200, 200, 200)),
    'Wall': Block(1, 'Wall', None, None, 5, 1, 0, (100, 100, 100)),
    'Opening': Block(2, 'Opening', None, None, 0, 1, 0, (0, 0, 0)),
    'Chest': Block(3, 'Chest', None, None, 0, 1, 1, (140, 70, 20))
}

def CreateWalls():
    for X in range(1, GridWidth + 1):
        for Y in range(1, GridHeight + 1):
            if X == 1 or X == GridWidth or Y == 1 or Y == GridHeight:
                Level.Set(X, Y, 'Wall')
                #Create Instance of Block
                _Block = Block.Create('Wall', X, Y)
                #Fill Coordinates on Block
                _Block.Set(X, Y)
                #Make Border Walls indestructible
                _Block.Mineability = 0
                #Insert Block into Grid
                Level.Grid[Level.Rows - Y][X - 1] = _Block


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

        Block = Level.Get(X, Y)

        if Block is not None:
            if Block.Name == 'Wall':
                Level.Set(X, Y, 'Opening')


def AddRubble():
    count = 0  # Counter to keep track of added rubble

    while count < RubbleCount:
        # Generate a random line segment within the Level
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

        # Check if the line segment intersects with any openings or Levels
        Valid = True

        for _ in range(Length):
            Block = Level.Get(X, Y)
            if Block is None:
                Valid = False
                break

            if Block.Name != 'Floor' and Block.Name != 'Wall':
                Valid = False
                break
            X += DeltaX
            Y += DeltaY

        if Valid:
            # Add the line segment as walls
            X = X - DeltaX
            Y = Y - DeltaY

            for _ in range(Length):
                Level.Set(X, Y, 'Wall')
                count += 1
                X -= DeltaX
                Y -= DeltaY

        if count >= RubbleCount:
            return  # Exit the function if the desired RubbleCount is reached


def AddChests():
    EmptyBlocks = []

    # Collect all empty blocks as potential starting positions
    for X in range(1, GridWidth + 1):
        for Y in range(1, GridHeight + 1):
            Block = Level.Get(X, Y)
            if Block is not None:
                if Block.Name == 'Floor':
                    EmptyBlocks.append((X, Y))

    ChestCount = 0
    DesiredChestCount = random.randint(ChestCountMin, ChestCountMax)
    print('ChestCount: ' + str(DesiredChestCount))

    while ChestCount < DesiredChestCount:
        if not EmptyBlocks:
            break

        # Choose a random empty block from the available options
        X, Y = random.choice(EmptyBlocks)
        Block = Level.Get(X, Y)

        # Check if the chosen block touches two or more wall blocks
        WallCount = 0
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            AdjacentBlock = Level.Get(X + dx, Y + dy)
            if AdjacentBlock is not None and AdjacentBlock.Name == 'Wall':
                WallCount += 1

        if WallCount >= 3:
            # Place the chest block
            Level.Set(X, Y, 'Chest')
            ChestCount += 1

        # Remove the chosen block from the list of empty blocks
        EmptyBlocks.remove((X, Y))


def CreateLevel():
    CreateWalls()
    AddOpenings()
    AddRubble()
    AddChests()


def PlacePlayer():
    global PlayerPosition
    EmptyBlocks = []

    # Collect all empty blocks as potential starting positions
    for X in range(1, GridWidth + 1):
        for Y in range(1, GridHeight + 1):
            Block = Level.Get(X, Y)
            if Block is not None:
                if Block.Name == 'Floor':
                    EmptyBlocks.append((X, Y))

    # Choose a random empty block from the available options
    if EmptyBlocks:
        PlayerPosition = random.choice(EmptyBlocks)

    # Set the chosen position as the player's starting point
    X, Y = PlayerPosition
    Level.Set(X, Y, 'Player')


def DebugScreen():
    for Row in Level.Grid:
        RowString = ''.join([str(Block.Mineability) for Block in Row])
        print(RowString)
    print('-' * GridWidth)


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


def HandleCollision(X, Y):
    Block = Level.Get(X, Y)
    print('Coordinates: ' + str(X) + '|' + str(Y))
    print('Block: ' + str(Block.X) + '|' + str(Block.Y))

    if Block is not None:
        if Block.Mineability > 1:
            print(str(Block.Mineability))
            Block.Mineability -= 1
            RGB = list(Block.Color)
            RGB[0] = RGB[0] // 1.2
            RGB[1] = RGB[1] // 1.2
            RGB[2] = RGB[2] // 1.2
            Block.Color = (RGB[0], RGB[1], RGB[2])
        elif Block.Mineability == 1:
            print(str(Block.Mineability))
            Level.Set(X, Y, 'Floor')
        else:
            return


def MovePlayer(DeltaX, DeltaY):
    global PlayerPosition
    X, Y = PlayerPosition
    NewX = X + DeltaX
    NewY = Y + DeltaY
    Block = Level.Get(NewX, NewY)

    if Block is None:
        return

    if Block.Collision == 0:
        Level.Set(X, Y, 'Floor')
        Level.Set(NewX, NewY, 'Player')
        PlayerPosition = (NewX, NewY)
    else:
        HandleCollision(NewX, NewY)


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

        for Y, Row in enumerate(Level.Grid):
            for X, Block in enumerate(Row):
                if Block is not None:
                    if Block.Name == 'Player':
                        DrawPlayer(Screen, X, Y)
                    else:
                        Square = pygame.Rect(X * GridScaling, Y * GridScaling, GridScaling, GridScaling)
                        pygame.draw.rect(Screen, Block.Color, Square)

        pygame.display.flip()
        Clock.tick(60)


Debug = 1
GridWidth = 30
GridHeight = 20
GridScaling = 25
RubbleCount = GridWidth * GridHeight // 3
ChestCountMin = 1
ChestCountMax = 5

Level = Level()
Level.Create(GridHeight, GridWidth)

CreateLevel()
PlacePlayer()
UpdateScreen()
