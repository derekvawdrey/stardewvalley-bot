import pygame
import random
import math

# Define constants for the window dimensions
WINDOW_WIDTH = 148
WINDOW_HEIGHT = 592
GAME_HEIGHT = 548

class GameTime:
    def __init__(self):
        self.elapsed_time = 0

    def tick(self, milliseconds):
        self.elapsed_time += milliseconds

class FishingMinigame:
    def __init__(self):
        #Processing

        self.mouse_down = False
        self.difficulty = 4000 # DONT KNOW WHERE VALUE COMES FROM
        self.distanceFromCatching = 0
        self.space_below = 0 # DONT KNOW WHERE VALUE COMES FROM
        self.space_above = 0 # DONT KNOW WHERE VALUE COMES FROM

        # Ranges from -1.5 to 1.5
        self.floaterSinkerAcceleration = 0.00
        self.motionType = 0

        # bobbers
        self.bobberTargetPosition = 0
        self.bobberPosition = GAME_HEIGHT
        self.bobberSpeed = 0
        self.bobberAcceleration = 0
        self.bobberInBar = True

        # bobber bar
        self.bobberBarPos = 0
        self.bobberBarSpeed = 0
        self.bobberBarHeight = 0
        

        pass
    
    
    def update_floater(self):
        if(self.motionType == 3):
            self.floaterSinkerAcceleration = max(floaterSinkerAcceleration + 0.01, 1.5)
        elif(self.motionType == 4):
            self.floaterSinkerAcceleration = max(self.floaterSinkerAcceleration - 0.01, -1.5)

    def update_bobber(self):
        if random.random() < (self.difficulty * (1 if self.motionType != 2 else 20) / 4000.0) and (self.motionType != 2 or self.bobberTargetPosition == -1.0):
            self.space_below = GAME_HEIGHT - self.bobberPosition
            self.space_above = self.bobberPosition
            self.percent = min(99.0, self.difficulty + random.randint(10, 45)) / 100.0
            self.bobberTargetPosition = self.bobberPosition + random.randint(int(-self.space_above), int(self.space_below)) * self.percent

        if abs(self.bobberPosition - self.bobberTargetPosition) > 3.0 and self.bobberTargetPosition != -1.0:
            self.bobberAcceleration = (self.bobberTargetPosition - self.bobberPosition) / (random.randint(10, 30) + (100.0 - min(100.0, self.difficulty)))
            self.bobberSpeed += (self.bobberAcceleration - self.bobberSpeed) / 5.0
        elif self.motionType != 2 and random.random() < (self.difficulty / 2000.0):
            self.bobberTargetPosition = self.bobberPosition + (random.randint(-100, -51) if random.random() < 0.5 else random.randint(50, 101))
        else:
            self.bobberTargetPosition = -1.0


        if self.motionType == 1 and random.random() < (difficulty / 1000.0):
            self.bobberTargetPosition = self.bobberPosition + (random.randint(-100 - int(difficulty) * 2, -51) if random.random() < 0.5 else random.randint(50, 101 + int(self.difficulty) * 2))

        self.bobberTargetPosition = max(-1.0, min(self.bobberTargetPosition, GAME_HEIGHT))
        self.bobberPosition += self.bobberSpeed + self.floaterSinkerAcceleration

        if self.bobberPosition > 532.0:
            self.bobberPosition = 532.0
        elif self.bobberPosition < 0.0:
            self.bobberPosition = 0.0
        
        self.bobberInBar = (self.bobberPosition + 12.0 <= self.bobberBarPos - 32.0 + self.bobberBarHeight) and (self.bobberPosition - 16.0 >= self.bobberBarPos - 32.0)

        if self.bobberPosition >= (GAME_HEIGHT - self.bobberBarHeight) and self.bobberBarPos >= (568.0 - self.bobberBarHeight - 4):
            bobberInBar = True


    def update_bobber_bar(self):
        gravity = -0.25 if self.mouse_down else 0.25
        if(self.mouse_down and gravity < 0 and (self.bobberBarPos == 0 or self.bobberBarPos == (568-self.bobberBarHeight))):
            self.bobberBarSpeed = 0
        
        if(self.bobberInBar):
            # if trapBobber: gravity *= 0.3
            # else:
            gravity *= 0.6
            # Other trabBobber stuff
        
        self.bobberBarSpeed += gravity
        self.bobberBarPos += self.bobberBarSpeed

        if(self.bobberBarPos + self.bobberBarHeight > 568):
            self.bobberBarPos = 568 - self.bobberBarHeight
            self.bobberBarSpeed = (0.00 - self.bobberBarSpeed) * (2/3)
        elif(self.bobberBarPos < 0):
            self.bobberBarPos = 0
            self.bobberBarSpeed = (0.00 - self.bobberBarSpeed) * (2/3)
        
        if(self.bobberPosition < 0):
            self.bobberPosition = 0
        elif(self.bobberPosition > GAME_HEIGHT):
            self.bobberPosition = GAME_HEIGHT
        
    def update_catching_distance(self):
        if(self.bobberInBar):
            self.distanceFromCatching += 0.002
            # Add fish shaking
        
        self.distanceFromCatching = max(0.0, min(1.0, self.distanceFromCatching))
        if(self.distanceFromCatching <= 0):
            # Die
            pass
        
        if(self.distanceFromCatching >= 1):
            # You get fish
            pass



    def update(self, time: GameTime):
        self.update_floater()
        self.update_bobber()
        self.update_bobber_bar()
        self.update_catching_distance()
        pass

    def reposition(self):
        # Implement the reposition logic here
        pass



# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Fishing Mini-game")

# Create instances of GameTime and FishingMinigame
game_time = GameTime()
fishing_minigame = FishingMinigame()

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update game time
    milliseconds = clock.tick(60)  # Limit frame rate to 60 FPS
    game_time.tick(milliseconds)

    fishing_minigame.mouse_down = pygame.mouse.get_pressed()[0]
    fishing_minigame.update(game_time)

    # Clear the screen
    screen.fill((255, 255, 255))  # Fill with white color

    # Load image
    image_path = "./assets/fishingMinigameUI.png"
    background_image = pygame.image.load(image_path)

    screen.blit(background_image, (0, 0))

    fish_path = "./assets/fish.png"
    fish_image = pygame.image.load(fish_path)

    screen.blit(fish_image, (64, fishing_minigame.bobberPosition))


    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
