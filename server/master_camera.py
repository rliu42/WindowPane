from cv2 import *
import math, thread, firebase
import numpy as np

APP_NAME = 'window-pane'

CONNECTIONS = 0
FRAME_RATE = 15 # frame update rate in ms
SYNC_SCREEN_RATE = 500 # check for new screens every X ms
COUNTER = 0

FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
MIN_OBJECT_AREA = 60 * 60
MAX_OBJECT_AREA = 400 * 400

colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (0,255,255), (255,0,255)]
screens = ["none"]

def syncScreens():
	_screens = firebase.firebaseURL(APP_NAME + "/screens")
	resp = firebase.get(_screens)
	if resp is not None:
		CONNECTIONS = len(resp) - 1
		print "Number of connections: ", CONNECTIONS
		print resp
	for idx, screen in enumerate(screens):
		if idx > 0:
			s = firebase.firebaseURL(APP_NAME + "/screens/" + str(idx))
			center, dims, rotation = screen
			firebase.put(s, {u'center': {u'x':int(center[0]), u'y':int(center[1])}, u'dims': {u'h':int(dims[0]), u'w':int(dims[1])}, u'rotation': int(rotation)})


def interpolateScreen(rect):
	THRESHOLD = 200
	center, dims, rotation = rect
	for idx, screen in enumerate(screens):
		if idx > 0:
			if abs(screen[0][1] - center[1]) + abs(screen[0][0] - center[0]) < THRESHOLD:
				screens[idx] = rect
				return idx, screens[idx]
	return None, None


def drawScreens(frame):
	for idx, screen in enumerate(screens):
		if idx > 0:
			box = np.int0(boxPoints(screen))
			fillConvexPoly(frame, box, colors[idx % len(colors)])
		#for i in range(4):
			#line(frame, (box[i][0], box[i][1]), (box[(i+1)%4][0], box[(i+1)%4][1]), (0,0,255), 2)


if __name__ == "__main__":
	root = firebase.firebaseURL(APP_NAME)
	firebase.patch(root, {u'FRAME_WIDTH': FRAME_WIDTH , u'FRAME_HEIGHT': FRAME_HEIGHT})
	_screens = firebase.firebaseURL(APP_NAME + "/screens")
	firebase.put(_screens, {u'0': 'none'})

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
			screens_copy = screens[::]
			thread.start_new_thread(syncScreens, ())	
		#store image to matrix
		rval, frame = capture.read()
		if not rval:
			break
		#convert frame from BGR to HSV colorspace
		gray = cvtColor(frame, COLOR_BGR2GRAY)
		gray = bilateralFilter(gray, 11, 17, 17)
		if firstFrame is None:
			firstFrame = gray

		# compute the absolute difference between the current frame and
		# first frame
		frameDelta = absdiff(firstFrame, gray)
		firstFrame = gray

		thresh = threshold(frameDelta, 100, 255, THRESH_BINARY)[1]
		edged = Canny(thresh, 1, 300)
 
		# dilate the thresholded image to fill in holes, then find contours
		# on thresholded image
		edged = dilate(edged, None, iterations=3)
		(_, cnts, _) = findContours(edged.copy(), RETR_TREE, CHAIN_APPROX_SIMPLE)
 
		for c in cnts:
			peri = arcLength(c, True)
			approx = approxPolyDP(c, 0.02 * peri, True)
			# if the contour is too small, ignore it
			# drawContours(frame, [c], 0, (0,0, 255), 2)
			if contourArea(c) > MIN_OBJECT_AREA and contourArea(c) < MAX_OBJECT_AREA and len(approx) <= 6:
				rect = minAreaRect(c)
				#box = boxPoints(rect)
				#box = np.int0(box)
				#for i in range(4):
					#line(frame, (box[i][0], box[i][1]), (box[(i+1)%4][0], box[(i+1)%4][1]), (0,255,0), 2)
				#drawContours(frame, [box], 0, (0,255,0))
				print rect
				idx, screen = interpolateScreen(rect)
				if idx is None and len(screens)-1 < CONNECTIONS:
					screens.append(rect)
				if len(screens)-1 == CONNECTIONS:
					break

		drawScreens(frame)

		imshow("Delta",frameDelta);
		#imshow("Edges", edged);
		#imshow("Thresh", thresh)
		imshow("Webcam", frame);
		

		#delay 30ms so that screen can refresh.
		#image will not appear without this waitKey() command
		COUNTER = (COUNTER + 1) % int(SYNC_SCREEN_RATE / FRAME_RATE)
		waitKey(FRAME_RATE);
