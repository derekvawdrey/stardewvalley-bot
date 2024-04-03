from dataGrabber import DataGrabber
from fishingMinigameSim import FishingMinigame
import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
import threading
import argparse
import threading
import pickle
import time
from machine_training import Agent

data_grabber = DataGrabber()
current_size = pyautogui.size()
fishing_game = FishingMinigame()
train = False

def process_screen():
    try:
        while True:
            # Process the screen for each template
            data_grabber.process_screen(current_size)
    except KeyboardInterrupt:
        print("Stopping data grabber")

def start_simulation():
    fishing_game.startSimulationProgram()
    while fishing_game.running:
        fishing_game.run()
        # train_model step


def get_reward():
    reward = 0
    if fishing_game.bobberInBar:
        reward = 1
    return reward

# Train the neural network
def train_model():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    score = 0
    fishing_game.training = True
    
    agent = Agent(fishing_game, data_grabber)
    while True:
        fishing_game.wait = False
        reward = 0
        state_old = agent.get_state()
        action = agent.get_action(state_old)

        if action[0] == 1:
            fishing_game.mouse_down = True
        else:
            fishing_game.mouse_down = False

        reward += get_reward()
        score += reward
        state_new = agent.get_state()

        agent.train_short_memory(state_old, action, reward, state_new, fishing_game.is_ended())
        agent.remember(state_old, action, reward, state_new, fishing_game.is_ended())

        if fishing_game.is_ended():
            fishing_game.wait = True
            # train long memory
            fishing_game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print("Game", agent.n_games, "Score", score, 'Record', record)
            plot_scores.append(score)
            total_score += score
            mean_score = total_score/agent.n_games
            plot_mean_scores.append(mean_score)
            score = 0
            
    print("Training done")

def main(args):
    if args.train:
        train = args.train
    # Create threads for each function
    screen_thread = threading.Thread(target=process_screen)
    simulation_thread = threading.Thread(target=start_simulation)

    # Start both threads
    screen_thread.start()
    simulation_thread.start()

    if args.train:
        train_thread = threading.Thread(target=train_model)
        train_thread.start()

    # Wait for all threads to finish
    screen_thread.join()
    simulation_thread.join()

    if args.train:
        train_thread.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tasks concurrently or train a model.")
    parser.add_argument("--train", action="store_true", help="Train the model instead of running tasks concurrently")
    args = parser.parse_args()
    main(args)
