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

columnTiles = {
    1: 56,
    2: 58,
    3: 59
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

def routeLog(s=""):
    f = open("routeLog.txt", "a")
    f.write(str(s)+", ")
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


# SEEKING FUNCTIONS ----------------------------------------------------------------------------------------------------


# verifies black tiles by taking multiple point color checks, returns true if it is a black square.
def checkIfBlackTile():
    blackSensorCheck = 0
    # (value used to be 4)
    for i in range(2):
        if color() == 1:
            blackSensorCheck += 1
        tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.2) # (used 0.08)
        sleep(0.1)

    if blackSensorCheck >= 2: # If 2 checks showed black, its a black square. (value used to be 4)
        return True
    else:
        return False


# drives until it can count another black tile, upon which it increments the current tile number.
def countBlackTile():
    global currentTileNum
    foundBlackTile = False

    while not foundBlackTile:  # while its not on a black square
        if orientation == 180: # if robot is travelling down a column
            tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.3)  # drive forward more rotations
        else: # else robot is travelling across a row
            tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.2)  # drive forward
        if color() == 1:  # then check if its a black square, and verify
            if checkIfBlackTile():
                currentTileNum += deltaTiles[orientation]
                foundBlackTile = True


# start at tile 1. If not, the math.ceil function will break
def findBlackTile(desiredTile):
    announce("find" + str(desiredTile))
    global currentTileNum

    while currentTileNum != desiredTile:  # until you find the desired tile

        # if desired tile is BELOW the current row, need to travel DOWN
        if math.ceil(desiredTile / 15) > math.ceil(currentTileNum / 15):
            changeOrientation(180)
            countBlackTile()  # then count squares until you find the tile

        # if desired tile is ABOVE the current row, need to travel UP
        elif math.ceil(desiredTile / 15) < math.ceil(currentTileNum / 15):
            changeOrientation(180)
            countBlackTile()  # then count squares until you find the tile

        # if desired tile is WITHIN the current row, need to travel LEFT or RIGHT
        elif math.ceil(desiredTile / 15) == math.ceil(currentTileNum / 15):

            # if the desired tile is to the LEFT of the robot
            if desiredTile < currentTileNum:
                changeOrientation(270)  # face left
                countBlackTile()

            # if the desired tile is to the RIGHT of the robot
            elif currentTileNum < desiredTile:
                changeOrientation(90)  # face right
                countBlackTile()
    # announce when you find the desired tile
    if currentTileNum == desiredTile:
        announce("FOUND " + str(desiredTile))


# uses tank rotate to move to a desired rotation
def changeOrientation(desiredOrientation):
    while orientation != desiredOrientation:
        if orientation < desiredOrientation:  # make sure we turn using the appropriate direction
            tankRotateRight(90)
        else:
            tankRotateLeft(90)


# HAVE NOT IMPLEMENTED, BUT SHOULD HOPEFULLY WORK
def scanColumn(columnNumber):
    global towerDist  # towers distance
    global towerCol  # towers column

    findBlackTile(columnTiles[columnNumber])
    changeOrientation(90)  # make sure its facing 90 degrees, may not be needed.

    if columnNumber != 2:  # if column 1 or 3 (with 2 black tiles on the edge of the big tile)
        tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.2)  # drive to center of tile
        rotateDegreesRight(90)  # turn right, to face down (180) to scan
        tempDist = ultrasonic()
        if tempDist < towerDist:  # if current distance is less than the last tower distance
            towerDist = tempDist  # then update the tower variables
            towerCol = columnNumber
        rotateDegreesRight(-90)  # reverse the turn

    else:  # if column 2 (with black tile in center of the big tile)
        changeOrientation(180)  # pivot to face down
        tempDist = ultrasonic()
        if tempDist < towerDist:  # if current distance is less than the last tower distance
            towerDist = tempDist  # then update the tower variables
            towerCol = columnNumber


# seeks the tower by scanning each of the 3 tower tile columns, reports back the towers column
def seekTower():
    towerDist = 0
    colNum = 0

    # find column 1's first black square
    findBlackTile(56)
    while currentTileNum == 56:
        changeOrientation(90)
        tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.2)
        rotateDegreesRight(90)
        towerDist = ultrasonic()
        rotateDegreesRight(-90)
        colNum = 1
        break

    # find column 2's first black square
    findBlackTile(58)
    while currentTileNum == 58:
        changeOrientation(180)
        col2 = ultrasonic()
        if col2 < towerDist:
            tempDistance = col2
            colNum = 2
        break

    # find column 3's first black square
    findBlackTile(59)
    while currentTileNum == 59:
        changeOrientation(90)
        tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.2)

        rotateDegreesRight(90)
        col3 = ultrasonic()
        rotateDegreesRight(-90)
        if col3 < towerDist:
            towerDist = col3
            colNum = 3
        break

    announce("column " + str(colNum))
    sleep(0.2)
    announce("distance " + str(towerDist))


# EVENT CODE -----------------------------------------------------------------------------------------------------------

# SEEK VARIABLES
towerDist = 0
towerCol = 0

# CHANGEABLE VARIABLES
orientation = 0 # 0, 90, 180, 270
currentTileNum = 1

# PROCESSES
seekTower()


""" 
fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
"""
