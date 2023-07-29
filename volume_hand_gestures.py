#importing all the necessary modules and functions
import cv2
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np

def adjust_volume():
    #initialising the camera
    cap = cv2.VideoCapture(0)
    #initialising mediapipe, pycaw

    mpHands = mp.solutions.hands #used to detect the hand
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils 


    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    #getting the values of the volume range of the device
    volRange = volume.GetVolumeRange()
    min,max = volRange[0],volRange[1]; # Assigns volRange[0] to min, and volRange[1] to max

    #initialize the volume to 0
    vol = 0
    while cap.isOpened():
        res, frame = cap.read() 
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #Convert frame to RGB

        #Collect the gesture information
        results = hands.process(imgRGB) #completes the image processing.
    
        lmlist = []
        #Detecting the hands
        if results.multi_hand_landmarks:
            for hand_landmark in results.multi_hand_landmarks:
                for id, lm in enumerate(hand_landmark.landmark):
                    h, w, _ = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmlist.append([id, cx, cy]) #Adding details to the list
                mpDraw.draw_landmarks(frame, hand_landmark, mpHands.HAND_CONNECTIONS)#Drawing on the frame
        
        if lmlist != []:
            x1, y1 = lmlist[4][1], lmlist[4][2]  #coordinates of thumb
            x2, y2 = lmlist[8][1], lmlist[8][2]  #coordinates of index finger

            #making a circle at the tips of the thumb and index finger
            cv2.circle(frame, (x1, y1), 15, (255, 0, 255), cv2.FILLED) #order of parameters --> image, fingers, radius, RGB
            cv2.circle(frame, (x2, y2), 15, (255, 0, 255), cv2.FILLED) #order of parameters --> image, fingers, radius, RGB
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)  #joining the circles with a line of thickness 3px

            length = hypot(x2 - x1, y2 - y1) #calulating the distance between the fingertips using hypotenuse
            # Converting the volume to the range of min and max
            vol = np.interp(length, [20,190], [min,max])
            # Setting the volume of the device to vol
            volume.SetMasterVolumeLevel(vol, None)
        cv2.imshow('Image', frame) #Showing each frame
        if cv2.waitKey(1) == ord('x'): # Pressing the 'x' key will terminate the program
            break
            
    cap.release() #stop cam       
    cv2.destroyAllWindows() #close window

if __name__ == '__main__':
    adjust_volume()