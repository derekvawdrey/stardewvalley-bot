from dataGrabber import DataGrabber
import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab

dataGrabber = DataGrabber()

current_size = pyautogui.size()

while True:
    # Process the screen for each template
    dataGrabber.process_screen(current_size)