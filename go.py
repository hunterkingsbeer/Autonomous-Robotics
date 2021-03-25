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
# Speech pauses now handled in the announce variable itself. Defaults to pause

# Imports

import math
from time import sleep, time, ctime

from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank, MoveSteering
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor, TouchSensor
from ev3dev2.sound import Sound

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
TURN90ROTATIONS = 0  # ninetyDegreeTurnRotations???????? huh????

sound = Sound()
mLeft = LargeMotor(OUTPUT_B)
mRight = LargeMotor(OUTPUT_C)
sColor = ColorSensor()
sSonic = UltrasonicSensor()
sTouch = TouchSensor()

steering_drive = MoveSteering(OUTPUT_B, OUTPUT_C)
tank_drive = MoveTank(OUTPUT_B, OUTPUT_C)

# Initialize common public variables

squareCurrent = 0  # currentSquare
squareLength = 0
squareXdis = 0  # bSquareXdis
squareYdis = 0  # bSquareYdis
squaresX = 0  # xSquares
squaresY = 0  # ySquares

orientation = 0
currentTileNum = 0
goal = False


# Define functions

# Kane functions, jackified

# Returns angle.
def calcAngle(rotations):
    ratio = rotations / TURN90ROTATIONS
    angle = 90 * ratio
    return angle


# Returns both.
def towerDistance(theta, hypotenuse):
    x = hypotenuse * math.cos(theta)
    horizontal = x / (squareXdis + squareLength)

    y = hypotenuse * math.sin(theta)
    vertical = y / (squareYdis + squareLength)

    return horizontal, vertical


# Jack functions

def turnClockwise():
    # Takes orientation to understand where it currently is, return orientation for where it ends up
    # Usage:
    global orientation
    announce("Current orientation: " + str(orientation))

    orientation += 90
    orientation = orientation % 360

    steering_drive.on_for_rotations(TURN90, SpeedPercent(50), 1)
    # I AM ASSUMIGN YOU'D DETECT BOXES HERE
    announce("New orientation: " + str(orientation) + " (Turned clock)")


def turnCounterclockwise():
    global orientation

    announce("Current orientation: " + str(orientation))

    orientation -= 90
    if orientation < 0:
        orientation = 360 - orientation
    orientation = orientation % 360

    steering_drive.on_for_rotations(-TURN90, SpeedPercent(50), 1)  # TODO FIX
    # I AM ASSUMIGN YOU'D DETECT BOXES HERE
    announce("New orientation: " + str(orientation) + " (Turned counter)")


def setOrientation(desired):
    global orientation
    difference = orientation - desired
    announce("\tSetting orientation, Difference: " + str(difference))
    if difference > 0:
        i = difference / 90
        # print(i)
        while i > 0.99:
            orientation = turnCounterclockwise()
            i = i - 1
    else:
        i = (difference / 90) * -1
        # print(i)
        while i > 0.99:
            orientation = turnClockwise()
            i = i - 1
    announce("\tSet orientation")
    # duringset = False


def announce(string, pause=True):
    print(string)
    if SIMULATOR is False:
        if not pause:
            sound.speak(string, play_type=sound.PLAY_NO_WAIT_FOR_COMPLETE)
        else:
            sound.speak(string)
    log(string)


def victorySound():
    return None


def failureSound():
    return None


def detectSound():
    return None


def motorSpeed(n):  # Alias for both motors.
    mLeft.on(speed=n)
    mRight.on(speed=n)


def halt():
    mLeft.on(0)
    mRight.on(0)


def goTillTouch():  # Experimental and hopefully functional!
    motorSpeed(15)
    sTouch.wait_for_pressed()
    motorSpeed(0)


def luminance(groundTuple):
    return (groundTuple[0] * 0.2126) + (groundTuple[1] * 0.7152) + (groundTuple[2] * 0.0722)


# Not dealing with this for now because it seems as though the color sensor automatically calibrates (DEPENDING ON MODE)
"""def calibrate(orientation):
    orientation = turnClockwise(orientation)
    ULTRASONICTRUEMAX=2
    return orientation"""


def ultrasonic():  # Alias that calls the ultrasonic sensor. This function exists so we can change it later.
    sleep(0.125)
    n = sSonic.distance_centimeters  # Supposedly, the ultrasonic sensor locks up when checked more than 1/100ms
    return n


def color():  # Alias calling colour sensor. Wish it was sColour.colour, but y'know
    n = sColor.color
    return n


def log(s=""):
    f = open("log.txt", "a")
    f.write("\n" + ctime(time()) + " " + str(s))
    f.close()


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


# rotates right wheel forward, to turn left
def rotateDegreesLeft(degrees):
    amount = 0.938 / 90
    mRight.on_for_rotations(SpeedPercent(20), amount * degrees)
    sleep(0.1)

    global orientation
    orientation -= degrees
    if orientation < 0:
        orientation = 360 - orientation
    orientation = orientation % 360


# rotates left wheel forward, to turn right
def rotateDegreesRight(degrees):
    amount = 0.938 / 90
    mLeft.on_for_rotations(SpeedPercent(20), amount * degrees)
    sleep(0.1)

    global orientation
    orientation += degrees
    if orientation < 0:
        orientation = 360 - orientation
    orientation = orientation % 360


# rotates left wheel backwards, to turn left
def reverseRotateLeft(degrees):
    amount = 0.938 / 90
    mLeft.on_for_rotations(SpeedPercent(-20), amount * degrees)
    sleep(0.1)

    global orientation
    orientation -= degrees
    if orientation < 0:
        orientation = 360 - orientation
    orientation = orientation % 360


# rotates right wheel backwards, to turn right
def reverseRotateRight(degrees):
    amount = 0.938 / 90
    mRight.on_for_rotations(SpeedPercent(-20), amount * degrees)
    sleep(0.1)

    global orientation
    orientation += degrees
    if orientation < 0:
        orientation = 360 - orientation
    orientation = orientation % 360


# rotates wheels opposite, to turn left
def tankRotateLeft(degrees):
    amount = (0.938 / 2) / 90
    tank_drive.on_for_rotations(SpeedPercent(-20), SpeedPercent(20), amount * degrees)

    global orientation
    orientation -= degrees
    if orientation < 0:
        orientation = 360 - orientation
    orientation = orientation % 360
    sleep(0.1)


# rotates wheels opposite, to turn right
def tankRotateRight(degrees):
    amount = (0.938 / 2) / 90
    tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(-20), amount * degrees)

    global orientation
    orientation += degrees
    if orientation < 0:
        orientation = 360 - orientation
    orientation = orientation % 360
    sleep(0.1)


# needs to be changed, doesnt actually even pivot
# should only put in 90 degree amounts, (90/180/270/360)
def squarePivot(degrees):
    for i in range(int(degrees / 90)):
        if degrees > 0:
            reverseRotateRight(90 / 2)
            rotateDegreesRight(90 / 2)
        else:
            degrees *= -1
            reverseRotateLeft(90 / 2)
            rotateDegreesLeft(90 / 2)

    sleep(0.1)

    announce(str(orientation))


def checkIfBlackTile():
    blackSensorCheck = 0

    for i in range(4):
        if color() == 1:
            blackSensorCheck += 1
        tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.08)
        sleep(0.1)

    if blackSensorCheck >= 4:
        return True
    else:
        return False


def countBlackTile():
    global currentTileNum
    foundBlackTile = False

    while not foundBlackTile:  # while its not on a black square
        tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.15)  # drive forward

        if color() == 1:  # then check if its a black square.
            if checkIfBlackTile():  # verify that it is actually a black square!
                currentTileNum += deltaTiles[orientation]  # add increment CHANGE TO WORK WITH ORIENTATION!!!!!!!
                announce(currentTileNum)
                foundBlackTile = True


def calibrate():
    global currentTileNum

    if currentTileNum == 0:
        announce("find 1")
        currentTileNum = countBlackTile()
        announce("found tile " + currentTileNum)


# start at tile 1. If not, the math.ceil will break
def findBlackTile(desiredTile):
    announce("desired tile " + str(desiredTile))
    announce("current tile " + str(currentTileNum))

    global currentTileNum

    while currentTileNum != desiredTile:  # until you find the desired tile

        # tile is with the current row
        if math.ceil(desiredTile / 15) > math.ceil(currentTileNum / 15):  # if desired row is below the current row
            # announce("column down")
            # orientate down (180)
            while orientation != 180:  # if robot isn't facing right (90), rotate until it is
                if 180 <= orientation <= 360:
                    tankRotateLeft(90)
                else:
                    tankRotateRight(90)
            countBlackTile()  # then count squares until you find the tile


        # tile is below the current row
        elif math.ceil(desiredTile / 15) == math.ceil(currentTileNum / 15):
            # if the desired tile is to the right of the robot
            if currentTileNum < desiredTile:
                # announce("row right")
                while orientation != 90:  # if robot isn't facing right (90), rotate until it is
                    tankRotateRight(90)
                countBlackTile()  # then count squares until you find the tile

            # desired tile must be to the left of robot
            elif desiredTile < currentTileNum:
                # announce("row left")
                while orientation != 270:  # if robot isn't facing left (270), rotate until it is
                    tankRotateRight(90)
                countBlackTile()
        else:
            announce("error")

    if currentTileNum == desiredTile:
        announce("FOUND " + desiredTile)



# start square 16?
# orientation reporting on a multiple of 90 pivot?
# return current tile as square num?

# start facing 0 degrees
orientation = 0
currentTileNum = 1 #to calibrate it, and not break the find black tile

findBlackTile(55)

"""


"""
