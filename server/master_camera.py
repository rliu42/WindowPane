from cv2 import *
import numpy as np
from matplotlib import pyplot as plt

H_MIN = 0
H_MAX = 256
S_MIN = 0
S_MAX = 256
V_MIN = 0
V_MAX = 256
FRAME_WIDTH = 1080
FRAME_HEIGHT = 810
MAX_NUM_OBJECTS = 10
MIN_OBJECT_AREA = 20 * 20
MAX_OBJECT_AREA = FRAME_HEIGHT * FRAME_WIDTH / 2
windowName = "Webcam Feed"
windowName1 = "HSV Image"
windowName2 = "Threshold"
windowName3 = "After Morphological Operations"
trackbarWindowName = "Trackbars"

def on_trackbar():
	# this function gets called 
	# whenever a trackbar position is changed   

def createTrackbars():
	namedWindow(trackbarWindowName, 0)
	createTrackbar("H_MIN", trackbarWindowName, H_MIN, H_MAX, on_trackbar)
	createTrackbar("H_MAX", trackbarWindowName, H_MAX, H_MAX, on_trackbar)
	createTrackbar("S_MIN", trackbarWindowName, S_MIN, S_MAX, on_trackbar)
	createTrackbar("S_MAX", trackbarWindowName, S_MAX, S_MAX, on_trackbar)
	createTrackbar("V_MIN", trackbarWindowName, V_MIN, V_MAX, on_trackbar)
	createTrackbar("V_MAX", trackbarWindowName, V_MAX, V_MAX, on_trackbar)

def drawObject(x, y, frame):
	circle(frame, (x, y), 20, (0, 255, 0), 2)
	if y-25>0:
		line(frame, (x, y), (x, y-25), (0, 255, 0), 2)
	else:
		line(frame,(x,y),(x,0),(0,255,0),2)
	if y+25<FRAME_HEIGHT:
		line(frame,(x,y),(x,y+25),(0,255,0),2)
	else:
		line(frame,(x,y),(x,FRAME_HEIGHT),(0,255,0),2)
	if x-25>0:
		line(frame,(x,y),(x-25,y),(0,255,0),2)
	else:
		line(frame,(x,y),(0,y),(0,255,0),2)
	if x+25<FRAME_WIDTH:
		line(frame,(x,y),(x+25,y),(0,255,0),2)
	else:
		line(frame,(x,y),(FRAME_WIDTH,y),(0,255,0),2)
	putText(frame, str(x) + "," + str(y), (x, y+30), 1,1,(0,255,0),2)

def morphOps(thresh):
	erodeElement = getStructuringElement(MORPH_RECT, (3,3))
	dilateElement = getStructuringElement(MORPH_RECT, (8,8))
	erode(thresh,thresh,erodeElement)
	erode(thresh,thresh,erodeElement)

	dilate(thresh,thresh,dilateElement)
	dilate(thresh,thresh,dilateElement)

def trackFilteredObject(x, y, threshold, cameraFeed):
	temp = Mat();
	threshold.copyTo(temp);
	#these two vectors needed for output of findContours
	contours = [[]];
	hierarchy = [];
	#find contours of filtered image using openCV findContours function
	findContours(temp,contours,hierarchy,CV_RETR_CCOMP,CV_CHAIN_APPROX_SIMPLE );
	#use moments method to find our filtered object
	refArea = 0.0;
	objectFound = False;
	if len(hierarchy) > 0:
		numObjects = len(hierarchy);
		#if number of objects greater than MAX_NUM_OBJECTS we have a noisy filter
		if numObjects<MAX_NUM_OBJECTS:
			index = 0;
			while index >= 0:
				moment = moments(cv.Mat(contours[index]));
				area = moment.m00;

				#if the area is less than 20 px by 20px then it is probably just noise
				#if the area is the same as the 3/2 of the image size, probably just a bad filter
				#we only want the object with the largest area so we safe a reference area each
				#iteration and compare it to the area in the next iteration.
				if area>MIN_OBJECT_AREA and area<MAX_OBJECT_AREA and area>refArea:
					x = moment.m10/area;
					y = moment.m01/area;
					objectFound = True;
					refArea = area;
				else:
					objectFound = False;
				index = hierarchy[index][0];
			#let user know you found an object
			if objectFound == True:
				putText(cameraFeed,"Tracking Object",Point(0,50),2,1,Scalar(0,255,0),2);
				#draw object location on screen
				drawObject(x,y,cameraFeed);
		else:
			putText(cameraFeed,"TOO MUCH NOISE! ADJUST FILTER",Point(0,50),1,2,Scalar(0,0,255),2);


if __name__ == "__main__":
	#some boolean variables for different functionality within this
	#program
	trackObjects = False;
	useMorphOps = False;
	#Matrix to store each frame of the webcam feed
	cameraFeed = Mat();
	#matrix storage for HSV image
	HSV = Mat();
	#matrix storage for binary threshold image
	threshold = Mat();
	#x and y values for the location of the object
	x=0;
	y=0;
	#create slider bars for HSV filtering
	createTrackbars();
	#video capture object to acquire webcam feed
	capture = VideoCapture();
	#open capture object at location zero (default location for webcam)
	capture.open(0);
	#set height and width of capture frame
	capture.set(CV_CAP_PROP_FRAME_WIDTH,FRAME_WIDTH);
	capture.set(CV_CAP_PROP_FRAME_HEIGHT,FRAME_HEIGHT);
	#start an infinite loop where webcam feed is copied to cameraFeed matrix
	#all of our operations will be performed within this loop
	while True:
		#store image to matrix
		capture.read(cameraFeed);
		#convert frame from BGR to HSV colorspace
		cvtColor(cameraFeed,HSV,COLOR_BGR2HSV);
		#filter HSV image between values and store filtered image to
		#threshold matrix
		inRange(HSV,Scalar(H_MIN,S_MIN,V_MIN),Scalar(H_MAX,S_MAX,V_MAX),threshold);
		#perform morphological operations on thresholded image to eliminate noise
		#and emphasize the filtered object(s)
		if useMorphOps:
			morphOps(threshold);
		#pass in thresholded frame to our object tracking function
		#this function will return the x and y coordinates of the
		#filtered object
		if trackObjects:
			trackFilteredObject(x,y,threshold,cameraFeed);

		#show frames 
		imshow(windowName2,threshold);
		imshow(windowName,cameraFeed);
		imshow(windowName1,HSV);
		

		#delay 30ms so that screen can refresh.
		#image will not appear without this waitKey() command
		waitKey(30);
