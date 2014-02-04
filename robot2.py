# -*- coding: utf-8 -*-

"""
PYROBOTS
Enric Mieza - Institut Lacetània
Janury 2014

English version
"""

from pyrobots import RobotBase, Shot
import random
from math import sin, cos, tan, atan, pi

class Robot(RobotBase):
    name = "fool"
    author = "enric"
    rounds = 0
    last_angle = 0
    last_dist = 1

    def round(self):
        # update round counter
        self.rounds += 1
        
        # every 6 rounds change robot direction randomly
        if self.rounds%6==0:
            self.turn( self.detect_angle() + random.randint(-10,+50) )
        
        # take care for not to crash
        walls = self.detect_walls()
        dmin = min( walls.values() )
        if dmin < 50:
            if walls["up"]==dmin:
                self.turn( 90 )
            elif walls["down"]==dmin:
                self.turn( -90 )
            elif walls["left"]==dmin:
                self.turn( 0 )
            elif walls["right"]==dmin:
                self.turn( 180 )
            else:
                print "ERROR turning robot2"
        
        # random acceleration
        #self.accel( random.randint(0,1) )
        
        # calculate enemy equation y = ax + b
        angle , distance = self.detect_enemy()
        angle_rad = 2*pi*angle/360.0
        alpha = self.last_angle - angle
        alphar = 2*pi*alpha/360.0
        ix = distance * sin( alphar )
        iy = self.last_dist*cos( alphar ) - distance
        a = iy / ix
        b = self.last_dist
        
        # angles alpha and beta in radians
        def fun( a, b, d1, d2, alpha, beta, vel):
            # i*j -k
            i = b / (atan(beta) - a)
            j = ( 1 / (d1*sin(alpha)) ) - ( 1 / (vel*cos(beta)) )
            k = d1 / (d2*sin(alpha))
            return i*j-k
        
        res = []
        bs = []
        for i in range(-10,10):
            beta = i/10.0*pi/2
            bs.append(beta)
            f = fun( a, b, self.last_dist, distance, alphar, beta, Shot.vel )
            res.append( abs(f) )
        #print res
        #print bs
        
        rmin = min(res)
        index = res.index(rmin)
        shot_angle_rad = (index-10.0)/10.0*pi/2
        
        print rmin,index,shot_angle_rad
        
        # rectify direction
        #if cos(shot_angle_rad) * cos(angle_rad) < 0:
        #    shot_angle_rad += pi
        
        # we've got it! shot!
        self.shot(360.0*shot_angle_rad/(2*pi))
        #self.shot(shot_angle+180)
        
        # keep values for later calculations
        self.last_angle = angle
        self.last_dist = distance





