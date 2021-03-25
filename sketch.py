# Unused tile diagnostics
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
    announce("Luminance: " + str(luminance(sColor.raw())))
    announce("Reflectivity: " + str(reflect()))

