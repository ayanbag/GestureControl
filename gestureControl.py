import cv2
import mediapipe as mp
import time
import handTrackingModule as htm
import autopy
import numpy as np
import sys
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Variables 
prevT=0
currT=0
wCam,hCam=640,480
vol=0
vol_bar=400
vol_per=0
frameR=40
smooth=10
plocX,plocY=0,0
clocX,clocY=0,0

# Camera Initializations
cam = cv2.VideoCapture(0)
cam.set(3,wCam)
cam.set(4,hCam)

# Intialization
detection=htm.handdetection(detectionConf=0.7,maxhands=1)
wscreen,hscreen=autopy.screen.size()
detections=htm.handdetection(detectionConf=0.7)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))


def thanks():
    autopy.alert.alert("Thank You for using Gesture Control")


while True:
    success,img=cam.read() 

    img=detection.findingHands(img)
    lmklist,bbox=detection.findPosition(img)  

    if len(lmklist)!=0:
        x1,y1=lmklist[8][1:]
        x2,y2=lmklist[12][1:]
        fingers=detection.fingersUp()
        #cv2.rectangle(img,(frameR,frameR),(wCam-frameR,hCam-frameR),(255,0,255),2)

        # Mouse Pointer Movements
        if fingers[1]==1 and fingers[2]==0 and fingers[4]==0 and fingers[0]==0  and fingers[3]==0:
            cv2.rectangle(img,(frameR,frameR),(wCam-frameR,hCam-frameR),(255,0,255),2)
            x3=np.interp(x1,(frameR,wCam-frameR),(0,wscreen))
            y3=np.interp(y1,(frameR,hCam-frameR),(0,hscreen))
            clocX=plocX+(x3-plocX)/smooth
            clocY=plocY+(y3-plocY)/smooth
            autopy.mouse.move(wscreen-clocX,clocY)
            cv2.circle(img,(x1,y1),15,(255,0,255),thickness=5, lineType=8)
            plocX,plocY =clocX,clocY

        # Clicking Objects
        if fingers[1]==1 and fingers[2]==1 and fingers[4]==0 and fingers[0]==0  and fingers[3]==0:
            cv2.rectangle(img,(frameR,frameR),(wCam-frameR,hCam-frameR),(255,0,255),2)
            length,img,info=detection.findDistance(8,12,img)
            if length<45:
                cv2.circle(img,(info[4],info[5]),15,(0,255,0),cv2.FILLED)
                autopy.mouse.click()

        # Exiting from application using Hand Gesture
        if fingers[1]==1 and fingers[4]==1 and fingers[0]==0 and fingers[2]==0 and fingers[3]==0:
            cam.release()
            thanks()

        # Sound Control
        if fingers[1]==1 and fingers[4]==0 and fingers[0]==1 and fingers[2]==0 and fingers[3]==0:
            x11,y11=lmklist[8][1:]
            x4,y4=lmklist[4][1:]
            cx2,cy2=(x11+x4)//2,(y11+y4)//2

            #length,img,info=detection.findDistance(8,4,img,draw=False)
            length=math.hypot(x4-x11,y4-y11)
            cv2.circle(img,(x11,y11),10,(255,0,255),thickness=5, lineType=8)
            cv2.circle(img,(x4,y4),10,(255,0,255),thickness=5, lineType=8)
            cv2.line(img,(x11,y11),(x4,y4),(255,0,255),2)
            cv2.circle(img,(cx2,cy2),10,(0,255,0),cv2.FILLED)

            volume_range=volume.GetVolumeRange()
            min_vol=volume_range[0]
            max_vol=volume_range[1]

            vol = np.interp(length,[50,240],[min_vol,max_vol])
            volume.SetMasterVolumeLevel(vol, None)
            

            if length<50:
                cv2.circle(img,(cx2,cy2),10,(0,255,255),cv2.FILLED)

            vol_bar = np.interp(length,[50,240],[400,150])
            vol_per = np.interp(length,[50,240],[0,100])
            cv2.rectangle(img,(50,150),(85,400),(0,0,205),3)
            cv2.rectangle(img,(50,int(vol_bar)),(85,400),(0,0,205),cv2.FILLED)
            cv2.putText(img,f'{int(vol_per)} %',(40,450),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(0,0,205),2)


    # Calculating and Displaying FPS
    currT=time.time()
    fps=1/(currT-prevT)
    prevT=currT
    cv2.putText(img,f'FPS : {str(int(fps))}',(20,40),
                cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(0,0,205),2)


    # Camera On
    cv2.imshow("Track",img)
    cv2.waitKey(1)