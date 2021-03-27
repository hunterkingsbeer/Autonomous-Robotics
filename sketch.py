# The idea would be to incorporate the correction function in the findBlackTile function, where the correction function
# would be called based on the iterations since the findBlackTile function were called.
# This solution uses modulus, which means it will check roughly every nth tile where n is decided by the orientation
# it's not going to be perfect because I can't be fucked rearranging the function to make it perfect- but, modulus will
# be absolutely fine. Any correction is better than no correction. First explaination in green is the pseudocode,
# second explaination is a way to incorporate it into findBlackTile.
# The major upside to not rearranging the function is that we can use the presumed success of the change orientation
# function to avoid running a conditional.
#
# PERSONALLY, i think we could decrease the frequency of corrections. but also it's fine to yell at me when i'm wrong.
"""

findBlackTile:
    if the direction is 0 or 180, always correct() after moving one title.
    if the direction is 270 or 90, correct() if currentTileNum % 2 == 0


THE MAJOR CONCERN WITH THIS IS THE MULTIPLES OF DEGREES WE TURN. IT DOENS'T MATTER IF A DEGREE ITSELF IS WRONG,
BUT IT /MUST/ BE CONSISTENT. IT MIGHT END UP MAKING MORE SENSE TO TURN IN MULTIPLES OF 5 AND USE OPTION B

correct():

    while the colour is black
        turn left with the left wheel for 1 degree
        increment leftDegrees
    turn right with the left wheel for leftDegrees (undo what we did)

    while the colour is black
        turn right with the right wheel for 1 degree
        increment rightDegrees
    turn left with the right wheel for rightDegrees (undo what we did)

    OPTION A (Absolute degrees): # Remember, we store correctionsTotal to undo them if it impacts us negatively later in the test.
        if leftDegrees > rightDegrees:
            turn (leftDegrees-rightDegrees) degrees left # LINE A
            correctionsTotal-=(leftDegrees-rightDegrees) # If the robot is facing 0, +ve numbers are right, so we subtract
        if rightDegrees == leftDegrees:
            break()
        if rightDegrees > leftDegrees:
            turn (rightDegrees-leftDegrees) degrees right # LINE B
            correctionsTotal+=(rightDegrees-leftDegrees) # If the robot is facing 0, +ve numbers are right, so we add

    OPTION B (multiples of 5): # Replace LINE A and LINE B as follows
            LINE A: turn (math.ceil((leftDegrees-rightDegrees/5)-1))*5 left
            LINE B: turn (math.ceil((rightDegrees-leftDegrees/5)-1))*5 right

            These lines turn the difference in degrees to the next multiple of 5 DOWN, not up.

"""

# this uses poor colour sensing-- which is personally, fine.
# also, this is option A.
# oh and the turn function might not be the one you want? but i mean i'm just illustrating

correctionsTotal=0

def correct():

    global correctionsTotal
    leftDegrees=0
    rightDegrees=0
    while color() == 1:
        reverseRotateLeft(1)
        leftDegrees+=1
    reverseRotateRight(leftDegrees)
    while color() == 1:
        reverseRotateRight(1)
        rightDegrees+=1
    reverseRotateLeft(rightDegrees)

    if leftDegrees > rightDegrees:
        reverseRotateLeft(leftDegrees - rightDegrees)
        correctionsTotal -= (leftDegrees - rightDegrees)  # If the robot is facing 0, +ve numbers are right, so we subtract
    if rightDegrees == leftDegrees:
        break()
    if rightDegrees > leftDegrees:
        reverseRotateRight(rightDegrees - leftDegrees)
        correctionsTotal += (rightDegrees - leftDegrees)  # If the robot is facing 0, +ve numbers are right, so we add

def findBlackTile(desiredTile):

    global currentTileNum

    while currentTileNum != desiredTile:  # until you find the desired tile
        # if desired tile is ABOVE the current row, need to travel UP
        if math.ceil(desiredTile / 15) < math.ceil(currentTileNum / 15):
            changeOrientation(0)
            countBlackTile()  # then count squares until you find the tile
            correct()

        # if desired tile is BELOW the current row, need to travel DOWN
        elif math.ceil(desiredTile / 15) > math.ceil(currentTileNum / 15):
            changeOrientation(180)
            countBlackTile()  # then count squares until you find the tile
            correct()

        # if desired tile is WITHIN the current row, need to travel LEFT or RIGHT
        elif math.ceil(desiredTile / 15) == math.ceil(currentTileNum / 15):

            # if the desired tile is to the LEFT of the robot
            if desiredTile < currentTileNum:
                changeOrientation(270)  # face left
                countBlackTile()
                if currentTileNum % 2 == 0:
                    correct()

            # if the desired tile is to the RIGHT of the robot
            elif currentTileNum < desiredTile:
                changeOrientation(90)  # face right
                countBlackTile()
                if currentTileNum % 2 == 0:
                    correct()

    # announce when you find the desired tile
    if currentTileNum == desiredTile:
        announce("FOUND " + str(desiredTile))













































 # eyyy don't even worry about it

"""# Unused tile diagnostics
desiredRow=math.ceil(desiredTile/15)
currentRow=math.ceil(currentTileNum/15)
roundedDesired=desiredTile-(desiredTile%abs(deltaTile[orientation]))
tileRemainder = desiredTile - (desiredTile % abs(deltaTile[orientation]))

# the best code i have written in years.
if math.ceil(desiredTile/15) != math.ceil(currentTileNum/15):
    outsideRange=True

# Tower tile if the tower is detected and you are facing the tower.
towerTile=keyTile[currentTileNum+deltaTile[orientation]]

# Reflect shit
def reflect():
    n = sColor.reflected_light_intensity
    return n

def luminance(groundTuple):
    return (groundTuple[0] * 0.2126) + (groundTuple[1] * 0.7152) + (groundTuple[2] * 0.0722)

def testreflect():
    announce("Luminance: " + str(luminance(sColor.raw)))
    announce("Reflectivity: " + str(reflect()))


# Wait until motors aren't moving. May be a better replacement for sleep.
def velocityZero():
    mLeft.wait_until_not_moving(100)
    mRight.wait_until_not_moving(100)

sound.play_file('start.wav')
sound.play_file('victory.wav')

"""'''
Grey:
Lum: 145.0266
Refle: 38
Lum: 153.458
Refle: 40

Grout:
Lum:  76.5390000000~ funny
Refle: 22

White:
Lum: 178~176
Ref: 50
Lum: 194
Ref: 54

Black:
Lum: 46.637
Reflect: 11'''
"""

#redefine the seekTower to have a failure variable defaulting to 0.

#change your findBlackTile to something like findBlackTile(columnTiles[1+(15*failures)])
'
#do this in the event loop
for i in range (2):
    seekTower(failures=i)'
    
"""
"""
columnTiles = {
    1: 56,
    2: 58,
    3: 59
}
print(columnTiles)

def incrementColumnTiles():
    for i in columnTiles:
        columnTiles[i]=columnTiles[i]+15

def decrementColumnTiles():
    for i in columnTiles:
        columnTiles[i]=columnTiles[i]-15

while not seektower():
    incrementColumnTiles()

"""