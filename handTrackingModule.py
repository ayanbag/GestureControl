import cv2
import mediapipe as mp
import time 
import math
import numpy as np


class handdetection():
    def __init__(self,mode=False,maxhands=2,detectionConf=0.5,trackConf=0.5):
        self.mode=mode
        self.maxhands=maxhands
        self.detectionConf=detectionConf
        self.trackConf=trackConf
        self.mphand=mp.solutions.hands
        self.hands=self.mphand.Hands(self.mode,self.maxhands,self.detectionConf,self.trackConf)
        self.draw=mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findingHands(self,img,draw=True):
        rgbimg=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        self.res=self.hands.process(rgbimg)
        if self.res.multi_hand_landmarks:
            for handlmks in self.res.multi_hand_landmarks:
                if draw:    
                    self.draw.draw_landmarks(img,handlmks,self.mphand.HAND_CONNECTIONS)
        return img

    def findPosition(self,img,handNum=0,draw=True):
        xList = []
        yList = []
        bbox = []
        self.lmkList=[]
        if self.res.multi_hand_landmarks:
            myHands = self.res.multi_hand_landmarks[handNum]
            for id,lmk in enumerate(myHands.landmark):
                h,w,ch = img.shape
                cx,cy = int(lmk.x*w),int(lmk.y*h)
                xList.append(cx)
                yList.append(cy)
                self.lmkList.append([id,cx,cy])
                '''
                if draw:
                    cv2.circle(img,(cx,cy),5,(255,0,255),cv2.FILLED)
                '''

            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax
            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20),
                              (0, 255, 0), 2)

        return self.lmkList, bbox
    
    def fingersUp(self):
        fingers = []
        if self.lmkList[self.tipIds[0]][1] > self.lmkList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        for id in range(1, 5):
            if self.lmkList[self.tipIds[id]][2] < self.lmkList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers
      
    def findDistance(self, p1, p2, img, draw=True,r=10, t=3):
        x1, y1 = self.lmkList[p1][1:]
        x2, y2 = self.lmkList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), thickness=3, lineType=8)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), thickness=3, lineType=8)
            cv2.circle(img, (cx, cy), r-2, (0, 0, 255), thickness=2, lineType=8)
        length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]

    
   