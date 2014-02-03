pyrobots
========
Enric Mieza - Institut Lacetània Manresa

January 2014

Installation
------------
Pyrobots uses python (minimum 2.7) , Qt4, Phonon and PyQt4

Ubuntu / Debian
---------------
Install packages:

$ sudo apt-get install python-qt4 phonon python-qt4-phonon

Start game:

$ python pyrobots.py

(will ask for file names to import the robots, you can simply press ENTER to pick up the standard examples)

Game
----
Programming game. The users have to program their own fighting robot, as in the examples:
- robot1.py : the robot moves in circles and shot every time it can.
- robot2.py : randomized movement, and shots trying to anticipate the moves of the opponent.

Rules:
- Programming language is Python.
- The two robots will be placed randomly in the game field to begin the fight.
- The position is updated every 20ms (50 frames per second).
- The robots have a control round every 10 frames.
- Underscores ("_") are forbidden at the beginning of the robot's attributes and methods
- Each robot starts with 15 life points.
- Bumping the walls decrements 1 life point and leaves you on tilt during 3 rounds.
- Only 4 shots can be displayed in the screen.

Robot actions
-------------
- self.accel(val) : acceleration , can be (-1, 0, +1)
- self.brake(val) : True/False
- self.turn(degrees) : direction of the robot wheels
- self.shot(degrees) : that
- TODO: defense() : shooting not enable during defense

Robot sensors
-------------
- self.detect_vel() : returns our speed (pixels/frame)
- self.detect_turn() : returns current angle of the wheels
- self.detect_walls() : returns an associative array (dictionary) with
    the distances to the walls in pixels
    {
        "up"  : mur superior
        "down": mur inferior
        "left": mur esquerre
        "right": mur dret
    }
- self.detect_enemy() : angle en graus en la direcció on es troba l'enemic
- TODO: self.detect_shot()
