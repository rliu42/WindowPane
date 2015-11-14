from cv2 import *

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