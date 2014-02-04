#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
PyRobots
--------
January 2014 - Enric Mieza
Institut Lacetània Manresa

Classes:
- Shot
- RobotBase
- Screen
- Game
"""

import sys, math, random
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import Qt
from PyQt4.phonon import Phonon

class Shot():
    posx = 0
    posy = 0
    vel = 5
    angle = 0
    size = 6
    color = QtGui.QColor(0,0,0)

    def __init__(self,robot,angle):
        self.posx = robot._posx+robot._size/2
        self.posy = robot._posy+robot._size/2
        self.color = robot.color
        self.angle = angle

    def update(self,width,height):
        self.posx += self.vel*math.cos(self.angle/360.0*2*math.pi)
        self.posy += self.vel*math.sin(self.angle/360.0*2*math.pi)
        # returns false if it gets out of limits (to be deleted)
        if self.posx<=0 or self.posx>=width or self.posy<=0 or self.posy>=height:
            return False
        return True

    def draw(self,qp):
        qp.setBrush(self.color)
        qp.drawEllipse(self.posx,self.posy,self.size,self.size)

class UserError(Exception):
    pass

class RobotBase(QtCore.QObject):
    # constants
    _INITLIFE = 15
    _MAXVEL = 3
    _MAXSHOTS = 4
    _MAXFRAMES = 5
    _INITTILT = 3
    # basics
    name = "pyrobot-base"
    author = "anonymous"
    _life = 0
    _updateLife = QtCore.pyqtSignal()
    _errorSignal = QtCore.pyqtSignal()
    _error = False
    # position and velocity
    _posx = 100
    _posy = 100
    _vel = 0
    _angle = 45
    # forma
    _size = 18
    color = QtGui.QColor(250,250,0)
    # shots
    _shots = 0
    # other
    _frames = 0
    _tilt = 0
    _lastwidth = 0
    _lastheight = 0
    
    def __init__(self,width,height):
        super(RobotBase,self).__init__()
        self._restart(width,height)

    def _restart(self,width,height):
        # put the robot in a random place
        self._posx = random.randint(0,width-self._size)
        self._posy = random.randint(0,height-self._size)
        # reset values
        self._shots = []
        self._error = False
        self._life = self._INITLIFE
        self._updateLife.emit()

    def _impact(self,shot):
        r = QtCore.QRect(self._posx,self._posy,self._size,self._size)
        if r.contains( shot.posx, shot.posy ):
            self._life -= 1
            self._updateLife.emit()
            self._screen.impact_media.stop()
            self._screen.impact_media.play()
            return True
        return False

    def round(self):
        # to be filled by the robot programmer (user)
        pass

    def _update(self, width, height):
        self._frames += 1
        # user robot takes control
        if self._frames%self._MAXFRAMES==0:
            if self._tilt>0:
                # if tilt we loose some rounds
                # TODO: change color?...
                self._tilt -= 1
            else:
                try:
                    self.round()
                except Exception as e:
                    # we return False to end the game (error or illegal action)
                    self._error = True
                    print "ERROR ROBOT " + self.name
                    print e.message
                    #print sys.exc_info()[0]
                    self._errorSignal.emit()
                    return False
        # update position
        self._posx += self._vel*math.cos(self._angle/360.0*2*math.pi)
        self._posy += self._vel*math.sin(self._angle/360.0*2*math.pi)
        # limit control (bumps)
        bumped = False
        if self._posx >= width-self._size:
            self._posx = width-self._size*2
            bumped = True
        elif self._posx <= 0:
            self._posx = self._size
            bumped = True
        if self._posy >= height-self._size:
            self._posy = height-self._size*2
            bumped = True
        elif self._posy <= 0:
            self._posy = self._size
            bumped = True
        if bumped:
            self._vel = 0
            self._life -= 1
            self._tilt = self._INITTILT
            self._screen.clang_media.stop()
            self._screen.clang_media.play()
            self._updateLife.emit()
        # update shots
        for t in self._shots:
            if not t.update(width,height):
                self._shots.remove(t)
        # store values
        self._lastwidth = width
        self._lastheight = height
        # return True if all OK
        return True
        
    def _draw(self, qp):
        qp.setBrush( self.color )
        qp.drawRect( self._posx, self._posy, self._size, self._size )
        for t in self._shots:
            t.draw(qp)
        
    def gira(self,degrees):
        self.turn(degrees)
    def turn(self,degrees):
        self._angle = degrees

    def accel(self,val):
        # val = -1 , 0 , 1
        if abs(val)>1:
            raise UserError("accel")
        self._vel += val
        self._vel = min(self._vel,self._MAXVEL)

    def frena(self):
        self.brake()
    def brake(self):
        self._vel = self._vel/2

    def dispara(self,graus):
        self.shot(graus)
    def shot(self,degrees):
        if len(self._shots)>=self._MAXSHOTS:
            return False
        t = Shot(self,degrees)
        self._shots.append( t )
        # sons
        self._screen.shot_media.stop()
        self._screen.shot_media.play()
        return True

    def detecta_murs(self):
        return self.detect_walls()
    def detect_walls(self):
        walls = {
            "up"  : self._posy,
            "down": self._lastheight-self._posy,
            "left": self._posx,
            "right": self._lastwidth-self._posx
        }
        return walls

    def detecta_trets(self):
        return self.detect_shots()
    def detect_shots(self):
        # TODO: implement dectec_shots
        return []

    def detecta_vel(self):
        return self.detect_vel()
    def detect_vel(self):
        return self._vel

    def detecta_angle(self):
        return self.detect_angle()
    def detect_angle(self):
        return self._angle

    def detecta_enemic(self):
        return self.detect_enemy()
    def detect_enemy(self):
        p = self._screen
        # increments (from robot1)
        ix = p.robot2._posx - p.robot1._posx
        iy = p.robot2._posy - p.robot1._posy
        # avoid division by zero
        if ix==0 and iy>0:
            angle = math.pi/2
        elif ix==0 and iy<0:
            angle = -math.pi/2
        else:
            # calculate angle (between +pi/2 i -pi/2)
            # pass increments to floats
            angle = math.atan(1.0*iy/ix)
        # angle > 180º
        if ix<0:
            angle += math.pi
        # normalize
        if angle<0: angle += math.pi*2
        # distance
        dist = math.sqrt(ix**2+iy**2)
        # return angle from robot1 or 2
        if p.robot1 == self:
            return 360.0*angle/(2*math.pi) , dist
        else:
            # robot 2
            angle -= math.pi
            return 360.0*angle/(2*math.pi) , dist


class Screen(QtGui.QWidget):
    # Sounds
    #  shot_media
    #  clang_media
    #  impact_media
    #  boum_media
    _RESTART_MS = 5000
    
    def __init__(self):
        super(QtGui.QWidget,self).__init__()
        self.initUI()
    
    def initUI(self):
        # background
        pal = self.palette()
        pal.setColor(self.backgroundRole(), QtGui.QColor(230,230,250) )
        self.setPalette(pal)
        self.setAutoFillBackground(True)

        # robots
        file1 = raw_input("File for robot 1, without .py [ENTER for 'robot1']:")
        file2 = raw_input("File for robot 1, without .py [ENTER for 'robot2']:")
        if not file1: file1 = "robot1"
        if not file2: file2 = "robot2"
        # check file rules
        if self._check_file( file1 ) and self._check_file( file2 ):
            mod1 = __import__(file1)
            mod2 = __import__(file2)
            self.robot1 = mod1.Robot( self.width(), self.height() )
            self.robot2 = mod2.Robot( self.width(), self.height() )
            self.robot1.color = QtGui.QColor(250,250,0)
            self.robot2.color = QtGui.QColor(250,0,50)
            self.robot1._screen = self
            self.robot2._screen = self

        # sounds
        self.shot_media = Phonon.MediaObject( self )
        self.clang_media = Phonon.MediaObject( self )
        self.impact_media = Phonon.MediaObject( self )
        self.boum_media = Phonon.MediaObject( self )
        audioOutput1 = Phonon.AudioOutput( Phonon.GameCategory, self )
        audioOutput2 = Phonon.AudioOutput( Phonon.GameCategory, self )
        audioOutput3 = Phonon.AudioOutput( Phonon.GameCategory, self )
        audioOutput4 = Phonon.AudioOutput( Phonon.GameCategory, self )
        Phonon.createPath( self.shot_media , audioOutput1 )
        Phonon.createPath( self.clang_media , audioOutput2 )
        Phonon.createPath( self.impact_media , audioOutput3 )
        Phonon.createPath( self.boum_media , audioOutput4 )
        #self.shot_media.setCurrentSource( Phonon.MediaSource("sounds/laser3.mp3") )
        self.impact_media.setCurrentSource( Phonon.MediaSource("sounds/laser2.mp3") )
        self.clang_media.setCurrentSource( Phonon.MediaSource("sounds/clang1.mp3") )
        self.boum_media.setCurrentSource( Phonon.MediaSource("sounds/crash1.mp3") )

        # timer 1 : repaint frame
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.repaint)
        # timer 2 : restart game
        self.timer2 = QtCore.QTimer(self)
        self.timer2.setInterval(self._RESTART_MS)
        self.timer2.setSingleShot(True)
        self.timer2.timeout.connect(self.restart)
        
    def restart(self):
        self.robot1._restart( self.width(), self.height() )
        self.robot2._restart( self.width(), self.height() )
        self.timer.start()

    def paintEvent(self,event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setFont(QtGui.QFont('Decorative',18))
        self.draw(qp,event)
        qp.end()
        
    def draw(self,qp,event):
        # check errors
        if self.robot1._error and self.robot2._error:
            qp.drawText(event.rect(),QtCore.Qt.AlignCenter,"ERROR both 2 robots")
            self.boum_media.play()
            return            
        elif self.robot1._error:
            qp.drawText(event.rect(),QtCore.Qt.AlignCenter,"ERROR ROBOT 1 "+self.robot1.name)
            self.boum_media.play()
            return            
        elif self.robot2._error:
            qp.drawText(event.rect(),QtCore.Qt.AlignCenter,"ERROR ROBOT 2 "+self.robot2.name)
            self.boum_media.play()
            return
        # comprova final partida
        if self.robot1._life<=0 and self.robot2._life<=0:
            qp.drawText(event.rect(),QtCore.Qt.AlignCenter,"TIE (empat)!")
            self.boum_media.play()
            return
        if self.robot1._life<=0:
            qp.drawText(event.rect(),QtCore.Qt.AlignCenter,"Winner: ROBOT 2 "+unicode(self.robot2.name))
            self.boum_media.play()
            return
        if self.robot2._life<=0:
            qp.drawText(event.rect(),QtCore.Qt.AlignCenter,"Winner: ROBOT 1 "+unicode(self.robot1.name))
            self.boum_media.play()
            return
		# update position
        self.robot1._update( self.width(), self.height() )
        self.robot2._update( self.width(), self.height() )
        # shot impacts
        for shot in self.robot1._shots:
            if self.robot2._impact(shot):
                self.robot1._shots.remove( shot )
        for shot in self.robot2._shots:
            if self.robot1._impact(shot):
                self.robot2._shots.remove( shot )

        # TODO: impacts between robots
        
        # draw robots and shots
        self.robot1._draw(qp)
        self.robot2._draw(qp)
        
    # check robot user files to be imported
    def _check_file( self, filename ):
        f = open( filename+".py" )
        l = 0
        for line in f:
            l += 1
            if "._" in line or " _" in line or ";_" in line:
                print "FILE " + filename + " ILLEGAL, line " + str(l)
                print line
                return False
        return True

class Game(QtGui.QWidget):
    score1 = 0
    score2 = 0
    WIDTH = 800
    HEIGHT = 600
    
    def __init__(self):
        super(Game, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        # widgets
        self.grid = QtGui.QGridLayout()
        self.lcd1 = QtGui.QLCDNumber()
        self.lcd2 = QtGui.QLCDNumber()
        self.bar1 = QtGui.QProgressBar(self)
        self.bar2 = QtGui.QProgressBar(self)
        # screen (canvas) to draw
        self.screen = Screen()
        # progress bar styling
        s = self.bar1.styleSheet().append("""QProgressBar:horizontal {
            border: 1px solid gray;
            border-radius: 3px;
            background: white;
            padding: 1px;
            text-align: center;
            }
            QProgressBar::chunk:horizontal {
            background: qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 yellow, stop: 1 white);
            }""")
        self.bar1.setStyleSheet( s )
        s = self.bar2.styleSheet().append("""QProgressBar:horizontal {
            border: 1px solid gray;
            border-radius: 3px;
            background: white;
            padding: 1px;
            text-align: center;
            }
            QProgressBar::chunk:horizontal {
            background: qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #fa0033, stop: 1 white);
            }""")
        self.bar2.setStyleSheet( s )
        
        # connect robots to displays
        self.bar1.setRange( 0, RobotBase._INITLIFE )
        self.screen.robot1._updateLife.connect( self.updatelife, QtCore.Qt.QueuedConnection )
        self.screen.robot1._errorSignal.connect( self.error_robot, QtCore.Qt.QueuedConnection  )
        self.bar2.setRange( 0, RobotBase._INITLIFE )
        self.screen.robot2._updateLife.connect( self.updatelife, QtCore.Qt.QueuedConnection )
        self.screen.robot2._errorSignal.connect( self.error_robot, QtCore.Qt.QueuedConnection  )

        # layout
        spanPant = 20
        self.grid.addWidget(self.screen,1,0,spanPant,spanPant)
        self.grid.addWidget(self.lcd1,0,0)
        self.grid.addWidget(self.lcd2,0,spanPant-1)
        self.grid.addWidget(self.bar1,0,1)
        self.grid.addWidget(self.bar2,0,spanPant-2)
		
        self.setLayout(self.grid)
        
        self.setGeometry(50, 50, self.WIDTH, self.HEIGHT)
        self.setWindowTitle('PyRobots')
        self.setFocus()
        # restart game : reset values + start timer
        self.screen.restart()
        # take screen to closeup (particulary for Mac)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.show()
    
    def updatelife(self):
        # life robot1
        life1 = max(self.screen.robot1._life,0)
        self.bar1.setValue( life1 )
        # end of game control
        if life1<=0:
            self.screen.timer.stop()
            self.score2 += 1
            self.lcd2.display(self.score2)
            self.screen.repaint()
            # restart game in 5 seconds
            self.screen.timer2.start()
        # life robot2
        life2 = max(self.screen.robot2._life,0)
        self.bar2.setValue( life2 )
        # end of game control
        if life2<=0:
            self.screen.timer.stop()
            self.score1 += 1
            self.lcd1.display(self.score1)
            self.screen.repaint()
            # restart game in 5 seconds
            self.screen.timer2.start()
    
    def error_robot(self):
        self.screen.timer.stop()
        if self.sender()==self.screen.robot1:
            self.score2 += 1
        else:
            self.score1 += 1
        self.screen.repaint()

    def keyPressEvent(self,e):
        if e.key() == QtCore.Qt.Key_Return:
            self.screen.restart()

def main():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("PyRobots")
    game = Game()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
