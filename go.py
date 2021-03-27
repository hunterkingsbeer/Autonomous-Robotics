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

SIMULATOR = False

# Imports

import math
from time import sleep, time, ctime

from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank, MoveSteering
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor
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
    3: 59,
    4: 71,
    5: 73,
    6: 74,
    7: 86,
    8: 88,
    9: 89,
    10: 101,
    11: 103,
    12: 104
}

keyTiles = {
    56: 1,
    57: 1,
    58: 2,
    59: 3,
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

sound = Sound()
mLeft = LargeMotor(OUTPUT_B)
mRight = LargeMotor(OUTPUT_C)
sColor = ColorSensor()
sSonic = UltrasonicSensor()

steering_drive = MoveSteering(OUTPUT_B, OUTPUT_C)
tank_drive = MoveTank(OUTPUT_B, OUTPUT_C)

# Initialize common public variables
# If you're up here because of a warning, pleeeease leave these alone. Yes they may have been set before/after,
# but if we forget to set them on the day, these should correspond to the right values for a successful test.
orientation = 0
currentTileNum = 1
goal = False
foundTower = False

def announce(string, pause=True):
    print(string)
    if SIMULATOR is False:
        if not pause:
            sound.speak(string, play_type=sound.PLAY_NO_WAIT_FOR_COMPLETE)
        else:
            sound.speak(string)
    log(string)


def motorSpeed(n):  # Alias for both motors.
    mLeft.on(speed=n)
    mRight.on(speed=n)


def halt():
    mLeft.on(0)
    mRight.on(0)



def luminance(groundTuple):
    return (groundTuple[0] * 0.2126) + (groundTuple[1] * 0.7152) + (groundTuple[2] * 0.0722)


def ultrasonic():  # Alias that calls the ultrasonic sensor. This function exists so we can change it later.
    sleep(0.125) # Supposedly, the ultrasonic sensor locks up when checked more than 1/100ms
    n = sSonic.distance_centimeters
    return n


def color():  # Alias calling colour sensor. Wish it was sColour.colour, but y'know
    n = sColor.color
    return n


def log(s=""):
    f = open("log.txt", "a")
    f.write("\n" + ctime(time()) + " " + str(s))
    f.close()

def routeLog(s=""): # I don't think we'll end up using this
    f = open("routeLog.txt", "a")
    f.write(str(s)+", ")
    f.close()


# rotates right wheel forward, to turn left
def rotateDegreesLeft(degrees):
    amount = 0.94 / 90
    mRight.on_for_rotations(SpeedPercent(20), amount * degrees)
    sleep(0.1)

    global orientation
    orientation -= degrees
    if orientation < 0:
        orientation = 360 - orientation
    orientation = orientation % 360


# rotates left wheel forward, to turn right
def rotateDegreesRight(degrees):
    amount = 0.94 / 90
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


# uses tank rotate to move to a desired rotation
def changeOrientation(desiredOrientation):
    while orientation != desiredOrientation:
        if orientation < desiredOrientation:  # make sure we turn using the appropriate direction
            tankRotateRight(90)
        else:
            tankRotateLeft(90)


# SEEKING FUNCTIONS ----------------------------------------------------------------------------------------------------


# verifies black tiles by taking multiple point color checks, returns true if it is a black square.
def checkIfBlackTile():
    blackSensorCheck = 0
    for i in range(2):  # (value used to be 4)
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
                sleep(0.1)
                foundBlackTile = True


# start at tile 1. If not, the math.ceil function will break
def findBlackTile(desiredTile):
    global currentTileNum

    while currentTileNum != desiredTile:  # until you find the desired tile
        # if desired tile is ABOVE the current row, need to travel UP
        if math.ceil(desiredTile / 15) < math.ceil(currentTileNum / 15):
            changeOrientation(0)
            countBlackTile()  # then count squares until you find the tile

        # if desired tile is BELOW the current row, need to travel DOWN
        elif math.ceil(desiredTile / 15) > math.ceil(currentTileNum / 15):
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


# HAVE NOT IMPLEMENTED, BUT SHOULD HOPEFULLY WORK
def scanColumn(columnNumber):
    global towerDist  # towers distance
    global towerCol  # towers column

    failureAddition = failures * 15  # NEEDS TO BE FIXED!!!!!!!! GOES TO 56 ON FAILURE 2.

    findBlackTile(columnTiles[columnNumber] + failureAddition)
    changeOrientation(90)  # make sure its facing 90 degrees, may not be needed.

    if columnNumber != 2:  # if column 1 or 3 (with 2 black tiles on the edge of the big tile)
        tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.2)  # drive to center of tile
        rotateDegreesRight(90)  # turn right, to face down (180) to scan
        tempDist = ultrasonic()
        rotateDegreesRight(-90)  # reverse the turn
        if tempDist < towerDist:  # if current distance is less than the last tower distance
            towerDist = tempDist  # then update the tower variables
            towerCol = columnNumber
            return True

    else:  # if column 2 (with black tile in center of the big tile)
        changeOrientation(180)  # pivot to face down
        tempDist = ultrasonic()
        if tempDist < towerDist:  # if current distance is less than the last tower distance
            towerDist = tempDist  # then update the tower variables
            towerCol = columnNumber
            return True
    return False


# SCANS DOWN THE TOWERS COLUMN
def scanTowerColumn(rowNumber):
    if towerCol == 1:  # scan 45 to right COLUMN 1
        findBlackTile(57 + (rowNumber * 15))
        changeOrientation(180)

        tankRotateRight(30)
        sleep(0.1)
        tempDist = ultrasonic()
        sleep(0.2)
        tankRotateRight(-30)
        if tempDist < 20:
            return True
        else:
            return False

    elif towerCol == 2:  # center COLUMN 2
        findBlackTile(58 + (rowNumber * 15))
        changeOrientation(180)

        if ultrasonic() < 20:
            return True
        else:
            return False

    elif towerCol == 3:  # scan 45 to left COLUMN 3
        findBlackTile(59 + (rowNumber * 15))
        changeOrientation(180)

        tankRotateLeft(30)
        sleep(0.1)
        tempDist = ultrasonic()
        sleep(0.2)
        tankRotateLeft(-30)
        if tempDist < 20:
            return True
        else:
            return False

    else:
        return False


# seeks the tower by scanning each of the 3 tower tile columns, reports back the towers column
def seekTower():
    global foundTower
    global towerCol
    global towerDist

    # scanning da tower
    for x in range(1, 4):
        announce("scanning column" + str(x))
        if scanColumn(x):
            for y in range(4-failures):
                if scanTowerColumn(y):
                    return True
    return False


# EVENT CODE -----------------------------------------------------------------------------------------------------------


# SEEK VARIABLES
towerDist = 255
towerCol = 0
failures = 0
foundTower = False


# CHANGEABLE VARIABLES
orientation = 90 # 0, 90, 180, 270
currentTileNum = 55


# PROCESSES ---------------------------------

# sound.play_file('start.wav')
for i in range(4):
    if seekTower():
        announce("fantastic")
        announce("tile " + str(keyTiles[currentTileNum]))
        announce("column " + str(towerCol))
        # sound.play_file('victory.wav')
        break
    else:
        failures += 1
announce("finished")

"""

"""
