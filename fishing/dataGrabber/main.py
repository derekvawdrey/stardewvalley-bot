import cv2
import numpy as np
import pandas as pd
import pyautogui
from PIL import ImageGrab
import threading
import time
from .models import *
import pygetwindow as gw


upperBound_s1 = np.array([200, 150, 255])
lowerBound_s1 = np.array([100, 0, 85])

upperBound_fish = np.array([50, 255, 197])
lowerBound_fish = np.array([20, 215, 147])

upperBound_chest = np.array([58, 86, 215])
lowerBound_chest = np.array([8, 36, 165])

# Makes the x coordinate of the center of the fish and of the rectangle to be in the right place
x_center_calibration_value = 10

class DataGrabber():

    # meter-bar hex color: #82e500
    # outside border color: #e8ae4e
    # fishing background color: #7ba2e8

    
    def fishFound(self, match_location):
        print("Fish found")
        self.recent_fish_x = match_location[0]
        self.recent_fish_y = match_location[1]
        self.find_fishing_meter(match_location)
        pass

    def exclamationPointFound(self, match_location):
        print("Exclamation point found - " + str(match_location))
        pass

    def get_window_position_and_size(self, window_title):
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            window = windows[0]  # Assuming there's only one window with the given title
            left, top, right, bottom = window.left, window.top, window.right, window.bottom
            return (left, top, right, bottom)
        else:
            return None
        
    def find_black_column_positions(self, x, image):
        # Convert the image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Initialize variables for tracking the longest black span
        longest_span_length = 0
        current_span_length = 0
        top_y_position = None
        bottom_y_position = None

        # Scan along the specified x-coordinate
        for y in range(gray_image.shape[0]):
            pixel_value = gray_image[y, x]

            if pixel_value == 0:  # Black pixel
                current_span_length += 1
            else:  # White pixel
                if current_span_length >= 5:
                    # Update longest span if needed
                    if current_span_length > longest_span_length:
                        longest_span_length = current_span_length
                        top_y_position = y - current_span_length
                        bottom_y_position = y - 1

                # Reset current span length
                current_span_length = 0

        # Check if the last span is the longest
        if current_span_length >= 9:
            if current_span_length > longest_span_length:
                top_y_position = gray_image.shape[0] - current_span_length
                bottom_y_position = gray_image.shape[0] - 1

        return top_y_position, bottom_y_position


    def find_fishing_meter(self, fish_location):


        try:

            window_title = "Stardew Valley"
            window_position_and_size = self.get_window_position_and_size(window_title)
            if window_position_and_size is not None:
                left, top, right, bottom = window_position_and_size

                bottom_y = float('-inf')  # Initialize to negative infinity
                top_y = float('inf')   # Initialize to positive infinity
                # Capture the screen using OpenCV
                capture_y = top

                x = fish_location[0]
                y = fish_location[1] - capture_y + 10


                screen = np.array(pyautogui.screenshot(region=(int(x), capture_y, 40, bottom-100)))
                
                screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
                
                # Black out fish
                for i in range (0, 38):
                    for j in range(y-25, y+25):
                        screen[j, i] = [0, 0, 0] 

                # Iterate over each pixel and modify it
                for i in range(screen.shape[0]):
                    for j in range(screen.shape[1]):
                        # Check if pixel is green and blue
                        if ((screen[i, j, 1] > 145 and screen[i, j, 0] < 145) or screen[i, j, 1] >= 140) and screen[i,j,0] < 200 or screen[i,j,0] <= 6:
                            screen[i, j] = [0, 0, 0]  # Set pixel to black

                top_y, bottom_y = self.find_black_column_positions(20,screen)

                # Meant to be ran in a thread
                def click_and_release():
                    pyautogui.mouseDown()
                    time.sleep(0.35)
                    pyautogui.mouseUp()


                if(bottom_y-(bottom_y-top_y)/2 > y):
                    click_and_release()
                else:
                    pyautogui.mouseUp()

                print("Bottom:", bottom_y)
                print("Top:", top_y)
        except Exception as e:
            print("ERROR:", e)
            pass
    def __init__(self):
        self.border_color = (232, 174, 78)
        self.meter_color = (130, 229, 0)
        self.bbox_size = 600
        self.recent_fish_y = 0
        self.recent_fish_x = 0
        # Define a dictionary with template images and corresponding functions
        self.template_functions = {
            "fish": {"template_path": "../assets/images/FishingGui/Fish/fish.png", "function": self.fishFound},
        }

    # Function to process screen capture
    def process_screen(self, current_size):
        # Define the size of the bounding box
        if self.recent_fish_x == 0:
            # Capture the entire screen
            screen = np.array(ImageGrab.grab(bbox=(0, 0, current_size[0], current_size[1])))
        else:
            # Limit the bounding box around the recent fish coordinates
            bbox_x2 = min(current_size[0], self.recent_fish_x + self.bbox_size // 2)
            bbox_y2 = min(current_size[1], self.recent_fish_y + self.bbox_size // 2)

            # Capture the screen within the limited bounding box
            screen = np.array(ImageGrab.grab(bbox=(0, 0, bbox_x2, bbox_y2)))

        for template_name, data in self.template_functions.items():
            template_path = data["template_path"]
            function = data["function"]

            # Read the template image
            template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
            hh, ww = template.shape[:2]

            # Extract base image and alpha channel and make alpha 3 channels
            base = template[:, :, 0:3]
            alpha = template[:, :, 3]
            alpha = cv2.merge([alpha, alpha, alpha])

            # Set threshold for template matching
            threshold = 0.95

            # Convert color space from BGR to RGB
            screen_rgb = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)

            # Do masked template matching and save correlation image
            correlation = cv2.matchTemplate(screen_rgb, base, cv2.TM_CCORR_NORMED, mask=alpha)

            # Get locations where matches exceed the threshold
            loc = np.where(correlation >= threshold)

            # Call function for each match
            for pt in zip(*loc[::-1]):
                function(pt)