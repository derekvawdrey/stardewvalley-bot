import threading
import argparse
import time
import pyautogui
from fishing_minigame import FishingMinigame
from machine_training import Agent
from data_grabber import DataGrabber

# Constants
REWARD_HIT = 0.1
REWARD_MISS = -0.1
REWARD_IN_BOBBER = 0.15
ACTION_MOUSE_DOWN = 0
ACTION_MOUSE_UP = 1

record = 0
score = 0

def get_reward(action, bobber_center, bobber_in_bar, fish_y):
    print("Bobber Center", bobber_center, "Bobber in bar", bobber_in_bar, "fish y",fish_y)

    if bobber_in_bar:
        return REWARD_IN_BOBBER
    elif bobber_center < fish_y and action[ACTION_MOUSE_DOWN] == 1:
        return REWARD_MISS
    elif bobber_center < fish_y and action[ACTION_MOUSE_UP] == 1:
        return REWARD_HIT
    elif bobber_center > fish_y and action[ACTION_MOUSE_DOWN] == 1:
        return REWARD_HIT
    elif bobber_center > fish_y and action[ACTION_MOUSE_UP] == 1:
        return REWARD_MISS
    return 0

def train_model(fishing_game, agent, data_grabber):
    global score
    global record

    fishing_game.wait = False
    reward = 0
    state_old = agent.get_state()
    action = agent.get_action(state_old)
    
    if action[0] == 1:
        fishing_game.mouse_down = True
    else:
        fishing_game.mouse_down = False

    reward += get_reward(action, data_grabber.bobber_center, fishing_game.bobberInBar, data_grabber.recent_fish_y)
    print(action, reward)
    score += reward
    state_new = agent.get_state()

    agent.train_short_memory(state_old, action, reward, state_new, fishing_game.is_ended())
    agent.remember(state_old, action, reward, state_new, fishing_game.is_ended())

    if fishing_game.is_ended():
        fishing_game.wait = True
        fishing_game.reset()
        agent.n_games += 1
        agent.train_long_memory()

        if score > record:
            record = score
            agent.model.save()

        print("Game", agent.n_games, "Score", score, 'Record', record)
        score = 0

def main(args):
    data_grabber = DataGrabber()
    current_size = pyautogui.size()
    fishing_game = FishingMinigame()
    agent = Agent(fishing_game, data_grabber)

    if args.train:
        fishing_game.training = True

    fishing_game.startSimulationProgram()
    while True:
        data_grabber.process_screen(current_size)
        fishing_game.run()
        train_model(fishing_game, agent, data_grabber)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tasks concurrently or train a model.")
    parser.add_argument("--train", action="store_true", help="Train the model instead of running tasks concurrently")
    args = parser.parse_args()
    main(args)
