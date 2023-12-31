# ImageViewer.py
# Program to start evaluating an image in python
from operator import truediv
from tkinter import *
from tkinter import Tk, Frame, Checkbutton, BooleanVar
import math
import os
from turtle import clear
from PixInfo import PixInfo
from PIL import Image, ImageTk
from statistics import stdev
from copy import deepcopy
import numpy
from collections import defaultdict
import cv2
import os
import time

# Main app.


class ImageViewer(Frame):

    # Constructor.
    def __init__(self, master, pixInfo):
        Frame.__init__(self, master)
        self.master = master
        self.pixInfo = pixInfo
        self.resultWin = None

        # pixInfo.save_intenCode_to_file('intenCode.txt')
        # with open('intenCode.txt', 'r') as file:
        #     lines = file.readlines()

        # for line in lines:
        #     values = list(map(int, line.strip().split()))
        #     self.intenCode.append(values)
        self.intenCode = pixInfo.get_intenCode()
        self.cutResults = []
        self.gtResults = []
        self.frameDistance = []
        self.displayFrames = [[0, 0]]
        # Full-sized images.
        self.imageList = pixInfo.get_imageList()
        # Thumbnail sized images.
        self.photoList = pixInfo.get_photoList()
        # Image size for formatting.
        self.xmax = pixInfo.get_xmax()
        self.ymax = pixInfo.get_ymax()

        # Create Main frame.
        mainFrame = Frame(master)
        mainFrame.pack()

        # Create Picture chooser frame.
        listFrame = Frame(mainFrame)
        listFrame.pack(side=LEFT)

        # Create Control frame.
        controlFrame = Frame(mainFrame)
        controlFrame.pack(side=RIGHT)

        # Create Preview frame.
        previewFrame = Frame(mainFrame,
                             width=self.xmax, height=self.ymax)
        previewFrame.pack_propagate(0)
        previewFrame.pack(side=RIGHT)

        # Create Results frame.
        self.resultsFrame = Frame(self.resultWin)
        self.resultsFrame.pack(side=BOTTOM)

        self.canvas = Canvas(self.resultsFrame)
        self.canvas.pack()
        self.cutFrames = [[0, 0]]
        self.gtFrames = []
        self.twinComparison()

        # Loop through self.displayFrames to modify the values
        for i in range(len(self.cutFrames) - 1):
            self.cutFrames[i] = [self.cutFrames[i]
                                 [1], self.cutFrames[i + 1][0]]
        #     print("First frame # of each shot (cut):", [
        #         self.cutFrames[i][0] + 1000, self.cutFrames[i][1] + 1000])
        # print("First frame # of each shot (cut):",
        #      self.cutFrames[-1][0] + 1000)
        for i in range(len(self.gtFrames) - 1):
            self.gtFrames[i] = [self.gtFrames[i]
                                [0], self.gtFrames[i + 1][0] - 1]
            # print("First frame # of each shot (gradual transition):", [
            #    self.gtFrames[i][0] + 1000, self.gtFrames[i][1] + 1000])

        self.displayFrames = self.cutFrames + self.gtFrames

        self.displayFrames = sorted(self.displayFrames)
        # for i in range(len(self.displayFrames)):
        #     print("First frame # of each shot (combined):",
        #           [self.displayFrames[i][0] + 1000, self.displayFrames[i][1] + 1000])

        print("First frame # of each shot:")
        for i in range(len(self.displayFrames) - 1):
            curShotEnd = self.displayFrames[i][1]
            nextShotStart = self.displayFrames[i + 1][0]
            if curShotEnd >= nextShotStart:
                self.displayFrames[i][1] = self.displayFrames[i + 1][0] - 1
            print(self.displayFrames[i][0] + 1000)
        print(self.displayFrames[-1][0] + 1000)

        # print([self.displayFrames[i][0] + 1000,
        #           self.displayFrames[i][1] + 1000])
        # print(self.displayFrames[-1][0] + 1000,
        #       self.displayFrames[-1][1] + 1000)
        # Layout Picture Listbox.
        self.listScrollbar = Scrollbar(listFrame)
        self.listScrollbar.pack(side=RIGHT, fill=Y)
        self.list = Listbox(listFrame,
                            yscrollcommand=self.listScrollbar.set,
                            selectmode=BROWSE,
                            bg="white",
                            height=10)
        for i in range(len(self.displayFrames)):
            index = self.displayFrames[i][0]
            # print("index: ", index + 1000)
            name = "frame #" + str(index + 1000)
            self.list.insert(i, name)
        self.list.pack(side=TOP, fill=BOTH)
        self.list.activate(0)
        self.list.bind('<<ListboxSelect>>', self.update_preview)
        self.listScrollbar.config(command=self.list.yview)

        # Layout Preview.
        self.selectImg = Label(previewFrame,
                               image=self.photoList[0])
        self.selectImg.pack(side="top", fill="both", expand=True)
        self.selectImageIndex = 0
        self.playVideo = Button(
            controlFrame, text="Play Video", command=lambda: self.play_video())
        self.playVideo.pack(side=BOTTOM)
        self.create_main_frame()

    # Create the main frame with Picture Listbox and Control Frame
    def create_main_frame(self):
        self.canvas.delete(ALL)
        mainFrame = Frame(self.master)
        mainFrame.pack()
    # Handle the "Color-Code" button click

    def update_preview(self, event):
        i = self.list.curselection()[0]
        self.selectImageIndex = self.displayFrames[i]
        self.selectImg.configure(
            image=self.photoList[int(self.selectImageIndex[0])])

    # Find the Manhattan Distance of each image and return a
    # list of distances between image i and each image in the
    # directory uses the comparison method of the passed
    # binList
    def twinComparison(self):
        # Get frame-to-frame difference
        for i in range(len(self.intenCode) - 1):
            distance = 0
            for j in range(1, 26):
                distance += abs((self.intenCode[i]
                                [j]) - self.intenCode[i + 1][j])
            self.frameDistance.append(distance)
        # calculate the mean, std for threshold values
        mean = sum(self.frameDistance) // len(self.frameDistance)
        std = stdev(self.frameDistance)
        # Setting the thresholds, Tb = cut, Ts = Gradual Transition
        Tb = round(mean + std * 11)
        Ts = round(mean * 2)
        Tor = 2
        print("Tb:", Tb, "Ts:", Ts)
        fsCandidate, feCandidate = 0, 0
        i = 0

        # Looping through SD
        while i < len(self.frameDistance):
            if self.frameDistance[i] >= Tb:
                self.cutResults.append((i + 1000, i + 1 + 1000))
                i = i + 1
            elif Ts <= self.frameDistance[i] < Tb:
                Tconsecutive = 0
                fsCandidate = i
                for j in range(fsCandidate + 1, len(self.frameDistance)):
                    if Ts <= self.frameDistance[j] < Tb:
                        Tconsecutive = 0
                    elif Ts >= self.frameDistance[j]:
                        Tconsecutive += 1
                        if Tconsecutive == Tor:
                            feCandidate = j - 2
                            currentSum = 0
                            # print("j:", j + 1000, "fs:", fsCandidate +
                            #      1000, self.frameDistance[j-1], self.frameDistance[j], feCandidate + 1000)
                            for k in range(fsCandidate, feCandidate + 1):
                                #    print(self.frameDistance[k])
                                currentSum += self.frameDistance[k]
                            # print(currentSum)
                            if currentSum >= Tb:
                                self.gtResults.append(
                                    (fsCandidate + 1000, feCandidate + 1000))
                            i = feCandidate
                            break
                    elif self.frameDistance[j] >= Tb:
                        Tconsecutive = 0
                        feCandidate = j - 1
                        currentSum = 0
                        for k in range(fsCandidate, feCandidate + 1):
                            currentSum += self.frameDistance[k]
                        if currentSum >= Tb:
                            self.gtResults.append(
                                (fsCandidate + 1000, feCandidate + 1000))
                            i = feCandidate
                        else:
                            self.cutResults.append((j + 1000, j + 1 + 1000))
                            i = j + 1
                        break
            i += 1

        # Printing the output to the terminal
        print("Outputting the set of (Cs,Ce) and (Fs, Fe):")
        print("(Cs, Ce):")
        for cutStart, cutEnd in self.cutResults:
            print((cutStart, cutEnd))
            self.cutFrames.append([cutStart - 1000, cutEnd - 1000])
        print("(Fs, Fe):")
        for frameStart, frameEnd in self.gtResults:
            print((frameStart, frameEnd))
            self.gtFrames.append([frameStart + 1 - 1000, frameEnd - 1000])

    def play_video(self):
        shot, finish = self.selectImageIndex[0] + \
            1000, self.selectImageIndex[1] + 1000
        # print("in play_video", shot, finish)

        video_path = 'Videos/20020924_juve_dk_02a.avi'
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("Error: Unable to open the video file")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if cap.get(cv2.CAP_PROP_POS_FRAMES) >= 1000:
                break

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Play the video starting from the frame associated with the clicked image
            if shot <= cap.get(cv2.CAP_PROP_POS_FRAMES) <= finish:
                # print(cap.get(cv2.CAP_PROP_POS_FRAMES))
                cv2.imshow('Video Player', frame)

                # Adjust the delay (in milliseconds) to control playback speed
                # 30 milliseconds provides ~33 frames per second (adjust as needed)
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
            if cap.get(cv2.CAP_PROP_POS_FRAMES) >= finish:
                break
        cap.release()
        cv2.destroyAllWindows()

    # Open the picture with the default operating system image
    # viewer.
    def inspect_pic(self, filename):
        command = str('open ' + os.getcwd() + '/' + filename)
        os.system(command)


if __name__ == '__main__':
    root = Tk()
    root.title('Video Shot Boundary Detection System')

    window_width = 800
    window_height = root.winfo_screenheight()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    # root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    pixInfo = PixInfo(root)
    imageViewer = ImageViewer(root, pixInfo)
    app = Frame(root)
    app.pack()

    root.mainloop()
