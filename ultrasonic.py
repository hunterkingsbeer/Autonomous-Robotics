#!/usr/bin/env python3

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
SIMULATOR = False

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


def ultrasonic(): # Alias that calls the ultrasonic sensor. This function exists so we can change it later.
    n = sSonic.distance_centimeters # Supposedly, the ultrasonic sensor locks up when checked more than 1/100ms
    return int(n)


def color(): # Alias calling colour sensor. Wish it was sColour.colour, but y'know
    n = sColor.color
    return n

def sense():
    return None

"""
EVENT LOOP funny moments 
"""
announce("Ultrasonic checking")
announce("Current reading"+str(ultrasonic()))
sleep(0.1)
motorSpeed(25)
while ultrasonic() > 200:
    sleep(0.1)
motorSpeed(0)

goal = True
# drive forward until black square
# drive to top of black square and save the length
# go back that length

# go backwards until next black sqare
# update square (+15)

# TODO record distance and save as bSquareYdis
# TODO move 1/2 squarelegth from start of square

# 90 degree turn clockwise with pivot on the square
# go to furthest edge of square

# travel to next square
#       TODO furtherest edge????

# update square (+1)

# TODO save distance travelled as bSquareXdis
# go to middle of black square (drive forward 1/2 squarelength)
# GOOD rotate 90 degrees and detect using sonar the tower, method? (findTower())
wheelRotations = 0
# start rotating, incrementing rotations as a float

# TODO also sensing for tower, maybe a while loop?
#  WHILE(wheelRotations != required90rotations){
#       rotate
#       increment wheelRotations
#       sense for tower
#       if towersensed break

# theta = calculateAngle(wheelRotations)
# TODO xSquares = xDistanceToTower(theta, hypotenuse)
# TODO ySquares = yDistanceToTower(theta, hypotenuse)

#travelToTower()
# TODO from here, rotate back to origin x plane, travel the required number of
# TODO black squares horizontally

# turn 90 degrees clockwise

# resense tower
# if tower, travel needed black squares vertically and slow down on approach
#   to tower, use bump sensors to sense collision with tower and report
#   the big square number it is in (how do we do this)
# else findTower() badabing badaboom

if goal is True:
    announce("Goal")
    victorySound()
else:
    announce("No goal")
    failureSound()