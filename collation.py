#!/usr/bin/env python3

from time import sleep

from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank, MoveSteering
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor, TouchSensor
from ev3dev2.sound import Sound

import math
import logging

# Initialize dictionaries
deltaTiles = {  # Orientations to delta tile positions. Usage would be tile+=deltaTiles[orientation]
    0: -15,
    90: 1,
    180: 15,
    270: -1,
    360: -15
}

keyTiles = {
    56: 1,
    57: 1,
    58: 2,
    59: 2,
    60: 3,
    71: 4,
    72: 4,
    73: 5,
    74: 6,
    75: 6,
    86: 7,
    87: 7,
    88: 8,
    89: 9,
    90: 9,
    101: 10,
    102: 10,
    103: 11,
    104: 12,
    105: 12
}

# Initialize objects and constants. Nothing in here should cause the robot to move.
ULTRASONICTRUEMAX = 255.0  # Highest possible distance the ultrasonic can detect.
TURN90 = 48.555  # Motor value for 90 degree turn. Matt's solution.
TURN90ROTATIONS = 0 # ninetyDegreeTurnRotations???????? huh????
SIMULATOR = False
STANDARDSPEED = 25

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
    sound.tone([
        (392, 350, 100), (392, 350, 100), (392, 350, 100), (311.1, 250, 100),
        (466.2, 25, 100), (392, 350, 100), (311.1, 250, 100), (466.2, 25, 100),
        (392, 700, 100), (587.32, 350, 100), (587.32, 350, 100),
        (587.32, 350, 100), (622.26, 250, 100), (466.2, 25, 100),
        (369.99, 350, 100), (311.1, 250, 100), (466.2, 25, 100), (392, 700, 100),
        (784, 350, 100), (392, 250, 100), (392, 25, 100), (784, 350, 100),
        (739.98, 250, 100), (698.46, 25, 100), (659.26, 25, 100),
        (622.26, 25, 100), (659.26, 50, 400), (415.3, 25, 200), (554.36, 350, 100),
        (523.25, 250, 100), (493.88, 25, 100), (466.16, 25, 100), (440, 25, 100),
        (466.16, 50, 400), (311.13, 25, 200), (369.99, 350, 100),
        (311.13, 250, 100), (392, 25, 100), (466.16, 350, 100), (392, 250, 100),
        (466.16, 25, 100), (587.32, 700, 100), (784, 350, 100), (392, 250, 100),
        (392, 25, 100), (784, 350, 100), (739.98, 250, 100), (698.46, 25, 100),
        (659.26, 25, 100), (622.26, 25, 100), (659.26, 50, 400), (415.3, 25, 200),
        (554.36, 350, 100), (523.25, 250, 100), (493.88, 25, 100),
        (466.16, 25, 100), (440, 25, 100), (466.16, 50, 400), (311.13, 25, 200),
        (392, 350, 100), (311.13, 250, 100), (466.16, 25, 100),
        (392.00, 300, 150), (311.13, 250, 100), (466.16, 25, 100), (392, 700)
    ])


def failureSound():
    announce("FAILURE")


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

def quickchunk():
    increment=0
    for i in range(3):
        if color()==1:
            increment+=1
        motorSpeed(25)
        sleep(.1)
        halt()
    return increment

def luminance(groundTuple):
    return (groundTuple[0]*0.2126)+(groundTiple[1]*0.7152)+(groundTuple[2]*0.0722)

def rotateDegreesRight(degrees):
    amount = 0.935 / 90
    mLeft.on_for_rotations(SpeedPercent(20), amount*degrees)
    sleep(0.1)


def rotateDegreesLeft(degrees):
    amount = 0.935 / 90
    mRight.on_for_rotations(SpeedPercent(20), amount*degrees)
    sleep(0.1)


def reverseRotateLeft(degrees):
    amount = 0.935 / 90
    mLeft.on_for_rotations(SpeedPercent(-20), amount * degrees)
    sleep(0.1)

def reverseRotateRight(degrees):
    amount = 0.935 / 90
    mRight.on_for_rotations(SpeedPercent(-20), amount * degrees)
    sleep(0.1)

def tankRotateDegrees(degrees):
    amount = (0.935/2) / 90
    tank_drive.on_for_rotations(SpeedPercent(-20 if degrees < 0 else 20), SpeedPercent(20 if degrees > 0 else -20), amount*degrees)
    sleep(0.1)

def squarePivot(degrees):
    reverseRotateRight(degrees / 2)
    rotateDegreesRight(degrees / 2)
    sleep(0.1)



def checkIfBlackTile():
    blackSensorCheck = 0

    for i in range(3):
        if color() == 1:
            blackSensorCheck += 1
        tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.08)
        sleep(0.1)

    if blackSensorCheck >= 3:
        return True
    else:
        return False



def countBlackTile(currentTileNum):
    foundBlackTile = False

    while foundBlackTile == False: #while its not on a black square
        tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.15) #drive forward

        if color() == 1: #then check if its a black square.
            if checkIfBlackTile(): #verify that it is actually a black square!
                currentTileNum += deltaTiles[orientation] #add increment CHANGE TO WORK WITH ORIENTATION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                announce(currentTileNum)
                foundBlackTile = True
                return currentTileNum

def findBlackTile(desiredTile):
    while currentTileNum != desiredTile:
        currentTileNum = countBlackTile(currentTileNum)
    if currentTileNum == desiredTile:
        announce("FOUND")

def findTowerLocation():
    while currentTileNum != desiredTile:
        currentTileNum = countBlackTile(currentTileNum)
    if currentTileNum == desiredTile:
        announce("FOUND")

"""
EVENT LOOP 
"""
# Collating everything to solve solution - Very Hard coded and rough
currentTileNum = 0
columnDistance = 0

while sColor != 1:
    motorSpeed(-15)

halt()
sleep(0.5)
currentTileNum = 16
announce(currentTileNum)

squarePivot(90)
findBlackTile(currentTileNum+10)

squarePivot(90)
findBlackTile(currentTileNum+30)

columnDistance = ultrasonic()
towerColumn = 1
for i in range(2):
    squarePivot(-90)
    findBlackTile(currentTileNum+20)
    squarePivot(90)
    columnDistanceNew = ultrasonic()
    if columnDistanceNew < columnDistance:
        columnDistance = columnDistanceNew
        towerColumn = i+2


if towerColumn != 3:
    squarePivot(90)
    if towerColumn == 2:
        findBlackTile(currentTileNum-2)
    else:
        findBlackTile(currentTileNum-2)
    squarePivot(-90)

while ultrasonic() > 10:
    motorSpeed(25)
    if checkIfBlackTile() is True:
        currentTileNum += deltaTiles[orientation]
        announce(currentTileNum)
halt()
while ultrasonic() > 5:
    motorSpeed(10)
    if checkIfBlackTile() is True:
        currentTileNum += deltaTiles[orientation]
        announce(currentTileNum)
sleep(1)
halt()
towerLocation = keyTiles[currentTileNum]
announce(towerLocation)
if towerLocation is not None:
    goal = True

# drive forward until black square
# drive to top of black square and save the length
# go back that lengt h

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