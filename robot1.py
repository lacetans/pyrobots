# -*- coding: utf-8 -*-

"""
PYROBOTS
Enric Mieza - Institut Lacetània
Gener 2014
"""

from pyrobots import RobotBase, Game
import random, math

class Robot(RobotBase):
    name = "cercles"
    author = "enric"
    compt = 0
    ultim_mov = 0
    angle = 0
    
    def round(self):
        if self.compt==0:
            self.gira(0)
            
        self.compt += 1

        # acceleracio
        if self.detecta_vel() < 5:
            self.accel( 1 )
        
        # direcció
        #self.angle += 8
        #self.gira( self.angle )
        murs = self.detecta_murs()
        if murs["left"]<30:
            self.gira(0)
        elif murs["right"]<50:
            self.gira(180)
        
        # apuntem i disparem a l'enemic
        angle_enemic, distancia = self.detecta_enemic()
        self.dispara( angle_enemic )


