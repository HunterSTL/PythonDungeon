import pygame
import random
from CaveSimulation import CaveSimulation

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

    def Set(self, X, Y, Level):
        self.X = X
        self.Y = Y
        #Insert Block into Grid
        Level.Grid[Level.Rows - Y][X - 1] = self

class Level:
    def __init__(self, GridHeight, GridWidth):
        self.Create(GridHeight, GridWidth)

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
        self.Build()
        self.PlacePlayer()

    def Get(self, X, Y):
        if 1 <= X <= self.Columns and 1 <= Y <= self.Rows:
            return self.Grid[self.Rows - Y][X - 1]
        else:
            return None

    def Set(self, X, Y, Blockname):
        _Block = Block.Create(Blockname, X, Y)
        _Block.Set(X, Y, self)

        if Blockname == 'Opening':
            self.StoreOpening(_Block)

    def StoreOpening(self, Block):
        if not hasattr(self, 'Openings'):
            self.Openings = []
        self.Openings.append(Block)

    def AddRubble(self):
        _CaveSimulation = CaveSimulation(GridHeight, GridWidth, GridScaling, 0.5, 3, 1)
        _CaveSimulation.simulate_grid()

        for Y in range(GridHeight):
            for X in range(GridWidth):
                if _CaveSimulation.grid[Y][X] == 1:
                    self.Set(X + 1, Y + 1, GetWallName(random.randint(1,3)))

    def CreateWalls(self):
        for X in range(1, GridWidth + 1):
            for Y in range(1, GridHeight + 1):
                if X == 1 or X == GridWidth or Y == 1 or Y == GridHeight:
                    self.Set(X, Y, 'WallBorder')

    def AddOpenings(self):
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

            Block = self.Get(X, Y)

            if Block is not None:
                if Block.Name[0:4] == 'Wall':
                    self.Set(X, Y, 'Opening')

    def AddChests(self):
        EmptyBlocks = []

        # Collect all empty blocks as potential spawns
        for X in range(1, GridWidth + 1):
            for Y in range(1, GridHeight + 1):
                Block = self.Get(X, Y)
                
                if Block is not None:
                    if Block.Name == 'Floor':
                        EmptyBlocks.append((X, Y))

        ChestCount = 0
        DesiredChestCount = random.randint(ChestCountMin, ChestCountMax)

        while ChestCount < DesiredChestCount:
            if not EmptyBlocks:
                break

            # Choose a random empty block from the available options
            X, Y = random.choice(EmptyBlocks)
            Block = self.Get(X, Y)

            # Check if the chosen block touches two or more wall blocks
            WallCount = 0
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                AdjacentBlock = self.Get(X + dx, Y + dy)
                if AdjacentBlock is not None and AdjacentBlock.Name[0:4] == 'Wall':
                    WallCount += 1

            if WallCount == 3:
                # Place the chest block
                self.Set(X, Y, 'Chest')
                ChestCount += 1

            # Remove the chosen block from the list of empty blocks
            EmptyBlocks.remove((X, Y))

    def AddGold(self):
        WallBlocks = []

        # Collect all empty blocks as potential spawns
        for X in range(1, GridWidth + 1):
            for Y in range(1, GridHeight + 1):
                Block = self.Get(X, Y)
                
                if Block is not None:
                    if Block.Name[0:4] == 'Wall':
                        WallBlocks.append((X, Y))

        GoldCount = 0
        DesiredGoldCount = random.randint(2, 4)

        while GoldCount < DesiredGoldCount:
            if not WallBlocks:
                break

            # Choose a random empty block from the available options
            X, Y = random.choice(WallBlocks)
            Block = self.Get(X, Y)

            # Check if the chosen block touches four wall blocks
            WallCount = 0
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                AdjacentBlock = self.Get(X + dx, Y + dy)
                if AdjacentBlock is not None and AdjacentBlock.Name[0:4] == 'Wall':
                    WallCount += 1

            if WallCount == 4:
                # Place the gold block
                self.Set(X, Y, 'Gold')
                GoldCount += 1

            # Remove the chosen block from the list of empty blocks
            WallBlocks.remove((X, Y))

    def PlacePlayer(self):
        EmptyBlocks = []

        # Collect all empty blocks as potential starting positions
        for X in range(1, GridWidth + 1):
            for Y in range(1, GridHeight + 1):
                Block = self.Get(X, Y)
                
                if Block is not None:
                    if Block.Name == 'Floor':
                        EmptyBlocks.append((X, Y))

        # Choose a random empty block from the available options
        if EmptyBlocks:
            SpawnBlock = random.choice(EmptyBlocks)

        # Set the chosen position as the player's starting point
        X, Y = SpawnBlock
        self.Set(X, Y, 'Player')
        Player.UpdatePosition(X, Y)
    
    def Build(self):
        self.AddRubble()
        self.CreateWalls()
        self.AddOpenings()
        self.AddChests()
        self.AddGold()

class Player:
    def __init__(self, X, Y, HP, MaxHP, Coins, Facing):
        self.X = X
        self.Y = Y
        self.HP = HP
        self.MaxHP = MaxHP
        self.Coins = Coins
        self.Difficulty = Difficulty
        self.Facing = Facing

    def AddCoins(self, Amount):
        self.Coins += Amount
        print(str(Amount) + ' Coins added')

    def UpdatePosition(self, X, Y):
        self.X = X
        self.Y = Y

Blocks = {
    'Player': Block('P', 'Player', None, None, 0, 0, 0, (255, 0, 0)),
    'Floor': Block(0, 'Floor', None, None, 0, 0, 0, (200, 200, 200)),
    'WallBorder': Block(1, 'Wall1', None, None, 0, 1, 0, (80, 80, 80)),
    'WallSoft': Block(2, 'Wall2', None, None, 5, 1, 0, (70, 70, 70)),
    'WallMedium': Block(3, 'Wall3', None, None, 10, 1, 0, (60, 60, 60)),
    'WallHard': Block(3, 'Wall3', None, None, 15, 1, 0, (50, 50, 50)),
    'Opening': Block('O', 'Opening', None, None, 0, 1, 0, (0, 0, 0)),
    'Chest': Block('C', 'Chest', None, None, 0, 1, 1, (140, 70, 20)),
    'Gold': Block('G', 'Gold', None, None, 1, 1, 0, (230, 190, 80)),
    'Debug': Block('D', 'Debug', None, None, 0, 1, 0, (200, 100, 0))
}


def GetWallName(Variant):
    if Variant == 1:
        return 'WallSoft'
    elif Variant == 2:
        return 'WallMedium'
    else:
        return 'WallHard'

def DebugScreen():
    for Row in Level.Grid:
        RowString = ''.join([str(Block.ID) for Block in Row])
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


def DrawChest(Screen, X, Y):
    WoodColor = (140, 70, 20)  # Brown
    LockColor = (155, 155, 155)  # Grey
    LineColor = (0, 0, 0)  # Black

    # Draw the wooden box
    body_rect = pygame.Rect(X * GridScaling + 2, Y * GridScaling + 2, GridScaling - 4, GridScaling - 4)
    pygame.draw.rect(Screen, WoodColor, body_rect)

    # Draw the black line
    LineY = Y * GridScaling + GridScaling // 3
    LineStartX = X * GridScaling
    LineEndX = X * GridScaling + GridScaling
    pygame.draw.line(Screen, LineColor, (LineStartX, LineY), (LineEndX, LineY), 2)

    # Draw the lock
    LineY = Y * GridScaling + GridScaling // 3
    LineStartX = X * GridScaling + GridScaling // 2 - GridScaling // 8
    LineEndX = X * GridScaling + GridScaling // 2 + GridScaling // 8
    pygame.draw.line(Screen, LockColor, (LineStartX, LineY), (LineEndX, LineY), GridScaling // 3)


def ClearMiningProgress():
    for X in range(1, GridWidth + 1):
        for Y in range(1, GridHeight + 1):
            _Block = Level.Get(X, Y)
            if _Block.Name[0:4] == 'Wall' and _Block.Name != 'WallBorder':
                _Block.Mineability = Blocks[_Block.Name].Mineability
                _Block.Color = Blocks[_Block.Name].Color


def MineBlock(Direction):
    X = Player.X
    Y = Player.Y

    #North
    if Player.Facing == 1:
        _Block = Level.Get(X, Y + 1)
    #East
    elif Player.Facing == 2:
        _Block = Level.Get(X + 1, Y)
    #South
    elif Player.Facing == 3:
        _Block = Level.Get(X, Y - 1)
    #West
    elif Player.Facing == 4:
        _Block = Level.Get(X - 1, Y)

    if _Block is not None:
        if _Block.Mineability > 1:
            _Block.Mineability -= 1
            RGB = list(_Block.Color)
            RGB[0] = RGB[0] // 0.9
            _Block.Color = (RGB[0], RGB[1], RGB[2])
        elif _Block.Mineability == 1:
            if _Block.Name == 'Gold':
                Coins = random.randint(1, 5) + Difficulty
                Player.AddCoins(Coins)
            Level.Set(_Block.X, _Block.Y, 'Floor')
        else:
            return


def MovePlayer(DeltaX, DeltaY):
    X = Player.X
    Y = Player.Y
    NewX = X + DeltaX
    NewY = Y + DeltaY
    Block = Level.Get(NewX, NewY)

    #Moving North
    if DeltaY == 1:
        Player.Facing = 1
    #Facing East
    elif DeltaX == 1:
        Player.Facing = 2
    #Facing South
    elif DeltaY == -1:
        Player.Facing = 3
    #Facing West
    elif DeltaX == -1:
        Player.Facing = 4

    if Block is None:
        return

    if Block.Collision == 0:
        Level.Set(X, Y, 'Floor')
        Level.Set(NewX, NewY, 'Player')
        Player.UpdatePosition(NewX, NewY)
        ClearMiningProgress()


def RenderUI(Screen, ScreenWidth, ScreenHeight):
    Font = pygame.font.SysFont(None, GridScaling * 2)

    #Coins
    UICoins = Font.render('Coins: ' + str(Player.Coins), True, (230, 190, 80))
    Screen.blit(UICoins, (ScreenWidth - ScreenWidth // 3, ScreenHeight - ScreenHeight // 20))

    #Healthbar
    HealthbarSize = ScreenWidth // 3
    HPFloat = Player.HP / Player.MaxHP
    Healthbar = pygame.Rect(0, GridHeight * GridScaling + GridScaling // 2, HealthbarSize, GridScaling)
    pygame.draw.rect(Screen, (200, 0, 0), Healthbar)
    Healthbar = pygame.Rect(HealthbarSize - (HealthbarSize * (1 - HPFloat)), GridHeight * GridScaling + GridScaling // 2, HealthbarSize - HealthbarSize * HPFloat, GridScaling)
    pygame.draw.rect(Screen, (50, 0, 0), Healthbar)
    
    


def UpdateScreen():
    pygame.init()
    ScreenWidth = GridWidth * GridScaling
    ScreenHeight = GridHeight * GridScaling + HotbarSize
    Screen = pygame.display.set_mode((ScreenWidth, ScreenHeight))
    Clock = pygame.time.Clock()
    pygame.key.set_repeat(200, 50)

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
                elif event.key == pygame.K_SPACE:
                    MineBlock(Player.Facing)
                if Debug == 1:
                    DebugScreen()

        Screen.fill((0, 0, 0))

        for Y, Row in enumerate(Level.Grid):
            for X, Block in enumerate(Row):
                if Block is not None:
                    if Block.Name == 'Player':
                        DrawPlayer(Screen, X, Y)
                    elif Block.Name == 'Chest':
                        DrawChest(Screen, X, Y)
                    else:
                        Square = pygame.Rect(X * GridScaling, Y * GridScaling, GridScaling, GridScaling)
                        pygame.draw.rect(Screen, Block.Color, Square)

        RenderUI(Screen, ScreenWidth, ScreenHeight)
        pygame.display.flip()
        Clock.tick(60)


Debug = 0
GridWidth = 30
GridHeight = 30
GridScaling = 25
Difficulty = 0
HotbarSize = GridScaling * 2
ChestCountMin = 1
ChestCountMax = 5

Player = Player(None, None, 10, 10, 0, 1)

Level = Level(GridHeight, GridWidth)
UpdateScreen()