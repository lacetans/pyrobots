# -*- coding: utf-8 -*-

"""
PYROBOTS
Enric Mieza - Institut Lacetània
Gener 2014
"""

from pyrobots import RobotBase
import random

class Robot(RobotBase):
    name = "atontao"
    author = "enric"
    compt = 0
    ultim_angle_enemic = 0
    ultima_dist_enemic = 1

    def round(self):
        # actualitzem comptador de torns
        self.compt += 1
        
        # cada 5 torns canviem de direcció aleatòriament
        if self.compt%6==0:
            self.gira( self.detecta_angle() + random.randint(-10,+50) )
        
        # vigilem de no estrellar-nos
        murs = self.detecta_murs()
        dmin = min( murs.values() )
        # si ens acostem massa al mur (distància mínima)
        if dmin < 50:
            if murs["up"]==dmin:
                self.gira( 90 )
            elif murs["down"]==dmin:
                self.gira( -90 )
            elif murs["left"]==dmin:
                self.gira( 0 )
            elif murs["right"]==dmin:
                self.gira( 180 )
            else:
                print "ERROR gir robot2"
        
        # accelerem aleatòriament
        self.accel( random.randint(0,1) )
        
        # apuntem i disparem a l'enemic
        angle , distancia = self.detecta_enemic()
        inc = angle - self.ultim_angle_enemic

        self.dispara(angle+2*inc)
        self.dispara(angle)
        
        self.ultim_angle_enemic = angle
