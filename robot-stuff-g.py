#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent
from ev3dev2.sound import Sound
from time import sleep
import math

# Needed "public" Variables

bSquareXdis = 0
bSquareYdis = 0
currentSquare = 0
squareLength = 0
ninetyDegreeTurnRotations = 0 # set this
xSquares = 0
ySquares = 0

# used so our robot learns the exact distances and sizes of our black squares
def CalculateBlackSquareParams():
    # drive forward until black square
    # drive to top of black square and save the length
    # go back that length
    # go backwards until next black sqare
    # update square (+15)
    # record distance and save as bSquareYdis
    # move 1/2 squarelegth from start of square
    # 90 degreeturn clockwise with pivot on the square
    # go to furthest edge of square
    # travel to next square
    # update square (+1)
    # save distance travelled as bSquareXdis
    # go to middle of black square (drive forward 1/2 squarelength)
    # rotate 90 degrees and detect using sonar the tower, method? (findTower())
    findTower()
    
# uses sensor while turning to locate tower, hopefully accurately reports distance
def findTower():
    wheelRotations = 0
    # start rotating, incrementing rotations as a float
    # also sensing for tower, maybe a while loop?
    #  WHILE(wheelRotations != required90rotations){
    #       rotate
    #       increment wheelRotations
    #       sense for tower
    #       if towersensed break
    # hypotenuse
    # theta = calculateAngle(wheelRotations)
    # xSquares = xDistanceToTower(theta, hypotenuse)
    # ySquares = yDistanceToTower(theta, hypotenuse)
    travelToTower()

# returns an angle the robot has rotated from the origin as degrees
def calculateAngle(wheelRotations):
    # find percentage of wheel rotations turned over rotations needed for
    # a 90 degree turn
    ratio = wheelRotations / ninetyDegreeTurnRotations
    angle = 90 * ratio
    return angle

# with the following functions there is a chance they may be in degrees or
# radians, testing is needed (degrees preffered)

# returns the number of black squares needed to travel horizontally
def xDistanceToTower(theta, hypotenuse):
    xDis = hypotenuse * math.cos(theta)
    horizontalSquares = xDis / (bSquareXdis + squareLength)
    return horizontalSquares

#returns the number of black squares needed to travel vertically
def yDistanceToTower(theta, hypotenuse):
    yDis = hypotenuse * math.sin(theta)
    horizontalSquares = yDis / (bSquareYdis + squareLength)
    return verticalSquares

def travelToTower():
# from here, rotate back to origin x plane, travel the required number of
# black squares horizontally
# turn 90 degrees clockwise
# resense tower
# if tower, travel needed black squares vertically and slow down on approach
#   to tower, use bump sensors to sense collision with tower and report
#   the big square number it is in (how do we do this)
# else findTower() badabing badaboom
    print ("yeah boy")