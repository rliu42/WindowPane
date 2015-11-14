from cv2 import *
import numpy as np
from matplotlib import pyplot as plt
import requests, json, firebase

APP_NAME = 'window-pane'

CONNECTIONS = 1
FRAME_RATE = 30 # frame update rate in ms
SYNC_SCREEN_RATE = 1000 # check for new screens every X ms
COUNTER = 0

FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
MIN_OBJECT_AREA = 100 * 100
MAX_OBJECT_AREA = 400 * 400

screens = []

def syncScreens():
	root = firebase.firebaseURL(APP_NAME)
	firebase.patch(root, {u'FRAME_WIDTH': FRAME_WIDTH , u'FRAME_HEIGHT': FRAME_HEIGHT})
	_screens = firebase.firebaseURL(APP_NAME + "/screens")
	resp = firebase.get(_screens)
	if resp is not None:
		CONNECTIONS = len(resp)
		print "Number of connections: ", CONNECTIONS
		print resp
	for idx, screen in enumerate(screens):
		s = firebase.firebaseURL(APP_NAME + "/screens/" + str(idx))
		firebase.put(s, {u'x': screen[0], u'y': screen[1], u'w': screen[2], u'h': screen[3]})


def interpolateScreen(rect):
	THRESHOLD = 400
	for idx, screen in enumerate(screens):
		if sum([abs(rect[i] - screen[i]) for i in range(4)]) < THRESHOLD:
			screens[idx] = rect
			return idx, screens[idx]
	return None, None


def drawScreens():
	for screen in screens:
		(x, y, w, h) = screen
		rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)


if __name__ == "__main__":
	capture = VideoCapture();
	capture.open(0);
	#set height and width of capture frame
	capture.set(4,FRAME_WIDTH);
	capture.set(5,FRAME_HEIGHT);
	#start an infinite loop where webcam feed is copied to cameraFeed matrix
	#all of our operations will be performed within this loop
	firstFrame = None
	while True:
		if COUNTER == 0:
			syncScreens()
		#store image to matrix
		rval, frame = capture.read()
		if not rval:
			break
		#convert frame from BGR to HSV colorspace
		gray = cvtColor(frame, COLOR_BGR2GRAY)
		if firstFrame is None:
			firstFrame = gray
			continue

		# compute the absolute difference between the current frame and
		# first frame
		gray = bilateralFilter(gray, 11, 17, 17)
		#frameDelta = absdiff(firstFrame, gray)
		firstFrame = gray

		thresh = threshold(gray, 50, 255, THRESH_BINARY)[1]
		edged = Canny(thresh, 10, 300)
 
		# dilate the thresholded image to fill in holes, then find contours
		# on thresholded image
		edged = dilate(edged, None, iterations=3)
		(_, cnts, _) = findContours(edged.copy(), RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)
 
		for c in cnts:
			peri = arcLength(c, True)
			approx = approxPolyDP(c, 0.02 * peri, True)
			# if the contour is too small, ignore it
			if contourArea(c) > MIN_OBJECT_AREA and contourArea(c) < MAX_OBJECT_AREA and len(approx) == 4:
				(x, y, w, h) = boundingRect(c)
				idx, screen = interpolateScreen((x, y, w, h))
				if idx is None and len(screens) < CONNECTIONS:
					screens.append((x, y, w, h))

		drawScreens()

		#imshow("Delta",frameDelta);
		imshow("Edges", edged);
		imshow("Thresh", thresh)
		imshow("Webcam", frame);
		

		#delay 30ms so that screen can refresh.
		#image will not appear without this waitKey() command
		COUNTER = (COUNTER + 1) % int(SYNC_SCREEN_RATE / FRAME_RATE)
		waitKey(FRAME_RATE);
