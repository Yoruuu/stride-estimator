import math

import cv2
import mediapipe as mp
import time
import os
import numpy as np
import keyboard

from mediapipe.framework.formats import landmark_pb2

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_holistic = mp.solutions.holistic


def main():
    maxX = 0
    maxY = 0

    '''
  # For static images:
  with mp_pose.Pose(
      static_image_mode=True,
      model_complexity=2,
      min_detection_confidence=0.5) as pose:
      image = cv2.imread('ballerina_test.jpg')  #Insert your Image Here
      image_height, image_width, _  = image.shape
      # Convert the BGR image to RGB before processing.
      results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
      # Draw pose landmarks on the image.
      annotated_image = image.copy()
      mp_drawing.draw_landmarks(annotated_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

      print(results.pose_landmarks)

      cv2.imwrite(r'4.png', annotated_image)

      ########
      # https://github.com/google/mediapipe/issues/2031
      # ############

      landmark_subset = landmark_pb2.NormalizedLandmarkList(
          landmark=[
              results.pose_landmarks.landmark[29],
              results.pose_landmarks.landmark[30],
              results.pose_landmarks.landmark[31],
              results.pose_landmarks.landmark[32],
          ]
      )
      annotated_image = image.copy()
      mp_drawing.draw_landmarks(
          image=annotated_image,
          landmark_list=landmark_subset)
      #cv2.imshow(annotated_image)

      cv2.imwrite(r'res.png', annotated_image)
  '''

    # For webcam input:
    # cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture("vid2.mp4")
    cap = cv2.VideoCapture("../data/12_55_1.mp4")
    # For Video input:
    prevTime = 0


    frame_counter = 0
    shoe_pixel_calibrator = 1
    ##Uncomment later
    initial_shoe_pixel_size = 1
    # while True:
    #     shoe_size = input("What is your shoe size in cm? ")
    #     if shoe_size.isdigit() is True:
    #         break
    #     print("Non int value detected\n")
    shoe_size = 23

    # sr = cv2.dnn_superres.DnnSuperResImpl()
    # path = "EDSR_x3.pb"
    # sr.readModel(path)
    # sr.setModel("edsr", 3)

    # need m and f?

    with mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                break

            # image = sr.upsample(image)

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

            # get the x and y coordinates of certain landmarks
            head = results.pose_landmarks.landmark[0].y * IMG_HEIGHT

            left_heelX = results.pose_landmarks.landmark[29].x * IMG_WIDTH
            left_heelY = results.pose_landmarks.landmark[29].y * IMG_HEIGHT
            left_indexX = results.pose_landmarks.landmark[31].x * IMG_WIDTH
            left_indexY = results.pose_landmarks.landmark[31].y * IMG_HEIGHT

            right_heelX = results.pose_landmarks.landmark[30].x * IMG_WIDTH
            right_heelY = results.pose_landmarks.landmark[30].y * IMG_HEIGHT
            right_indexX = results.pose_landmarks.landmark[32].x * IMG_WIDTH
            right_indexY = results.pose_landmarks.landmark[32].y * IMG_HEIGHT

            # get the length of the left feet
            left_feet_length_pixelsX = abs(left_heelX - left_indexX)
            left_feet_length_pixelsY = abs(left_heelY - left_indexY)
            left_feet_length_pixels = math.sqrt(pow(left_feet_length_pixelsX, 2) + pow(left_feet_length_pixelsY, 2))

            # get the length of the right feet
            right_feet_length_pixelsX = abs(right_heelX - right_indexX)
            right_feet_length_pixelsY = abs(right_heelY - right_indexY)
            right_feet_length_pixels = math.sqrt(pow(right_feet_length_pixelsX, 2) + pow(right_feet_length_pixelsY, 2))

            # print(initial_shoe_pixel_size, right_feet_length_pixels, left_feet_length_pixels)
            # issue: how do we calibrate for a constant feet pixel length
            # for the first 30 frames, add then average
            # first 30 coz we assume the person is standing still

            frame_used = 60

            ##set the first size to be the bigger of the 2 feets
            if frame_counter < 1:
                if right_feet_length_pixels > left_feet_length_pixels:
                    shoe_pixel_calibrator = right_feet_length_pixels
                else:
                    shoe_pixel_calibrator = left_feet_length_pixels

            # if frame_counter < frame_used:
            #     if avg < shoe_pixel_calibrator + 5 and avg > shoe_pixel_calibrator - 5:
            #         shoe_pixel_calibrator += avg
            #         shoe_pixel_calibrator /= 2
            #     frame_counter += 1
            # elif frame_counter == frame_used:
            #     initial_shoe_pixel_size = shoe_pixel_calibrator

            # callibration part
            #
            avg = (right_feet_length_pixels + left_feet_length_pixels) / 2
            # if the right foot is too small compared to the left
            if (right_feet_length_pixels < left_feet_length_pixels - 2):
                avg = left_feet_length_pixels
            elif (left_feet_length_pixels < right_feet_length_pixels - 2):
                avg = right_feet_length_pixels
            else:
                avg = (right_feet_length_pixels + left_feet_length_pixels) / 2

            # only allow values near the current average to contribute to the average calculation
            # constant update rather than initial calibration
            if avg < shoe_pixel_calibrator + 3 and avg > shoe_pixel_calibrator - 3:
                shoe_pixel_calibrator += avg
                shoe_pixel_calibrator /= 2

            # calculate size of feet in pixels and corelate them to irl value
            feet_width = abs(left_heelX - right_heelX)
            feet_height = abs(left_heelY - right_heelY)
            feet_distance = math.floor(
                math.sqrt((feet_height * feet_height) + (feet_width * feet_width)))

            # calculate the pixel length of the right leg
            pixel_ratio = int(shoe_size) / shoe_pixel_calibrator

            # predicted distance of the step's x axis in cm
            predicted_step_x = math.floor(feet_width * pixel_ratio)

            # a: feet_width, b: 7cm (heel to heel)
            # c = sqrt(feet_width^2 + 7^2)

            heel_to_heel = 7
            # predicted distance of the step from one heel to another
            # ideal value for c: 40.61cm (1 line), 56.57cm (2 line)
            predicted_step_pythagorus = math.floor(
                math.sqrt((feet_width * feet_width) + (heel_to_heel * heel_to_heel)))

            cv2.putText(image, f'StepX: {predicted_step_x}cm, StepP: {predicted_step_pythagorus}cm',
                        (20, 70), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 0), 2)

            print(
                f'Pixel ratio: {pixel_ratio}, Shoe calibrator: {shoe_pixel_calibrator}, Avg: {avg}. StepX: {predicted_step_x}cm')

            # #probably irrelevant
            # #print the longest length in pixels to the console
            # #change this to display pythagorus instead of x
            # if (feet_width > maxX):
            #     maxX = feet_width
            #     maxY = math.floor(abs(left_heelY - right_heelY))
            #     print("max distance in pixels: ", maxX * pixel_to_height, maxY * pixel_to_height)

            # list of landmarks
            # https://developers.google.com/mediapipe/solutions/vision/pose_landmarker#get_started
            # get the legs and the head
            # get the heels
            landmark_subset = landmark_pb2.NormalizedLandmarkList(
                landmark=[
                    ##results.pose_landmarks.landmark[0],
                    results.pose_landmarks.landmark[29],  # 29 right leg
                    results.pose_landmarks.landmark[30],
                    results.pose_landmarks.landmark[31],
                    results.pose_landmarks.landmark[32]
                    # results.pose_landmarks.landmark[25],
                    # results.pose_landmarks.landmark[26],
                ]
            )

            # draw the points onto the screen, on top of the line
            mp_drawing.draw_landmarks(
                # below code in comment is to draw the entire skeleton model
                # image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                image, landmark_list=landmark_subset)

            cv2.imshow('FYP Project', image)
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

            # pause the program
            if keyboard.is_pressed('p') or isAStep(left_heelY, right_heelY, predicted_step_x):
                # print(left_heelY, right_heelY)
                loop = True
                while loop is True:
                    if keyboard.is_pressed('o'):
                        loop = False
    cap.release()


def isAStep(leftHeelY, rightHeelY, predictedStep):
    if abs(leftHeelY - rightHeelY) <= 10 and predictedStep == 40:
        return True
    return False


# Learn more AI in Computer Vision by Enrolling in our AI_CV Nano Degree:
# https://bit.ly/AugmentedAICVPRO

# Created by MediaPipe
# Modified by Augmented Startups 2021
# Pose-Estimation in 5 Minutes
# Watch 5 Minute Tutorial at www.augmentedstartups.info/YouTube
# https://www.augmentedstartups.com/Pose-Estimation

if __name__ == "__main__":
    main()