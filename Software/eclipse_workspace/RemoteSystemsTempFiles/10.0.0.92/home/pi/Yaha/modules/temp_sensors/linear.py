#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py
#python /home/pi/Yaha/modules/heatingcontrol/linear.py

'''
Vorlauf, Kessel, Warmwasser: °C, Ohm
15,1067
20,1090
25,1113
30,1137
35,1161
40,1185
45,1210
50,1234
55,1260
60,1285
65,1311
70,1337
75,1363
80,1390
85,1417

Aussen:  °C, Ohm
-10,642
-5,633
0,623
5,612
10,600
15,588
20,575
25,563

'''


class chartLin():
    #init
    def __init__(self):
        self.points = []
        
        self.points.append([])
        self.points[0].append(1)
        self.points[0].append(2)

        self.points.append([])
        self.points[1].append(3)
        self.points[1].append(4)
        
        print(self.points[0][1])

        # Loop over rows.
        for pointPair in self.points:
            print(pointPair)



class xyLin():
    #init
    def __init__(self):
        self.x1 = 0         #x axis
        self.x2 = 0
        self.y1 = 0         #y axis
        self.y2 = 0
        self.k = 0
        self.d = 0
        self.xMin = 0
        self.xMax = 0
        self.yMin = 0
        self.yMax = 0
    
    def calcK(self):
        try:
            self.k = (float(self.y2) - float(self.y1)) / (float(self.x2) - float(self.x1)) 
        except:
            self.k = 0

    def calcD(self):
        try:
            self.d = ( (float(self.y1) * float(self.x2)) - (float(self.y2) * float(self.x1)) ) / (float(self.x2) - float(self.x1))
        except:
            self.d = 0
        
    def calcYfromX(self, x):
        try:
            y = self.k * float(x) + self.d #y = kx + d
            return max(min(y, self.yMax), self.yMin)
        except:
            return 0
    
    def calcXfromY(self, y):
        try:
            x = (y - self.d) / self.k     #x = (y - d) / k
            return max(min(x, self.xMax), self.xMin)
        except:
            return 0


tempChart = chartLin()
print("!!! DEBUGGING !!!")
