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
from machine_training import DQNAgent

data_grabber = DataGrabber()
current_size = pyautogui.size()
fishing_game = FishingMinigame()

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


# Example of usage
def train_model(max_episodes=1000, batch_size=32):
    agent = DQNAgent(state_dim=3, action_dim=2, lr=0.001, gamma=0.9, epsilon=1.0, epsilon_decay=0.995, buffer_size=10000)
    for episode in range(max_episodes):
        total_reward = 0
        fishing_game.reset()  # Reset the fishing game at the beginning of each episode
        while not fishing_game.distanceFromCatching <= 0.05 and not fishing_game.distanceFromCatching > 0.95 :
            is_fish_captured = fishing_game.bobberInBar
            fish_y = data_grabber.recent_fish_y
            bobber_top = data_grabber.bobber_top_y
            bobber_bottom = data_grabber.bobber_bottom_y

            bobber_center = (bobber_bottom + bobber_top) // 2 
            distance_from_fish = abs(bobber_center - fish_y) 

            state = [is_fish_captured, fish_y, distance_from_fish]
            
            # Agent takes action
            action = agent.act(state)
            
            # Simulate action in the environment and get reward
            reward = 0  # Default reward is 0
            if is_fish_captured:
                reward = 1

            if fishing_game.is_perfection == True and fishing_game.distanceFromCatching > 0.94:
                reward = 40
                break
            if fishing_game.distanceFromCatching > 0.94:
                reward = 20
                break

            if action == 1:
                pyautogui.mouseDown()
            else:
                pyautogui.mouseUp()
            
            # Get next state
            is_fish_captured = fishing_game.bobberInBar
            fish_y = data_grabber.recent_fish_y
            bobber_top = data_grabber.bobber_top_y
            bobber_bottom = data_grabber.bobber_bottom_y

            bobber_center = (bobber_bottom + bobber_top) // 2  # Calculate center correctly
            distance_from_fish = abs(bobber_center - fish_y)  # Ensure the distance is positive
            next_state =[is_fish_captured, fish_y, distance_from_fish]
            # Store experience and train agent
            agent.remember(state, action, reward, next_state, fishing_game.is_won)
            agent.replay(batch_size)
            


            total_reward += reward

        print(f"Episode {episode+1}, Total Reward: {total_reward}")
    with open("dqn_agent_model.pkl", 'wb') as f:
        pickle.dump(agent, f)


def main(args):
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
