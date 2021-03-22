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

SIMULATOR = False

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

# Hunter functions

def turnClockwiseRotations():
    mLeft.on_for_rotations(SpeedPercent(25), 50)


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
    sleep(0.125)
    n = sSonic.distance_centimeters # Supposedly, the ultrasonic sensor locks up when checked more than 1/100ms
    return n


def color(): # Alias calling colour sensor. Wish it was sColour.colour, but y'know
    n = sColor.color
    return n

"""
EVENT LOOP
"""

# rotate 90, slow 90 degree scanning distance
# when ultrasonic scanner hits, report distance, go back to initial
""" FUNCTIONS BUT NOT USED IN SOLUTION
def findTower(orientation):
    towerFound = False
    searchDegrees = 0
    searchRotationAmount = 5

    orientation = turnClockwise(orientation)

    for index in range(int(89/searchRotationAmount)):
        if towerFound is False:
            rotateDegreesRight(searchRotationAmount)  # turn 1 degree at a time, for 90 degrees
            searchDegrees += searchRotationAmount  # increment the searchDegrees +1
            testSonic = ultrasonic()
            if testSonic < 100:  # if ultrasonic returns less than 100cm, tower has been found
                announce("FOUND" + str(testSonic))
                towerFound = True
            sleep(0.5)

    if towerFound is True:
        rotateDegreesLeft(searchDegrees)  # rotate the degrees back into position

    return searchDegrees
"""

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
    currentTileNum = 0

    while currentTileNum != desiredTile:
        currentTileNum = countBlackTile(currentTileNum)
    if currentTileNum == desiredTile:
        announce("FOUND")


#testing purposes START ORIENTATION IN GOING HORIZONTAL
orientation = 90
findBlackTile(3)