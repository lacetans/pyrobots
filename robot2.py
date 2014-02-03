# -*- coding: utf-8 -*-

"""
PYROBOTS
Enric Mieza - Institut Lacetània
Janury 2014

English version
"""

from pyrobots import RobotBase
import random

class Robot(RobotBase):
    name = "fool"
    author = "enric"
    rounds = 0
    last_enemy_angle = 0
    last_enemy_distance = 1

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
        self.accel( random.randint(0,1) )
        
        # apuntem i disparem a l'enemic
        angle , distance = self.detect_enemy()
        inc = angle - self.last_enemy_angle

        self.shot(angle+2*inc)
        self.shot(angle)
        
        self.last_enemy_angle = angle
