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

