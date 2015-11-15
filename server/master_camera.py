from cv2 import *
import math, thread, firebase
import numpy as np

APP_NAME = 'window-pane'

CONNECTIONS = 0
FRAME_RATE = 15 # frame update rate in ms
SYNC_SCREEN_RATE = 25 # check for new screens every X ms
COUNTER = 0

FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_RATIO = 2.25
MIN_OBJECT_AREA = 30 * 40
MAX_OBJECT_AREA = 400 * 400
prevResp = []
landscape = True

colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (0,255,255), (255,0,255)]
screens = ["none"]

def syncScreens():
	global CONNECTIONS, prevResp, landscape
	_screens = firebase.firebaseURL(APP_NAME + "/screens")
	resp = firebase.get(_screens)
	if resp is not None:
		CONNECTIONS = len(resp) - 1
		if len(resp) != len(prevResp):
			print "Number of connections: ", CONNECTIONS
			print resp
			if CONNECTIONS >= 1:
				if "innerWidth" in resp[-1].keys():
					landscape = resp[-1]["innerWidth"] > resp[-1]["innerHeight"]
			prevResp = resp
	for idx, screen in enumerate(screens):
		if idx > 0:
			s = firebase.firebaseURL(APP_NAME + "/screens/" + str(idx))
			center, dims, rotation = screen
			firebase.patch(s, {u'center': {u'x':int(center[0]), u'y':int(center[1])}, u'dims': {u'h':int(dims[1]), u'w':int(dims[0])}, u'rotation': int(rotation)})


def interpolateScreen(rect):
	THRESHOLD = 75
	center, dims, rotation = rect
	for idx, screen in enumerate(screens):
		if idx > 0:
			diff = abs(screen[0][1] - center[1]) + abs(screen[0][0] - center[0]) 
			if (diff > 5 and diff < THRESHOLD):
				screens[idx][0] = list(center)
				screens[idx][2] = 0
				return idx, screens[idx]
			elif diff <= 5:
				return -1, -1
	return None, None


def drawScreens(frame):
	#print screens
	for idx, screen in enumerate(screens):
		if idx > 0:
			rect = (tuple(screen[0]), tuple(screen[1]), screen[2])
			box = np.int0(boxPoints(rect))
			fillConvexPoly(frame, box, colors[idx % len(colors)])


if __name__ == "__main__":
	root = firebase.firebaseURL(APP_NAME)
	firebase.patch(root, {u'FRAME_WIDTH': FRAME_WIDTH , u'FRAME_HEIGHT': FRAME_HEIGHT, u'RELOAD': -1, u'valid': "no"})
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
		#frameDelta = absdiff(firstFrame, gray)
		firstFrame = gray

		thresh = threshold(gray, 210, 255, THRESH_BINARY)[1]
		edged = Canny(thresh, 1, 300)
 
		# dilate the thresholded image to fill in holes, then find contours
		# on thresholded image
		edged = dilate(edged, None, iterations=2)
		(_, cnts, _) = findContours(edged.copy(), RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)
 
		for c in cnts:
			peri = arcLength(c, True)
			approx = approxPolyDP(c, 0.02 * peri, True)
			# if the contour is too small, ignore it
			# drawContours(frame, [c], 0, (0,0, 255), 2)
			rect = minAreaRect(c)
			area = rect[1][0] * rect[1][1]
			ratio = 1.0 * rect[1][0] / rect[1][1]
			if (area > MIN_OBJECT_AREA and area < MAX_OBJECT_AREA) and (ratio > 1.0 / FRAME_RATIO and ratio < FRAME_RATIO) and len(approx) <= 4:
				idx, screen = interpolateScreen(rect)
				if idx == None and len(screens)-1 < CONNECTIONS:
					center, dims, rotation = rect
					h = dims[0] if dims[0] > dims[1] else dims[1]
					w = dims[1] if dims[0] > dims[1] else dims[0]
					if landscape:
						temp = h
						h = w
						w = temp
					print "Detected new screen: " + ("landscape" if landscape else "portrait")
					screens.append([list(center), [w, h], 0])
				if len(screens)-1 == CONNECTIONS:
					break

		drawScreens(frame)

		#imshow("Delta",frameDelta);
		imshow("Edges", edged);
		#imshow("Thresh", thresh)
		imshow("Webcam", frame);
		

		#delay 30ms so that screen can refresh.
		#image will not appear without this waitKey() command
		COUNTER = (COUNTER + 1) % int(SYNC_SCREEN_RATE / FRAME_RATE)
		waitKey(FRAME_RATE);
