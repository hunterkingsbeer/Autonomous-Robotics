#!/usr/bin/env python3
# LEAVE THE ABOVE LINE ALONE.

# === TROUBLESHOOTING ===
#   1. On the bottom right, on the lowest bar of the GUI, make sure it says LF and not CRLF or CR (click it to change)
#
#   2. A change MUST be made for pycharm to sync EVEN IF THE FILE IS NO LONGER PRESENT ON THE ROBOT...
#   even if the upload fails. Add a dummy comment to fix.
#
#   3. The simulator can't really do text to speech, so announce will print it too, while also speaking it:
#   Set SIMULATOR to false for speech to work on the robot.
#
# TODO: Calibration, Colour sensing (in more detail), generally the whole assignment lmao
# TODO: Fix orientation

SIMULATOR = True

# Imports

from time import sleep

from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank, MoveSteering
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor, TouchSensor
from ev3dev2.sound import Sound

import math

# Initialize dictionaries
deltaTiles = {  # Orientations to delta tile positions. Usage would be tile+=deltaTiles[orientation]
    0: -15,
    90: 1,
    180: 15,
    270: -1,
    360: -15
}

keyTiles = {
    0: 0
}

# Initialize objects and constants. Nothing in here should cause the robot to move.
ULTRASONICTRUEMAX = 255.0  # Highest possible distance the ultrasonic can detect.
TURN90 = 48.555  # Motor value for 90 degree turn. Matt's solution.
TURN90ROTATIONS = 0 # ninetyDegreeTurnRotations???????? huh????

sound = Sound()
mLeft = LargeMotor(OUTPUT_B)
mRight = LargeMotor(OUTPUT_C)
sColor = ColorSensor()
sSonic = UltrasonicSensor()
sTouch = TouchSensor()

steering_drive = MoveSteering(OUTPUT_B, OUTPUT_C)
tank_drive = MoveTank(OUTPUT_B, OUTPUT_C)

# Initialize common public variables

squareCurrent = 0 #currentSquare
squareLength = 0
squareXdis = 0 #bSquareXdis
squareYdis = 0 #bSquareYdis
squaresX = 0 #xSquares
squaresY = 0 #ySquares

orientation = 0
goal = False

# Define functions

# Kane functions, jackified

# Returns angle.
def calcAngle(rotations):
    ratio = rotations / TURN90ROTATIONS
    angle = 90*ratio
    return angle

# Returns both.
def towerDistance(theta, hypotenuse):
    x = hypotenuse * math.cos(theta)
    horizontal = x/(squareXdis+squareLength)

    y = hypotenuse * math.sin(theta)
    vertical = y/(squareYdis+squareLength)

    return horizontal, vertical


# Jack functions

def turnClockwise(orientation):
    # Takes orientation to understand where it currently is, return orientation for where it ends up
    # Usage:
    announce("Current orientation: " + str(orientation))

    orientation += 90
    orientation = orientation % 360

    steering_drive.on_for_rotations(TURN90, SpeedPercent(50), 1)
    # I AM ASSUMIGN YOU'D DETECT BOXES HERE
    announce("New orientation: " + str(orientation) + " (Turned clock)")
    return orientation


def turnCounterclockwise(orientation):
    announce("Current orientation: " + str(orientation))

    orientation -= 90
    if orientation < 0:
        orientation = 360-orientation
    orientation = orientation % 360

    steering_drive.on_for_rotations(-TURN90, SpeedPercent(50), 1)  # TODO FIX
    # I AM ASSUMIGN YOU'D DETECT BOXES HERE
    announce("New orientation: " + str(orientation) + " (Turned counter)")
    return orientation


def setOrientation(orientation, desired):
    difference = orientation - desired
    announce("\tSetting orientation, Difference: " + str(difference))
    if difference > 0:
        i = difference / 90
        # print(i)
        while i > 0.99:
            orientation = turnCounterclockwise(orientation)
            i = i - 1
    else:
        i = (difference / 90) * -1
        # print(i)
        while i > 0.99:
            orientation = turnClockwise(orientation)
            i = i - 1
    announce("\tSet orientation")
    # duringset = False
    return orientation


def announce(string):
    print(string)
    if SIMULATOR is False:
        sound.speak(string)


def victorySound():
    return None


def failureSound():
    return None


def detectSound():
    return None

def motorSpeed(n): # Alias for both motors.
    mLeft.on(speed=n)
    mRight.on(speed=n)

def halt():
    mLeft.on(0)
    mRight.on(0)

def goTillTouch(): # Experimental and hopefully functional!
    motorSpeed(15)
    sTouch.wait_for_pressed()
    motorSpeed(0)

# Not dealing with this for now because it seems as though the color sensor automatically calibrates (DEPENDING ON MODE)
"""def calibrate(orientation):
    orientation = turnClockwise(orientation)
    ULTRASONICTRUEMAX=2
    return orientation"""


def ultrasonic(): # Alias that calls the ultrasonic sensor. This function exists so we can change it later.
    n = sSonic.distance_centimeters # Supposedly, the ultrasonic sensor locks up when checked more than 1/100ms
    return n


def color(): # Alias calling colour sensor. Wish it was sColour.colour, but y'know
    n = sColor.color
    return n

"""
EVENT LOOP
"""

while goal is False:

    # tank_drive.on(25, 25)
    # sleep(1)
    # orientation = turnClockwise(orientation)
    # sleep(2)
    # tank_drive.on(25, 25)
    # sleep(1)
    # orientation = turnCounterclockwise(orientation)
    # sleep(2)
    # announce("Key order G")
    # sleep(0.2)
    # announce(str(sColor.color))

    announce("Ultrasonic is" + str(ultrasonic()))
    motorSpeed(25)
    halt()
    announce("Ultrasonic is" + str(ultrasonic()))

    if color() is not 6:
        while True:
            sleep(1)
            announce("Ultrasonic is" + str(ultrasonic()))
    goal = True

if goal is True:
    announce("Goal")
else:
    announce("No goal")
