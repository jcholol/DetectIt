# PixInfo.py
# Program to start evaluating an image in python

from code import interact
from PIL import Image, ImageTk
import glob
import os
import math
import re
import cv2
import os

# Pixel Info class.


class PixInfo:

    # Constructor.
    def __init__(self, master):

        self.master = master
        self.imageList = []
        self.photoList = []
        self.xmax = 0
        self.ymax = 0
        self.colorCode = []
        self.intenCode = []

        self.extract_frames()
        # Add each image (for evaluation) into a list,
        # and a Photo from the image (for the GUI) in a list.
        # frame_tuples = []

        # for infile in glob.glob('extracted_frames/*.jpg'):
        #     file, ext = os.path.splitext(infile)

        #     # Extract the frame number using regex (assuming filenames are in the format "frame_1000.jpg")
        #     frame_number = int(re.search(r'\d+', file).group())

        #     im = Image.open(infile)
        #     # Resize the image for thumbnails.
        #     imSize = im.size
        #     x = int(imSize[0] / 3.2)
        #     y = int(imSize[1] / 3.2)
        #     imResize = im.resize((x, y), Image.LANCZOS)
        #     photo = ImageTk.PhotoImage(imResize)

        #     # Add the tuple of (frame number, photo, image) to the list
        #     frame_tuples.append((frame_number, photo, im))

        # # Sort the frame tuples based on frame numbers
        # frame_tuples.sort(key=lambda x: x[0])
        # # Unpack the sorted tuples back into separate lists
        # for frame_number, photo, im in frame_tuples:
        #     self.imageList.append(im)
        #     self.photoList.append(photo)

        #     # Update self.xmax and self.ymax if needed
        #     if x > self.xmax:
        #         self.xmax = x
        #     if y > self.ymax:
        #         self.ymax = y

        # # Create a list of pixel data for each image and add it
        # # to a list.
        # for im in self.imageList[:]:

        #     pixList = list(im.getdata())
        #     InBins = self.encode(pixList)
        #     self.intenCode.append(InBins)
        # temp = self.calculate_frame_difference()

    # Bin function returns an array of bins for each
    # image, both Intensity and Color-Code methods.
    def encode(self, pixlist):

        # 2D array initilazation for bins, initialized
        # to zero.
        InBins = [0]*26
        InBins[0] = len(pixlist)

        intensity = 0
        for i in range(len(pixlist)):
            j = 0
            r = pixlist[i][j]
            g = pixlist[i][j + 1]
            b = pixlist[i][j + 2]
            intensity = (0.299 * r) + (0.587 * g) + (0.114 * b)
            hIndex = int((intensity // 10) + 1)
            if hIndex == 26:
                InBins[hIndex - 1] += 1
            else:
                InBins[hIndex] += 1

        # Return the list of binary digits, one digit for each
        # pixel.
        return InBins

    # Method for extracting frames and storing into intensity
    def extract_frames(self):
        video_path = 'Videos/20020924_juve_dk_02a.avi'
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("Error: Unable to open the video file")
            return

        frame_tuple = []

        frame_number = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_number += 1

            if 1000 <= frame_number <= 4999:
                im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                imSize = im.size
                x = int(imSize[0])
                y = int(imSize[1])
                imResize = im.resize((x, y), Image.LANCZOS)
                photo = ImageTk.PhotoImage(imResize)
                frame_tuple.append((frame_number, photo, im))

            if frame_number >= 4999:
                break

        frame_tuple.sort(key=lambda x: x[0])

        for frame_number, photo, im in frame_tuple:
            self.imageList.append(im)
            self.photoList.append(photo)

            if x > self.xmax:
                self.xmax = x
            if y > self.ymax:
                self.ymax = y

        for im in self.imageList[:]:
            pixList = list(im.getdata())
            InBins = self.encode(pixList)
            self.intenCode.append(InBins)
    # This function is for myself, used for testing without loading video everytime

    def save_intenCode_to_file(self, filename):
        with open(filename, 'w') as file:
            for item in self.intenCode:
                file.write(' '.join(map(str, item)) + '\n')

    # Accessor functions:
    def get_imageList(self):
        return self.imageList

    def get_photoList(self):
        return self.photoList

    def get_xmax(self):
        return self.xmax

    def get_ymax(self):
        return self.ymax

    def get_colorCode(self):
        return self.colorCode

    def get_intenCode(self):
        return self.intenCode
