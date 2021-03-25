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
