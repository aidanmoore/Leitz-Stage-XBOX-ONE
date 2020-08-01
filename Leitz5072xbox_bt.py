########### Aidan Moore XBox Control of Trinamic Motor Drivers
# Aug 1st  2020
# This version is for dual 5072 driving the Leitz stage and the Polarizer motor
# With twos compliment Z axis readout
#
# With Raspberry Pi 4 4GB
# Motor Supply 12 Volts or Greater

# Uses SPI to send and receive data from Raspberry Pi, (0) for TMC5072 #1 (ENN GPIO 12 {pin 32}) and (1) for TMC5072 #2 (ENN GPIO 21 {pin 40})
#     Works with Python 3
#
#   Run sudo pigpiod before starting program (in batch file)
# This is part of bashrc ie nano ~/ .bashrc
#   alias python='/usr/bin/python3'
# alias pip=pip3
#  sudo pigpiod
# run as :  sudo python3 1axis_rawPLAY.py
#
#sudo /usr/bin/python3.5 2axis_XBOX_position.py
#

#     

# Import Libraries
from __future__ import print_function
import subprocess
import time
import pigpio
import chipdrive_5072_Dual_exp_A1, chipdrive_5072_Dual_exp_A2 # This is Trinamic chipdrive for Dual TMC5072 Chips 1 and 2
import trinamicDriver,tmc5072regs

# Connect to pigpiod daemon
pi = pigpio.pi()

# Instantiate the XBOX BT controller (XBOX ONE)
import gamepad2 #this is an updated version with all buttons mapped
import asyncio # asyncio is needed to use the Bluetooth version of the XBOX controller
import evdev #import InputDevice, ff, ecodes
joy = gamepad2.gamepad

# Set Raspberry ports for motors
motorport1 = 12 # Motor GPIO enable port number 12 for driver #1 on Raspberry Pi 3
motorport2 = 21 # Motor GPIO enable port number 23 for 5160 driver #2 on Raspberry Pi 3
polarizer_AIN1 =14   #Polarizer GPIO 
polarizer_AIN2 =15   #Polarizer GPIO 
pi.set_mode(motorport1, pigpio.OUTPUT) # Set driver chip #1 port to output
pi.set_mode(motorport2, pigpio.OUTPUT) # Set driver chip #2 port to output
pi.write(motorport1, 1) # Set motor port initally to 1 to disable
pi.write(motorport2, 1) # Set motor port initally to 1 to disable

pi.set_mode(polarizer_AIN1, pigpio.OUTPUT) # Set polarizer port to output
pi.set_mode(polarizer_AIN2, pigpio.OUTPUT) # Set polarizer  port to output
pi.set_PWM_frequency(polarizer_AIN1,60)
pi.set_PWM_dutycycle(polarizer_AIN1,0)
pi.set_PWM_frequency(polarizer_AIN2,60)
pi.set_PWM_dutycycle(polarizer_AIN2,0)

################################################### User functions ######################################################
def twoscomp(inval):       #Convert 32 bit twos compliment register values to signed integer values
    if inval > 2147483647:
        inval = -(4294967295 - inval)
    return inval

################################################### For TMC5072 #1 ######################################################

# Number 1 Motor X (Purple Dot Motor #1 on PCB) and Rail Setup Parameters
# This is for KR15 Rail with 1mm pitch, 30mm range, 200 step, 5.6 ohm, 4.8mH, 640ma Motor
# Controller is Trinamic #1 TMC-5072 SPI (0) ENN GPIO 12


xmotorstep = 400 # Motor steps per rotation
xvmax = 256000 # Maximum velocity count in rotation/sec vmax/motorstep/microstep
xamax = 1100 # Maximum acceleration from v1 to vmax
xa1 = 200 # Maximum acceleration from vstart to v1
xdmax = 800 # Maximum deceleration from vmax to v1
xd1 = 300 # Final deceleration from v1 to vstop
xv1 = 250000 # Velocity transition rotation/sec v1/motorstep/microstep
xvstart = 10 # Inital start velocity in pulses/sec
xvstop = 20 # Final stop velocity in pulses/sec, Note must be > than vstart!

# Number 2 Y (Green Dot Motor #2 on PCB) Motor and Rail Setup Parameters
# This is for KR 15 Rail with 1mm pitch, 30mm range, 200 step, 5.6 ohm, 4.8mH, 640ma Motor
# Controller is Trinamic #1 TMC-5072 SPI (0) ENN GPIO 12


ymotorstep2 = 400 # Motor steps per rotation
y2vmax = 256000 # Maximum velocity count in rotation/sec vmax/motorstep/microstep
y2amax = 1100 # Maximum acceleration from v1 to vmax
y2a1 = 200 # Maximum acceleration from vstart to v1
y2dmax = 800 # Maximum deceleration from vmax to v1
y2d1 = 300 # Final deceleration from v1 to vstop
y2v1 = 250000 # Velocity transition rotation/sec v1/motorstep/microstep
y2vstart = 10 # Inital start velocity in pulses/sec
y2vstop = 20 # Final stop velocity in pulses/sec, Note must be > than vstart!

# Read in data from Trinimac Specific Controller
# Note this is tmc5072 #1 define as "mot1"
md1=trinamicDriver.TrinamicDriver(datarate=1000000, motordef=tmc5072regs.tmc5072, drvenpin=12, spiChannel=0) # Setup md for reading position
mot1=chipdrive_5072_Dual_exp_A1.tmc5072(stepsPerRev=xmotorstep, vmax=xvmax, amax=xamax, a1=xa1, dmax=xdmax, d1=xd1, v1=xv1, vstart=xvstart, vstop=xvstop, v2max=y2vmax, a2max=y2amax, a21=y2a1, d2max=y2dmax, d21=y2d1, v21=y2v1, v2start=y2vstart, v2stop=y2vstop) # Activate Chip Drive for TMC5072 as mot1

################################################### For TMC5072 #2 ######################################################

zmotorstep = 400 # Motor steps per rotation
zvmax = 128000 # Maximum velocity count in rotation/sec vmax/motorstep/microstep
zamax = 600 # Maximum acceleration from v1 to vmax
za1 = 400 # Maximum acceleration from vstart to v1
zdmax = 800 # Maximum deceleration from vmax to v1
zd1 = 300 # Final deceleration from v1 to vstop
zv1 = 25000 # Velocity transition rotation/sec v1/motorstep/microstep
zvstart = 10 # Inital start velocity in pulses/sec
zvstop = 20 # Final stop velocity in pulses/sec, Note must be > than vstart!


# Read in data from Trinimac Specific Controller
# Note this is tmc5072 #2 define as "mot2"
md2=trinamicDriver.TrinamicDriver(datarate=1000000, motordef=tmc5072regs.tmc5072, drvenpin=23, spiChannel=1) # Setup md for reading position
mot2=chipdrive_5072_Dual_exp_A2.tmc5072(stepsPerRev=zmotorstep, vmax=zvmax, amax=zamax, a1=za1, dmax=zdmax, d1=zd1, v1=zv1, vstart=zvstart, vstop=zvstop) # Activate Chip Drive for TMC5072 as mot2


# Set Motor 1 Default Currents and Irun to Ihold Delay 
xihold = 0 # R motor hold current imax*(ihold + 1)/32
xirun = 14 # R motor run current imax*(irun + 1)/32
xihdelay = 4 # R motor hold delay (irun-ihold)*ihdelay*2^18/fclock
mot1.xmotorcurrent(xihold, xirun, xihdelay) # Write motor currents and hold delay



# Set Motor 2 Default Currents and Irun to Ihold Delay 
yihold2 = 0 # R motor hold current imax*(ihold + 1)/32
yirun2 = 14 # R motor run current imax*(irun + 1)/32
yihdelay2 = 4 # R motor hold delay (irun-ihold)*ihdelay*2^18/fclock
mot1.ymotorcurrent2(yihold2, yirun2, yihdelay2) # Write motor currents and hold delay

time.sleep(1.5) # this prevents an unknown inrush current on TMC5160

# Set Motor 3 Default Currents and Irun to Ihold Delay 
zihold = 0 # R motor hold current imax*(ihold + 1)/32
zirun = 14 # R motor run current imax*(irun + 1)/32
zihdelay = 4 # R motor hold delay (irun-ihold)*ihdelay*2^18/fclock
mot2.zmotorcurrent(zihold, zirun, zihdelay) # Write motor currents and hold delay


mot1.xdenergize() # Denergize Motor 1 TMC5072 Chip #1
mot1.ydenergize2() # Denergize Motor 2 TMC5072 Chip #1
# mot2.zdenergize() # Denergize Motor 1 TMC5072 Chip #1 disabled due to jerk



################################################### Main Routine ######################################################

try:
    async def main():
        # Stacking Camera & Strobe Trigger Parameters
        cameraport = 20 # Camera GPIO trigger port number 20 on Raspberry Pi 3
        strobeport = 16 # Strobe GPIO trigger port number 16 on Raspberry
        ledcameraport = 26 # Camera LED (Blue) GPIO trigger port number 26 on Raspberry Pi 3
        ledstrobeport = 19 # Strobe LED (Red or White) GPIO trigger port number 19 on Raspberry Pi 3

        
        XFLAG = 0 # 1 = deenergized and target reached 0 = target not reached
        YFLAG = 0 # 1 = deenergized and target reached 0 = target not reached
        ZFLAG = 0
        XNOW = 0 # Current value of X motor joystick value
        YNOW = 0 # Current value of Y motor joystick value
        ZNOW = 0
        POLCW = 0
        POLCCW = 0
        
        XOLD = 0
        YOLD = 0
        ZOLD = 0
        ZTEMP = 0

        XPOS = md1.readInt('XACTUAL')
        YPOS = md1.readInt('X2ACTUAL')
        ZPOS = md2.readInt('XACTUAL')
        print ('Starting Z postion ZPOS = ', ZPOS)
        ZSCALE = 2 #start in fine mode
        keep_going = True
    
################################################### Main Loop ###################################################### 

        while keep_going:
            
            # Read the Joystick values
            XNOW = round(remote_control.joystick_left_x,4)
            YNOW = round(remote_control.joystick_left_y,4)
            ZNOW = remote_control.joystick_right_y
            POLCW = round((remote_control.trigger_right)/32)  #Get scaled PWM Data for Polarizer CW motor direction range 0 -32
            POLCCW = round((remote_control.trigger_left)/32)  #Get scaled PWM Data for Polarizer CCW motor direction range 0 -32
            
            if  abs(XNOW) >0.1:  # if the Joystick is not in deadband  
                XPOS = XPOS + 20 * XNOW #Change the target
                mot1.xgotonowait(XPOS) # Go to the target Motor 1 (Purple)
                XFLAG = 1
            if  abs(YNOW) > 0.1:
                YPOS = YPOS + 20 * YNOW
                mot1.ygotonowait2(YPOS) # Write position count to Trinamic 5072 #1 Motor 2 (Green)
                YFLAG = 1
            if abs(ZNOW) > 0.05:
                ZOLD = ZTEMP
                ZPOS = ZPOS + ZSCALE * ZNOW
                mot2.zgotonowait(ZPOS) # Write position count to Trinamic 5072 Motor 3
                ZFLAG = 1
                
            if  POLCW > 5:     #setup to move CW
                 #print (' Clockwise ', POLCW)
                 pi.set_PWM_dutycycle(polarizer_AIN1,POLCW)
#                pi.set_PWM_dutycycle(polarizer_AIN2,0)
            elif POLCCW < 5 :
                 pi.set_PWM_dutycycle(polarizer_AIN1,0)
                
            if   POLCCW > 5:
                 #print (' Counter-clockwise ', POLCCW)
                 pi.set_PWM_dutycycle(polarizer_AIN2,POLCCW)
                 pi.set_PWM_dutycycle(polarizer_AIN1,0)
            elif POLCW < 5 :
                 pi.set_PWM_dutycycle(polarizer_AIN2,0)

    #
    # Now test if the motors have arrived at its target position. If it has, deenergize the motor.
    #   
            if md1.readInt('XACTUAL') == md1.readInt('XTARGET') and XFLAG == 1 : # if the target is reached and the flag is set  
                XFLAG = 0         # Clear the flag
                mot1.xdenergize() # Denergize Motor 1 TMC5072 Chip #1
                print (' X target reached ',md1.readInt('XACTUAL')  )   
            if md1.readInt('X2ACTUAL') == md1.readInt('X2TARGET') and YFLAG == 1 : # if the target is reached and the flag is set  
                YFLAG = 0         # Clear the flag
                mot1.ydenergize2() # Denergize Motor 2 TMC5072 Chip #1        
                print (' Y target reached ', md1.readInt('X2ACTUAL'))
            if md2.readInt('XACTUAL') == md2.readInt('XTARGET') and ZFLAG == 1 : # if the target is reached and the flag is set  
                ZFLAG = 0         # Clear the flag
                # mot2.zdenergize() # Denergize Motor 1 TMC5072 Chip #1 But getting jerk so disabled
                ZTEMP = md2.readInt('XACTUAL')
                ZTEMP = twoscomp(ZTEMP)
                print (' Just moved from ', ZOLD, 'to ', ZTEMP, ' a distance of ', ZTEMP - ZOLD )

    #
    # Buttons
    #
            if remote_control.button_x: # Super fine
                remote_control.button_x = False
                ZSCALE = 0.5 #fine mode
                print ("Super Fine Mode")           
            if remote_control.button_y:
                remote_control.button_y = False
                ZSCALE = 2 #fine mode
                print ("Fine Mode")
            if remote_control.button_b: # play once strong rumble effect
                remote_control.button_b = False
                ZSCALE = 30 #coarse mode
                print ("Coarse Mode")
                remote_control.rumble_effect = 2
            if remote_control.button_a: #take picture
                remote_control.button_a = False
                pi.write (cameraport, 1) # Write 1 to camera port
                await asyncio.sleep(0.01) # set pulse width to 10ms
                print (" Snap ")     
                pi.write (cameraport, 0) # Set camera port back to 0
 
            if remote_control.button_back: # Exit program
                remote_control.button_back = False
                print ("Goodbye")
                sys.exit() 
 

            await asyncio.sleep(0)       

    remote_control = joy(file = '/dev/input/event0')
    futures = [remote_control.read_gamepad_input(), remote_control.rumble(), main()]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(futures))
    loop.close()

except: 
    mot1.xdenergize() # Denergize Motor 1 TMC5072 Chip #1
    mot1.ydenergize2() # Denergize Motor 2 TMC5072 Chip #1
    mot2.zdenergize() # Denergize Motor 1 TMC5072 Chip #1 disabled due to jerk
    pi.stop() #close gpio
    print ("Exit Routine!")         
