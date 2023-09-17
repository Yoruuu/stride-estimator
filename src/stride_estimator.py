#Created by MediaPipe
#Modified by Augmented Startups 2021
#Pose-Estimation in 5 Minutes
#Watch 5 Minute Tutorial at www.augmentedstartups.info/YouTube
import cv2
import mediapipe as mp
import time
import os
import keyboard
from mediapipe.framework.formats import landmark_pb2

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_holistic = mp.solutions.holistic

# # For static images:
# with mp_pose.Pose(
#     static_image_mode=True,
#     model_complexity=2,
#     min_detection_confidence=0.5) as pose:
#     image = cv2.imread('4.jpg')  #Insert your Image Here
#     image_height, image_width, _  = image.shape
#     # Convert the BGR image to RGB before processing.
#     results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#     # Draw pose landmarks on the image.
#     annotated_image = image.copy()
#     mp_drawing.draw_landmarks(annotated_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
#     cv2.imwrite(r'4.png', annotated_image)

# For webcam input:
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("../data/12_55_1.mp4")
#For Video input:
prevTime = 0
with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as pose:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

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

    # get the heels
    landmark_subset = landmark_pb2.NormalizedLandmarkList(
      landmark=[
        results.pose_landmarks.landmark[29],
        results.pose_landmarks.landmark[30],
        # results.pose_landmarks.landmark[25],
        # results.pose_landmarks.landmark[26],
      ]
    )

    # draw a line that connects the landmarks together
    # poses = landmark_subset.landmark
    # for i in range(0, len(poses) - 1, 2):
    #     start_idx = [
    #         poses[i].x,
    #         poses[i].y
    #     ]
    #     end_idx = [
    #         poses[i + 1].x,
    #         poses[i + 1].y
    #     ]
    #     # IMG_HEIGHT, IMG_WIDTH = image.shape[:2]
    #     # print(start_idx)
    #
    #     cv2.line(image,
    #              # here we change coordinates to fit to the camera feed
    #              tuple(np.multiply(start_idx[:2], [
    #                  IMG_WIDTH, IMG_HEIGHT]).astype(int)),
    #              tuple(np.multiply(end_idx[:2], [
    #                  IMG_WIDTH, IMG_HEIGHT]).astype(int)),
    #              (255, 0, 0), 9)
    #
    #     a = tuple(np.multiply(start_idx[:2], [IMG_WIDTH, IMG_HEIGHT]).astype(int))
    #     b = tuple(np.multiply(end_idx[:2], [IMG_WIDTH, IMG_HEIGHT]).astype(int))
    #
    #     # length in pixels? or numpy stuff
    #     ans = "x:", abs(a[0] - b[0]), "y:", abs(a[1] - b[1])
    #     #print(ans)

    # printing stuff to the screen
    currTime = time.time()
    fps = 1 / (currTime - prevTime)
    prevTime = currTime
    cv2.putText(image, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 196, 255), 2)

    # pause the program
    if keyboard.is_pressed('p'):
      loop = True
      while loop is True:
        if keyboard.is_pressed('o'):
          loop = False
      # input("press enter in the console to continue")

    # list of landmarks
    # https://developers.google.com/mediapipe/solutions/vision/pose_landmarker#get_started
    # get the legs
    # get the heels
    landmark_subset = landmark_pb2.NormalizedLandmarkList(
      landmark=[
        results.pose_landmarks.landmark[30],  # 29 right leg
        results.pose_landmarks.landmark[32]  # 30 left leg
        # results.pose_landmarks.landmark[31],
        # results.pose_landmarks.landmark[26],
      ]
    )

    # draw the points onto the screen, on top of the line
    mp_drawing.draw_landmarks(
      # below code in comment is to draw the entire skeleton model
      # image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
      image, landmark_list=landmark_subset)

    cv2.imshow('Send Help Thanks', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()

# Learn more AI in Computer Vision by Enrolling in our AI_CV Nano Degree:
# https://bit.ly/AugmentedAICVPRO