import math

import cv2
import mediapipe as mp
import time
import os
import numpy as np
import keyboard

from mediapipe.framework.formats import landmark_pb2
import matplotlib.pyplot as plt

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_holistic = mp.solutions.holistic

class stride_estimator:

    # TODO: getters and setters for some variables for testing purposes

    def __init__(self, file, shoe_size=0):
        self.main(file, shoe_size)

    def main(self, file, shoe_size = 0):
        """
        Main function running the pose estimation

        :param file:
        :param shoe_size:
        :return:
        """

        left_heel_previous = 0
        right_heel_previous = 0

        first_step = False
        self.to_left = False
        self.to_right = False
        left_in_front = False

        initial_setup = False
        max_step_x = 0

        left_stride = 0
        right_stride = 0

        left_step_array = []
        right_step_array = []
        self.step_array = []
        left_stride_array = []
        right_stride_array = []
        self.stride_array = []

        self.left = []
        self.right = []
        self.pos = []
        i = 0

        # For webcam input:
        # cap = cv2.VideoCapture(0)
        # cap = cv2.VideoCapture("vid2.mp4")

        if file == "":
            file = "../data/11_110_1.mp4"
            cap = cv2.VideoCapture(file)
        else:
            cap = cv2.VideoCapture(file)

        # For Video input:
        prevTime = 0

        frame_counter = 0
        shoe_pixel_calibrator = 1

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        writer = cv2.VideoWriter("res.mp4", cv2.VideoWriter.fourcc(*'DIVX'), 20, (width, height))

        # Uncomment later
        initial_shoe_pixel_size = 1
        # while True:
        #     shoe_size = input("What is your shoe size in cm? ")
        #     if shoe_size.isdigit() is True:
        #         break
        #     print("Non int value detected\n")

        # for testing, remove later
        if shoe_size == 0:
            shoe_size = 23


        with mp_pose.Pose(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as pose:

            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    break

                # Convert the BGR image to RGB.
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image.flags.writeable = False
                results = pose.process(image)

                # Draw the pose annotation on the image.
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # get the size of the image
                IMG_HEIGHT, IMG_WIDTH = image.shape[:2]

                # continue if landmark not detected
                if results.pose_landmarks is None:
                    writer.write(image) # still write the empty image
                    continue


                # get the x and y coordinates of the heel and index of both feets
                left_heel_x = results.pose_landmarks.landmark[29].x * IMG_WIDTH
                left_heel_y = results.pose_landmarks.landmark[29].y * IMG_HEIGHT
                left_index_x = results.pose_landmarks.landmark[31].x * IMG_WIDTH
                left_index_y = results.pose_landmarks.landmark[31].y * IMG_HEIGHT

                right_heel_x = results.pose_landmarks.landmark[30].x * IMG_WIDTH
                right_heel_y = results.pose_landmarks.landmark[30].y * IMG_HEIGHT
                right_index_x = results.pose_landmarks.landmark[32].x * IMG_WIDTH
                right_index_y = results.pose_landmarks.landmark[32].y * IMG_HEIGHT

                self.left.append(left_heel_x)
                self.right.append(right_heel_x)
                self.pos.append(i)
                i += 1

                #print("leftheelx: ", left_heel_x, "rightheelx: ", right_heel_x)

                # initial setup for stride estimator
                if initial_setup is False:
                    initial_setup = True

                    # check if they are walking from LTR or RTL, based on the position of the heel and index
                    # if facing right
                    if right_heel_x < right_index_x and left_heel_x < left_index_x:
                        print('to right')
                        self.to_right = True
                        if left_index_x < right_index_x:
                            left_in_front = True
                        else:
                            left_in_front = False
                    # if facing left
                    elif right_heel_x > right_index_x and left_heel_x > left_index_x:
                        print('to left')
                        self.to_left = True
                        if left_index_x > right_index_x:
                            left_in_front = True
                        else:
                            left_in_front = False
                    # if unsure, reconfigure again in the next frame
                    else:
                        print('error')
                        initial_setup = False

                # get the length of the left feet
                left_feet_length_pixels_x = abs(left_heel_x - left_index_x)
                left_feet_length_pixels_y = abs(left_heel_y - left_index_y)
                left_feet_length_pixels = math.sqrt(pow(left_feet_length_pixels_x, 2) + pow(left_feet_length_pixels_y, 2))

                # get the length of the right feet
                right_feet_length_pixels_x = abs(right_heel_x - right_index_x)
                right_feet_length_pixels_y = abs(right_heel_y - right_index_y)
                right_feet_length_pixels = math.sqrt(pow(right_feet_length_pixels_x, 2) + pow(right_feet_length_pixels_y, 2))

                # set the first size to be the bigger of the 2 feets
                if frame_counter < 1:
                    if right_feet_length_pixels > left_feet_length_pixels:
                        shoe_pixel_calibrator = right_feet_length_pixels
                    else:
                        shoe_pixel_calibrator = left_feet_length_pixels
                    frame_counter += 1

                curr_avg, shoe_pixel_calibrator = self.callibrate_shoe_pixels(left_feet_length_pixels, right_feet_length_pixels,
                                                                         shoe_pixel_calibrator)

                predicted_step_x = self.estimate_step_length(left_heel_x, left_heel_y, right_heel_x, right_heel_y,
                                                                    shoe_pixel_calibrator, shoe_size)

                #update the max step
                if max_step_x < predicted_step_x:
                    max_step_x = predicted_step_x



                # calculate the stride using the predicted step length calculated above
                # calculations is done when the subject makes a step, the previous step length of the opposite leg is added
                # eg: if left steps in front, add the current step length and the recent right step length is added
                # if walking to the right
                if self.to_right is True and self.to_left is False:
                    # if the next step has started (hence a smaller predicted step) and the distance between the heels is
                    # bigger than the average estimated shoe size
                    if predicted_step_x < max_step_x * 0.8 and abs(left_heel_x - right_heel_x) > shoe_pixel_calibrator:

                        if left_in_front:
                            left_step_array.append(max_step_x)
                        else:
                            right_step_array.append(max_step_x)
                        self.step_array.append(max_step_x)


                        first_step, left_heel_previous, left_in_front, right_heel_previous = self.calculate_stride_to_right(
                            first_step, left_heel_previous, left_in_front, left_index_x, max_step_x, right_heel_previous,
                            right_index_x, left_stride_array, right_stride_array, self.stride_array)

                        max_step_x = 0
                # if walking to the left
                elif self.to_left is True and self.to_right is False:
                    if predicted_step_x < max_step_x * 0.8 and abs(right_heel_x - left_heel_x) > shoe_pixel_calibrator:

                        if left_in_front:
                            left_step_array.append(max_step_x)
                        else:
                            right_step_array.append(max_step_x)
                        self.step_array.append(max_step_x)

                        first_step, left_heel_previous, left_in_front, right_heel_previous = self.calculate_stride_to_left(
                            first_step, left_heel_previous, left_in_front, left_index_x, max_step_x, right_heel_previous,
                            right_index_x, left_stride_array, right_stride_array, self.stride_array)

                        max_step_x = 0

                # update the stride lengths
                left_stride = int(left_heel_previous + max_step_x)
                right_stride = int(right_heel_previous + max_step_x)

                self.draw_on_video(image, left_stride, predicted_step_x, results, right_stride)

                # write into video
                writer.write(image)

                # cv2.imshow('FYP Project', image)
                # if cv2.waitKey(5) & 0xFF == ord('q'):
                #     break

                # pause the program (test stuff, remove after)
                # pause_program()

        cap.release()
        writer.release()

        # print("Left step array:", left_step_array, "Average:", sum(left_step_array) / len(left_step_array))
        # print("Right step array:", right_step_array, "Average:", sum(right_step_array) / len(right_step_array))
        # print("Step array:", self.step_array, "Average:", sum(self.step_array) / len(self.step_array))
        # print("Left stride array:", left_stride_array)
        # print("Right stride array:", right_stride_array)
        # print("Stride array:", self.stride_array)

        # for test report stuff, leave in comment during real implementation
        # self.plot_heel_pos(file)

        # put a return over here for step array and stride array
        return self.step_array, self.stride_array

    def plot_heel_pos(self, file):
        plt.plot(self.pos, self.left, label="left heel")
        plt.plot(self.pos, self.right, label="right heel")
        plt.xlabel("Time (loops)")
        plt.ylabel("X pos")
        resStr = file.split("/")
        plt.title(f"Coords of heels over time for {resStr[len(resStr) - 1]}")
        plt.legend()
        plt.show()

    def pause_program(self):
        """
        A function to pause the program

        :return:
        """
        if keyboard.is_pressed('p'):  # or isAStep(left_heel_y, right_heel_y, predicted_step_x):
            # print(left_heel_y, right_heel_y)
            time.sleep(1.5)
            # loop = True
            # while loop is True:
            #     if keyboard.is_pressed('o'):
            #         loop = False


    def draw_on_video(self, image, left_stride, predicted_step_x, results, right_stride):
        """
        A function containing code to draw onto the video

        :param image: the image to draw onto
        :param left_stride: int, the value of the left stride
        :param predicted_step_x: int, the current step value
        :param results: object, holds the values of the pose estimation model predicted from the current frame
        :param right_stride: int, the value of the right stride
        :return:
        """
        # write the lengths onto the video
        height, width = image.shape[:2]

        x_pos, y_pos = 0, 80
        # print(height, type(height))
        # print(y_pos)

        # Create a black rectangle to serve as the background
        background_color = (0, 0, 0)  # Black color
        text_bg_height = 80  # Adjust the height of the background as needed
        image[0: int(height * 0.1), x_pos:x_pos + width] = background_color

        # cv2.rectangle(image, (0,0), (x_pos+20, width), (0,0,0), 2)

        cv2.putText(image,
                    f'StepX: {predicted_step_x}cm, LStride: {left_stride}cm, RStride: {right_stride}cm',
                    (0, int(height * 0.05)), cv2.FONT_HERSHEY_PLAIN, width // 400, (0, 255, 255), 2)

        # draw the dots of the legs onto the video
        landmark_subset = landmark_pb2.NormalizedLandmarkList(
            landmark=[
                results.pose_landmarks.landmark[29],  # right heel
                results.pose_landmarks.landmark[30],  # left heel
                results.pose_landmarks.landmark[31],  # right foot index
                results.pose_landmarks.landmark[32]  # left foot index
            ]
        )
        # draw the points onto the screen, on top of the line
        mp_drawing.draw_landmarks(
            # below code in comment is to draw the entire skeleton model
            # image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            image, landmark_list=landmark_subset)


    def calculate_stride_to_left(self, first_step, left_heel_previous, left_in_front, left_index_x, max_step_x,
                                 right_heel_previous, right_index_x, left_stride_array, right_stride_array,
                                 stride_array):
        """
        Calculates the stride when walking to the left

        :param first_step: boolean
        :param left_heel_previous: int, the max distance of the previous step
        :param left_in_front: boolean
        :param left_index_x: int, the x coordinate of the left index
        :param max_step_x: int, the max step length of the most recent step
        :param right_heel_previous: int, the max distance of the previous step
        :param right_index_x: int, the x coordinate of the left index
        :return:
        """

        # if left feet in front of right feet
        if left_index_x < right_index_x and not left_in_front:
            # if it's the first step
            if left_heel_previous == 0 and not first_step:
                first_step = True
            else:
                right_heel_previous = max_step_x

            left_in_front = True
            ####
            print(int(right_heel_previous + max_step_x), "left stride")
            left_stride_array.append(int(right_heel_previous + max_step_x))
            stride_array.append(int(right_heel_previous + max_step_x))
            #time.sleep(2)


        # if right feet in front of left feet
        elif right_index_x < left_index_x and left_in_front:
            # if it's the first step
            if right_heel_previous == 0 and not first_step:
                first_step = True
            else:
                left_heel_previous = max_step_x

            left_in_front = False
            ####
            print(int(left_heel_previous + max_step_x), "right stride")
            right_stride_array.append(int(left_heel_previous + max_step_x))
            stride_array.append(int(left_heel_previous + max_step_x))
            #time.sleep(2)




        return first_step, left_heel_previous, left_in_front, right_heel_previous


    def calculate_stride_to_right(self, first_step, left_heel_previous, left_in_front, left_index_x, max_step_x,
                                  right_heel_previous, right_index_x, left_stride_array, right_stride_array,
                                  stride_array):
        """
        Calculates the stride when walking to the right

        :param first_step: boolean
        :param left_heel_previous: int, the max distance of the previous step
        :param left_in_front: boolean
        :param left_index_x: int, the x coordinate of the left index
        :param max_step_x: int, the max step length of the most recent step
        :param right_heel_previous: int, the max distance of the previous step
        :param right_index_x: int, the x coordinate of the left index
        :return:
        """

        # if left leg is in front
        if left_index_x > right_index_x and not left_in_front:
            # if it's the first step
            if left_heel_previous == 0 and not first_step:
                first_step = True
            else:
                right_heel_previous = max_step_x

            left_in_front = True
            ####
            print(int(right_heel_previous + max_step_x), "left stride")
            left_stride_array.append(int(right_heel_previous + max_step_x))
            stride_array.append(int(right_heel_previous + max_step_x))

            #time.sleep(2)

        # if right leg is in front
        elif right_index_x > left_index_x and left_in_front:
            # if it's the first step
            if right_heel_previous == 0 and not first_step:
                first_step = True
            else:
                left_heel_previous = max_step_x

            left_in_front = False
            ####
            print(int(left_heel_previous + max_step_x), "right stride")
            right_stride_array.append(int(left_heel_previous + max_step_x))
            stride_array.append(int(left_heel_previous + max_step_x))

            #time.sleep(2)

        return first_step, left_heel_previous, left_in_front, right_heel_previous


    def estimate_step_length(self, left_heel_x, left_heel_y, right_heel_x, right_heel_y, shoe_pixel_calibrator, shoe_size):
        '''
        Estimates the step length of the subject

        :param left_heel_x: x coordinate of the left heel
        :param left_heel_y: y coordinate of the left heel
        :param right_heel_x: x coordinate of the right heel
        :param right_heel_y: y coordinate of the right heel
        :param shoe_pixel_calibrator: the current average shoe pixel value
        :param shoe_size: the real length of the subject's shoe
        :return: feet_width: the length of the feet in pixels, predicted_step_x: the estimated step length
        '''
        # calculate size of feet in pixels and correlate them to irl value
        feet_width = abs(left_heel_x - right_heel_x)
        feet_height = abs(left_heel_y - right_heel_y)
        feet_distance = math.floor(
            math.sqrt((feet_height * feet_height) + (feet_width * feet_width)))

        # calculate the pixel length of the right leg
        pixel_ratio = int(shoe_size) / shoe_pixel_calibrator

        # predicted distance of the step's x axis in cm
        predicted_step_x = math.floor(feet_width * pixel_ratio)

        return predicted_step_x


    def callibrate_shoe_pixels(self, left_feet_length_pixels, right_feet_length_pixels, shoe_pixel_calibrator):
        """
        A function to calibrate the feet pixels through taking either average or the bigger of the two feets.
        Bigger is preferred because during tests, the model can misinterpret part of the shoe as the ground due to bad
        lighting. This calibration also filters out outlier values and uses the average shoe pixel size instead.

        :param left_feet_length_pixels: float, the left feet length in pixels
        :param right_feet_length_pixels: float, the right feet length in pixels
        :param shoe_pixel_calibrator: float, the current average shoe feet length
        :return:
        """
        curr_avg = (right_feet_length_pixels + left_feet_length_pixels) / 2

        # if the right foot is too small compared to the left
        if right_feet_length_pixels < left_feet_length_pixels - 2:
            curr_avg = left_feet_length_pixels
        # if left feet is too small
        elif left_feet_length_pixels < right_feet_length_pixels - 2:
            curr_avg = right_feet_length_pixels
        # if neither, use the average value

        # this part prevents outlier values (most of the time are incorrect predictions from the model)
        # from being added to the average
        # make sure the curr_avg is within a 20% range of the shoe_pixel_calibrator, which is the average
        if curr_avg < shoe_pixel_calibrator * 1.2 < curr_avg:
            shoe_pixel_calibrator += curr_avg
            shoe_pixel_calibrator /= 2

        return curr_avg, shoe_pixel_calibrator

    def isAStep(leftHeelY, rightHeelY, predictedStep):
        """
        Test function, probably delete later

        :param leftHeelY:
        :param rightHeelY:
        :param predictedStep:
        :return:
        """
        if abs(leftHeelY - rightHeelY) <= 10 and predictedStep == 40:
            return True

        return False

if __name__ == "__main__":
    se = stride_estimator("../data/dslr/DSC_0500.MOV")
    pass