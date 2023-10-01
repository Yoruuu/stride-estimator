# # Import required Libraries
# from tkinter import *
# from PIL import Image, ImageTk
# import cv2

# # Create an instance of TKinter Window or frame
# win= Tk()

# # Set the size of the window
# win.geometry("700x350")# Create a Label to capture the Video frames
# label =Label(win)
# label.grid(row=0, column=0)
# cap= cv2.VideoCapture(0)

# # Define function to show frame
# def show_frames():
#    # Get the latest frame and convert into Image
#    cv2image= cv2.cvtColor(cap.read()[1],cv2.COLOR_BGR2RGB)
#    img = Image.fromarray(cv2image)

#    # Convert image to PhotoImage
#    imgtk = ImageTk.PhotoImage(image = img)
#    label.imgtk = imgtk
#    label.configure(image=imgtk)

# # Repeat after an interval to capture continiously
# label.after(20, show_frames)

# show_frames()
# win.mainloop()

import stride_estimator as stride

import tkinter as tk
from PIL import Image, ImageTk
import cv2

import mediapipe as mp


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_holistic = mp.solutions.holistic

class MainWindow():
    def __init__(self, window, cap):
        self.count = 0

        self.window = window
        self.cap = cap
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.interval = 33 # Interval in ms to get the latest frame

        # Create canvas for image
        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height)
        self.canvas.grid(row=0, column=0)

        # Update image on canvas
        self.update_image()

    def update_image(self):
        # Get the latest frame and convert image format
        self.image = cv2.cvtColor(self.cap.read()[1], cv2.COLOR_BGR2RGB) # to RGB
        self.image = Image.fromarray(self.image) # to PIL format
        self.image = ImageTk.PhotoImage(self.image) # to ImageTk format

        # Update image
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

        # Repeat every 'interval' ms
        self.window.after(self.interval, self.update_image)




if __name__ == "__main__":
    root = tk.Tk()
    stride.main("../data/12_95_1.mp4")
    MainWindow(root, cv2.VideoCapture("res.mp4"))
    root.mainloop()