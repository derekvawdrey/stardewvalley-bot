import pygame
import random
import math
from enum import Enum
import os

# Define constants for the window dimensions
WINDOW_WIDTH = 148
WINDOW_HEIGHT = 592
GAME_HEIGHT = 548

class MotionType(Enum):
    MIXED = 0
    DART = 1
    SMOOTH = 2
    FLOATER = 4
    SINKER = 3



class GameTime:
    def __init__(self):
        self.elapsed_time = 0

    def tick(self, milliseconds):
        self.elapsed_time += milliseconds

class FishingMinigame:

    def reset(self):
        #Processing
        self.mouse_down = False
        self.difficulty = random.randint(50, 115) # DONT KNOW WHERE VALUE COMES FROM
        self.distanceFromCatching = 0.3
        self.space_below = 0 # DONT KNOW WHERE VALUE COMES FROM
        self.space_above = 0 # DONT KNOW WHERE VALUE COMES FROM
        self.is_game_over = False
        self.is_won = False
        self.is_perfection = True
        # Ranges from -1.5 to 1.5
        self.floaterSinkerAcceleration = 0.00
        self.motionType = self.random_motion_type()

        # bobbers
        self.bobberTargetPosition = 0
        self.bobberPosition = GAME_HEIGHT
        self.bobberSpeed = 0
        self.bobberAcceleration = 0
        self.bobberInBar = False
        self.bobberInBarTime = 0.00

        # bobber bar
        self.bobberBarPos = GAME_HEIGHT
        self.bobberBarSpeed = 0
        self.bobberBarHeight = 100

    def is_ended(self):
        if self.is_won:
            return self.is_won
        return self.is_game_over

    def __init__(self):
        self.wait = False
        self.training = False
        #Processing
        self.reset()
        
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.running = False

        pass
    
    def random_motion_type(self):
        return random.choice(list(MotionType))
    
    
    
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
            self.bobberInBarTime += 1
        else:
            self.distanceFromCatching -= 0.002
            self.bobberInBarTime = 0
            self.is_perfection = False
            # Add fish shaking
        self.distanceFromCatching = max(0.0, min(1.0, self.distanceFromCatching))
        if(self.distanceFromCatching <= 0.05):
            self.is_game_over = True
            pass
        
        if(self.distanceFromCatching >= 1):
            self.is_won = True
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


    
    def startSimulationProgram(self):
        # Initialize Pygame
        pygame.init()
        self.clock = pygame.time.Clock()

        self.barMiddle = (130,229,0)
        self.barTop = (73,193,0)
        self.barSide = (33,101,1)

        # Set up the display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Fishing Mini-game")

        # Create instances of GameTime and FishingMinigame
        self.game_time = GameTime()
        self.running = True

    def run(self):
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False


        # Update game time
        milliseconds = self.clock.tick(60)  # Limit frame rate to 60 FPS
        self.game_time.tick(milliseconds)
        if not self.training:
            self.mouse_down = pygame.mouse.get_pressed()[0]

        if not self.wait:
            self.update(self.game_time)

        # Clear the screen
        self.screen.fill((255, 255, 255))  # Fill with white color

        # Load image
        image_path = os.path.join(self.current_dir, "assets", "fishingMinigameUI.png")
        background_image = pygame.image.load(image_path)

        self.screen.blit(background_image, (0, 0))

        # Draw the bar
        pygame.draw.rect(self.screen, self.barMiddle, (64, self.bobberBarPos, 36, self.bobberBarHeight))
        pygame.draw.rect(self.screen, self.barTop, (64, self.bobberBarPos + self.bobberBarHeight - 8, 36, 4))
        pygame.draw.rect(self.screen, self.barTop, (64, self.bobberBarPos , 36, 4))
        pygame.draw.rect(self.screen, self.barSide, (64, self.bobberBarPos, 4, self.bobberBarHeight))
        pygame.draw.rect(self.screen, self.barSide, (64+36-4, self.bobberBarPos, 4, self.bobberBarHeight))
        pygame.draw.rect(self.screen, self.barSide, (64, self.bobberBarPos + self.bobberBarHeight - 4, 36, 4))
        pygame.draw.rect(self.screen, self.barSide, (64, self.bobberBarPos - 4, 36, 4))


        fish_path = os.path.join(self.current_dir, "assets", "fish.png")
        fish_image = pygame.image.load(fish_path)

        self.screen.blit(fish_image, (64, self.bobberPosition))

        # Update the display
        pygame.display.flip()
