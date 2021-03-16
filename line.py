from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent
from ev3dev2.sound import Sound
from ev3dev2.sensor.lego import TouchSensor, ColorSensor
from time import sleep
from ev3dev2.motor import MoveTank, MoveSteering

mLeft = LargeMotor(OUTPUT_B)
mRight = LargeMotor(OUTPUT_C)
sColor = ColorSensor()

steering_drive = MoveSteering(OUTPUT_B,OUTPUT_C)
tank_drive = MoveTank(OUTPUT_B, OUTPUT_C)

initiallyfound = False
init = True
sleep(1)
mLeft.on(speed=25)
mRight.on(speed=25)

while True:
    while initiallyfound == False:
        logicreset=0
        if init == True:
            sleep(2)
            init=False

        if sColor.color == 1:
            initiallyfound=True

    while sColor.color != 1 and initiallyfound == True:
        mRight.on(speed=-1) #cheeky equivalent of breaking
        mLeft.on(speed=-1)
        #sleep(0.5)
        mRight.on(speed=0)
        mLeft.on(speed=0)
        #sleep(0.5)
        while sColor.color !=1:
            mLeft.on(speed=10)
        mLeft.on(speed=0)
        #steering_drive.on_for_rotations(53.555, SpeedPercent(50), 1)
        #sleep(2)
        logicreset=logicreset+1

    else:
        logicreset=0
        mLeft.on(speed=25)
        mRight.on(speed=25)
    #print("Nice")
