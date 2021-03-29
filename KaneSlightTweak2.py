#!/usr/bin/env python3

# Imports
import math
from time import sleep, time, ctime

from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank, MoveSteering
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor
from ev3dev2.sound import Sound

SIMULATOR = False

# Initialize dictionaries
deltaTiles = {  # Orientations to delta tile positions. Usage would be tile+=deltaTiles[orientation]
    0: -15,
    90: 1,
    180: 15,
    270: -1,
    360: -15
}

columnTiles = {
    1: 56, 2: 58, 3: 59,
    4: 71, 5: 73, 6: 74,
    7: 86, 8: 88, 9: 89,
    10: 101, 11: 103, 12: 104
}

keyTiles = {
    56: 1, 57: 1, 58: 2, 59: 3, 60: 3,
    71: 4, 72: 4, 73: 5, 74: 6, 75: 6,
    86: 7, 87: 7, 88: 8, 89: 9, 90: 9,
    101: 10, 102: 10, 103: 11, 104: 12, 105: 12
}

sound = Sound()
mLeft = LargeMotor(OUTPUT_B)
mRight = LargeMotor(OUTPUT_C)
sColor = ColorSensor()
sSonic = UltrasonicSensor()

steering_drive = MoveSteering(OUTPUT_B, OUTPUT_C)
tank_drive = MoveTank(OUTPUT_B, OUTPUT_C)


def announce(string, pause=True):
    print(string)
    if SIMULATOR is False:
        if not pause:
            sound.speak(string, play_type=sound.PLAY_NO_WAIT_FOR_COMPLETE)
        else:
            sound.speak(string)
    log(string)


def ultrasonic():  # returns the current ultrasonic distance
    sleep(0.125)
    n = sSonic.distance_centimeters  # Supposedly, the ultrasonic sensor locks up when checked more than 1/100ms
    return n


def color():  # return the current color
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

# MOVE FUNCTIONS -------------------------------------------------------------------------------------------------------


# rotates (only) the right wheel forward, to turn left.
def rotateDegreesLeft(degrees, correcting=False):
    degreeAmount = 0.94 / 90
    mRight.on_for_rotations(SpeedPercent(20), degreeAmount * degrees)
    if not correcting:  # ignore orientation if doing corrections, otherwise update current orientation
        updateOrientation(degrees)
    sleep(0.1)


# rotates (only) the left wheel forward, to turn right.
def rotateDegreesRight(degrees, correcting=False):
    degreeAmount = 0.94 / 90
    mLeft.on_for_rotations(SpeedPercent(20), degreeAmount * degrees)
    if not correcting:  # ignore orientation if doing corrections, otherwise update current orientation
        updateOrientation(degrees)
    sleep(0.1)


# rotates (only) the left wheel backwards, to turn left.
def reverseRotateLeft(degrees):
    mLeft.on_for_rotations(SpeedPercent(-20), degreeAmount * degrees)
    updateOrientation(degrees)
    sleep(0.1)


# rotates (only) the right wheel backwards, to turn right.
def reverseRotateRight(degrees):
    mRight.on_for_rotations(SpeedPercent(-20), degreeAmount * degrees)
    updateOrientation(degrees)
    sleep(0.1)


# rotates both wheels opposite, to turn left on the spot.
def tankRotateLeft(degrees):
    tank_drive.on_for_rotations(SpeedPercent(-20), SpeedPercent(20), degreeAmount/2 * degrees)
    updateOrientation(degrees)
    sleep(0.1)


# rotates both wheels opposite, to turn right on the spot.
def tankRotateRight(degrees):
    tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(-20), degreeAmount/2 * degrees)
    updateOrientation(degrees)
    sleep(0.1)


# used by turning methods to update current orientation.
def updateOrientation(degrees):
    global orientation
    orientation += degrees
    if orientation < 0:
        orientation = 360 - orientation
    orientation = orientation % 360


# rotate to move to a desired rotation, 0, 90, 180, 270.
def changeOrientation(desiredOrientation, willCorrect = True):
    while orientation != desiredOrientation:
        if orientation < desiredOrientation:  # make sure we turn using the appropriate direction
            tankRotateRight(90)
        else:
            tankRotateLeft(90)
    if willCorrect and currentTileNum != 1:
        correction()


# SEEKING FUNCTIONS ----------------------------------------------------------------------------------------------------


# verifies black tiles by taking multiple point color checks, returns true if it is a black square.
def checkIfBlackTile():
    blackSensorCheck = 0
    for i in range(4):  # (value used to be 4)
        sleep(0.1)
        if color() == 1:
            blackSensorCheck += 1
        tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.01)  # (used 0.08)
        sleep(0.2)

    if blackSensorCheck >= 2:  # If 2 checks showed black, its a black square. (value used to be 4)
        return True
    else:
        return False


# drives until it can count another black tile, upon which it increments the current tile number.
def countBlackTile():
    global currentTileNum
    foundBlackTile = False
    foundWhiteAgain = False

    while not foundBlackTile:  # to ensure we dont double scan we need to see white before verifying black
        if color() == 6:  # when white, toggle
            foundWhiteAgain = True

        if orientation == 180:  # if robot is travelling down a column
            tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.12)  # drive forward more rotations
        else:  # else robot is travelling across a row
            tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.1)  # drive forward
        sleep(0.2)
        if color() == 1 and foundWhiteAgain:  # then check if its a black square, and verify
            if checkIfBlackTile():
                currentTileNum += deltaTiles[orientation]
                announce(str(currentTileNum))
                foundBlackTile = True


# start at tile 1. If not, the math.ceil function will break #
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

    tank_drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), 0.2)
    # announce when you find the desired tile
    #if currentTileNum == desiredTile:
        #announce("TILE " + str(desiredTile))
        #announce("ROW " + str(math.ceil(currentTileNum / 15)))


# Checks if tower is within reasonable distance. Returns true if distance put in is less than 20cm, false if not.
def isTower(distance):
    if distance < 20:
        return True
    else:
        return False


# SCANS DOWN THE TOWERS COLUMN
def scanTowerColumn(rowNumber):
    if towerCol == 1:
        findBlackTile(57 + (rowNumber * 15))
        changeOrientation(180)
        tankRotateRight(25)
        firstDist = ultrasonic()
        tankRotateRight(10)
        secondDist = ultrasonic()
        tankRotateRight(-35)
        return isTower(firstDist if firstDist < secondDist else secondDist)

    elif towerCol == 2:
        findBlackTile(58 + (rowNumber * 15))
        changeOrientation(180)
        return isTower(ultrasonic())

    elif towerCol == 3:
        findBlackTile(59 + (rowNumber * 15))
        changeOrientation(180)
        tankRotateLeft(25)
        firstDist = ultrasonic()
        tankRotateLeft(10)
        secondDist = ultrasonic()
        tankRotateLeft(-35)
        return isTower(firstDist if firstDist < secondDist else secondDist)
    else:
        return False

# searches down column to look for the
def scanColumn(columnNumber):
    global towerDist  # towers distance
    global towerCol  # towers column
    failureAddition = failures * 15  # num of failures = row to scanning, use this to get its failure addition

    findBlackTile(columnTiles[columnNumber] + failureAddition)
    changeOrientation(90)  # make sure its facing 90 degrees, may not be needed.

    if columnNumber != 2:  # if column 1 or 3 (with 2 black tiles on the edge of the big tile)
        tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.2)  # drive to center of tile
        rotateDegreesRight(90)  # turn right, to face down (180) to scan
        tempDist = ultrasonic()
        rotateDegreesRight(-90)  # reverse the turn
        tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), -0.2)
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


# Seeks the tower by scanning each of the 3 tower tile columns, reports back the towers column
def seekTower():
    for x in range(1, 4):
        announce("scanning tower column" + str(x))
        if scanColumn(x):
            announce("found tower, dist " + str(towerDist))
            for y in range(4-failures):  # MAY NEED TO ALTER THIS TO WORK BETTER !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                announce("row" + str(y))
                if scanTowerColumn(y):
                    return True
    return False


# Takes 2 black/white color point checks, one further than the last, for both left and right.
# Appropriately adjusting away from the side with the most white.
def correction():
    tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.2)
    searchArea = 50  # 40 degrees search
    left = 0  # left amount counter
    right = 0  # right amount counter
    multiplier = 1  # multiplier for orientation based corrections, 1 for 90/270, and 0.3 for 0/180

    if orientation == 180 or orientation == 0:  # set multiplier for orientation correctly
        multiplier = 0.25  # needs to be less to account for further distance between black tiles when travelling down

    # check left, 2 times
    for i in range(1, 3):
        rotateDegreesLeft(searchArea / 2, True)
        if color() == 6:
            #   announce(str(i))
            left += i  # try 1: +1, try 2: +2
    rotateDegreesLeft(-searchArea, True)  # return to initial position before scan

    # check right, 2 times
    for i in range(1, 3):
        rotateDegreesRight(searchArea / 2, True)
        if color() == 6:
            #announce(str(i))
            right += i  # try 1: +1, try 2: +2
    rotateDegreesRight(-searchArea, True)  # return to initial position before scan

    if right > left:  # must be to the RIGHT side of a black square, TURN LEFT
        rotateDegreesLeft((5 * right) * multiplier, True)
    elif left > right:  # must be to the LEFT side of a black square, TURN RIGHT
        rotateDegreesRight((5 * left) * multiplier, True)

    sleep(0.1)  # have a nice little sleep, why not

def calibrate():
    changeOrientation(180, False)
    while color() == 1:
        tank_drive.on_for_rotations(SpeedPercent(20), SpeedPercent(20), 0.1)
    announce("calibrate white")
    sColor.calibrate_white()


    # EVENT CODE -----------------------------------------------------------------------------------------------------------

# SEEK VARIABLES
towerDist = 200  # Distance of tower. Default set to the max 255cm.
towerCol = 0  # Column of the tower. Default set to 0.
failures = 0  # Counts failures to detect tower after scanning all 3 columns in the row.

# CHANGEABLE VARIABLES
orientation = 0  # 0, 90, 180, 270
currentTileNum = 1
scannedCol1 = False
scannedCol2 = False
scannedCol3 = False

# OTHER VARIABLES
degreeAmount = 0.938 / 90


# MAIN PROCESSES --------------------------------


calibrate()
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
announce("finished.")
