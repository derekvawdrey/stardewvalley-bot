import torch 
import random
import numpy as np
from collections import deque
from .model import *

MAX_MEMORY = 100000
BATCH_SIZE = 5000
LR = 0.001

class Agent:
    def __init__(self, fishing_game, data_grabber):
        self.state = []
        self.fishing_game = fishing_game
        self.data_grabber = data_grabber

        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY) #popleft()

        self.model = Linear_QNet(5, 10, 2)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

        pass
    
    def get_state(self):
        is_fish_captured = self.fishing_game.bobberInBar
        fish_y = self.data_grabber.recent_fish_y
        bobber_top = self.data_grabber.bobber_top_y
        bobber_bottom = self.data_grabber.bobber_bottom_y
        bobber_center = (bobber_bottom + bobber_top) // 2 
        distance_from_fish = abs(bobber_center - fish_y) 
        time_in_bobber = self.fishing_game.bobberInBarTime
        return np.array([is_fish_captured, fish_y, bobber_top, bobber_bottom, distance_from_fish],dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
    
    def get_action(self, state):
        self.epsilon = 80 - self.n_games
        final_move = [0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 1)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move
    
