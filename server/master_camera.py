from cv2 import *

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