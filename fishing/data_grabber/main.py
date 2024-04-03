import cv2
import numpy as np
import pandas as pd
import pyautogui
from PIL import ImageGrab, Image
import threading
import time
from .models import *
import pygetwindow as gw
from mss import mss

upperBound_fish = np.array([50, 255, 197])
lowerBound_fish = np.array([20, 215, 147])
fish_x_calibration = -20
fish_y_calibration = -20

class DataGrabber():

    # meter-bar hex color: #82e500
    # outside border color: #e8ae4e
    # fishing background color: #7ba2e8

    def __init__(self):
        self.border_color = (232, 174, 78)
        self.meter_color = (130, 229, 0)
        self.bbox_size = 600
        self.recent_fish_y = 0
        self.recent_fish_x = 0
        self.bobber_top_y = 0
        self.bobber_bottom_y = 0
        self.bobber_center = 0
        self.current_image = None
        
    
        self.template_functions = {
            "fish": {"template_path": "../assets/images/FishingGui/Fish/fish.png", "function": self.fish_found, "template" : None},
        }
    
    def fish_found(self, match_location):
        # print("Fish found")
        self.recent_fish_x = match_location[0]
        self.recent_fish_y = match_location[1]
        self.find_fishing_meter(match_location)

    def exclamationPointFound(self, match_location):
        print("Exclamation point found - " + str(match_location))

    def get_window_position_and_size(self, window_title):
        return(0,0,600,1000)

        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            window = windows[0]
            left, top, right, bottom = window.left, window.top, window.right, window.bottom
            return (left, top, right, bottom)
        else:
            return None
        
    def find_black_column_positions(self, x, image):
        """
        Find the largest black column from the processed image in find_fishing_meter
        """
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

            # Search for pixel height
            if pixel_value == 0:
                current_span_length += 1
            else:
                if current_span_length >= 5 and current_span_length > longest_span_length:
                    longest_span_length = current_span_length
                    top_y_position = y - current_span_length
                    bottom_y_position = y - 1

                # Reset current span length
                current_span_length = 0

        # Check if the last span is the longest
        if current_span_length >= 50 and current_span_length > longest_span_length:
            longest_span_length = current_span_length
            top_y_position = gray_image.shape[0] - current_span_length
            bottom_y_position = gray_image.shape[0] - 1

        self.bobber_center = top_y_position + ((top_y_position - bottom_y_position) // 2)

        return top_y_position, bottom_y_position




    def find_fishing_meter(self, fish_location):
        """
            Takes in the x and y of the fish_location, and then uses that information to identify the green
        """

        try:
            window_title = "Stardew Valley"
            window_position_and_size = self.get_window_position_and_size(window_title)
            if window_position_and_size is not None:
                left, top, right, bottom = window_position_and_size

                bottom_y = float('-inf')
                top_y = float('inf')

                capture_y = top

                x = fish_location[0]
                y = fish_location[1] - capture_y + 10


                screen = np.array(pyautogui.screenshot(region=(int(x), capture_y, 40, bottom-100)))
                screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

                # Black out fish
                screen[y-25:y+25, 0:38] = [0, 0, 0]

                # Apply condition using NumPy indexing
                condition = ((screen[:,:,1] > 145) & (screen[:,:,0] < 145)) | (screen[:,:,1] >= 140) & ((screen[:,:,0] < 200) | (screen[:,:,0] <= 6))
                screen[condition] = [0, 0, 0]

                cv2.imshow("image",screen)
                cv2.waitKey(2)


                self.bobber_top_y, self.bobber_bottom_y = self.find_black_column_positions(20,screen)

        except Exception as e:
            print("ERROR:", e)
            pass

    def capture_screenshot(self, bbox):
        # Capture entire screen
        with mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(bbox)
            return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

    def process_screen(self, current_size):
        """
        Process screen and search for anything in the template_functions, and identifies the global x,y
        """
        start_time = time.time()

        # Capture the screen
        bbox = (0, 0, 1000, 1000)
        self.current_image = np.array(self.capture_screenshot(bbox))

        img_HSV = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2HSV)
        img_fish = cv2.inRange(img_HSV, lowerBound_fish, upperBound_fish)
        fish_detected = False
        conts, hierarchy = cv2.findContours(img_fish, cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE)

        for cnt in conts:

            area = cv2.contourArea(cnt)

            if area > 25:

                (x, y), radius = cv2.minEnclosingCircle(cnt)
                fish_center_point = (int(x + fish_x_calibration), int(y + fish_y_calibration))
                fish_center_height = fish_center_point[1]
                radius = int(radius)
                fish_detected = True   
                break
            
        if fish_detected:
            self.fish_found(fish_center_point)

        # print("--- %s seconds ---" % (time.time() - start_time))
