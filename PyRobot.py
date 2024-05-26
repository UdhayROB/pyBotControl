'''
Author - Udhaya Kumar Parameswaran
Date - 26-May-2024

Enable pigpio in auto-start by- sudo systemctl enable pigpiod
'''

import sys
import pigpio
import RPi.GPIO as GPIO
import datetime
from time import sleep
import pygame
import copy
import math

class servoSG90():
        def __init__(self, pinNo: int):
                self.pinNo = pinNo
                self.feedbackAngle = 90
                self.objectHolder = pigpio.pi()
                self.objectHolder.set_mode(self.pinNo, pigpio.OUTPUT)
                self.objectHolder.set_PWM_frequency(self.pinNo, 50)
                self.objectHolder.set_servo_pulsewidth(self.pinNo, 1500)
                sleep(1)

        def find_pulseWidth(self, angle: int):
                pulseWidth = (11.111 * angle) + 500
                if(pulseWidth < 500): pulseWidth = 500
                elif(pulseWidth > 2500): pulseWidth = 2500
                return pulseWidth 

        def set_angle_easing(self, angle, time):
                currentPulseWidth = round(self.find_pulseWidth(self.feedbackAngle))
                targetPulseWidth = round(self.find_pulseWidth(angle))
                stepSize = int((targetPulseWidth - currentPulseWidth) / (time * 50))
                if(stepSize):
                        for i in range(currentPulseWidth, targetPulseWidth, stepSize):
                                self.objectHolder.set_servo_pulsewidth(self.pinNo, i)
                                self.feedbackAngle = (i - 500) / 11.111
                                sleep(0.01)

        def set_angle(self, angle: int):
                targetPulseWidth = round(self.find_pulseWidth(angle))
                self.objectHolder.set_servo_pulsewidth(self.pinNo, targetPulseWidth)
                sleep(0.01)
                self.feedbackAngle = (targetPulseWidth - 500) / 11.111

        def close(self):
                self.objectHolder.set_PWM_dutycycle(self.pinNo, 0)
                self.objectHolder.set_PWM_frequency(self.pinNo, 0)

class stepperNEMA17():
        def __init__(self, name: str, directionPin: int, stepPin: int, stepsPerUnit: int, minTravel: int, maxTravel: int, pulseDelay: f>
                self.stepPin = stepPin
                self.directionPin = directionPin
                self.pulseDelay = pulseDelay
                self.name = name
                self.stepsPerUnit = stepsPerUnit
                self.stop = False
                self.currentPosition = 0.001 #Represents initial degrees
                self.maxTravel = maxTravel
                self.minTravel = minTravel
                GPIO.setup(self.directionPin, GPIO.OUT)
                GPIO.setup(self.stepPin, GPIO.OUT)
                GPIO.output(self.directionPin, True) # If True-> CW (Up) for Motor1 amd CCW for Motor2 and Motor3

        def continuous_rotate(self, direction):
                if(self.stop):
                        print("Motor Stopped")
                else:
                        if(((self.name != "Motor1") and  direction) or ((self.name == "Motor1") and not(direction))):
                                nextPosition = self.currentPosition - (1/self.stepsPerUnit)
                        elif(((self.name == "Motor1") and direction) or ((self.name != "Motor1") and not(direction))):
                                nextPosition = self.currentPosition + (1/self.stepsPerUnit)
                        if(nextPosition >= self.minTravel and nextPosition <= self.maxTravel):
                                GPIO.output(self.directionPin, direction)
                                if(self.name == "Motor2"):
                                        GPIO.output(motor3.directionPin, direction)
                                GPIO.output(self.stepPin, True)
                                if(self.name == "Motor2"):
                                        GPIO.output(motor3.stepPin, True)
                                sleep(self.pulseDelay)
                                GPIO.output(self.stepPin, False)
                                if(self.name == "Motor2"):
                                        GPIO.output(motor3.stepPin, False)
                                self.currentPosition = copy.deepcopy(nextPosition)
                                #print(self.currentPosition)
                        #else:
                                #print("Max Limit Reached")

        def move_relative(self, angle: float):
                if (angle == 0): return
                if (((angle + self.currentPosition) < self.minTravel) or ((angle + self.currentPosition) > self.maxTravel)): ret>
                for step in range(0, int(self.stepsPerUnit * abs(angle))):
                        if(angle < 0):
                                GPIO.output(self.directionPin, True)
                                if(self.name == "Motor1"):
                                        GPIO.output(self.directionPin, False)
                                elif(self.name == "Motor2"):
                                        GPIO.output(motor3.directionPin, True)
                                self.currentPosition -= (1/self.stepsPerUnit)
                        else:
                                GPIO.output(self.directionPin, False)
                                if(self.name == "Motor1"):
                                        GPIO.output(self.directionPin, True)
                                elif(self.name == "Motor2"):
                                        GPIO.output(motor3.directionPin, False)
                                self.currentPosition += (1/self.stepsPerUnit)
                        GPIO.output(self.stepPin, True)
                        if(self.name == "Motor2"):
                                GPIO.output(motor3.stepPin, True)
                        sleep(self.pulseDelay)
                        GPIO.output(self.stepPin, False)
                        if(self.name == "Motor2"):
                                 GPIO.output(motor3.stepPin, False)
                        sleep(self.pulseDelay)
                        #print(self.currentPosition)

        def motor_stop(self):
                self.stop = True

def inverseKinematics(x: float, y: float):
        if(x == 0): x=0.1 #To avoid atan(inf)
        try:
                q2 = (math.acos((x**2 + y**2 - robotArm2Lengthmm**2 - robotArm3Lengthmm**2) / (2 * robotArm2Lengthmm * robotArm3Lengthm>
                q1 = (math.atan2(y,x)) - math.atan((robotArm3Lengthmm * math.sin(q2))/(robotArm2Lengthmm + (robotArm3Lengthmm * math.co>
        except ValueError:
                return 0,0,False
        return math.degrees(q1),math.degrees(q2),True

def forwardKinematics(q1Deg: float, q2Deg: float):
        q1 = math.radians(q1Deg)
        q2 = math.radians(q2Deg)
        x = (robotArm3Lengthmm * math.cos(q1+q2)) + (robotArm2Lengthmm * math.cos(q1))
        y = (robotArm3Lengthmm * math.sin(q1+q2)) + (robotArm2Lengthmm * math.sin(q1))
        return x,y

def moveRelativePosition(x: float, y:float):
        currentq1, currentq2 = motor2.currentPosition, motor3.currentPosition
        currentX, currentY = forwardKinematics(currentq1, currentq2)
        targetX, targetY = currentX + x, currentY + y
        targetq1, targetq2, success = inverseKinematics(targetX, targetY)
        minMaxAnglesCheck = (targetq1 >= robotArm2MinAngledeg) and (targetq1 <= robotArm2MaxAngledeg)  and (targetq2 >= robotArm2MinAng>
        if(success and minMaxAnglesCheck ):
                motor2.move_relative(targetq1 - currentq1)
                motor3.move_relative(targetq2 - currentq2)
                if(panLock):
                        servo1.set_angle(180-targetq2-targetq1)

def moveToPosition(x: int, y:int, z: int):
        currentq1, currentq2 = motor2.currentPosition, motor3.currentPosition
        currentX, currentY = forwardKinematics(currentq1, currentq2)
        currentZ = motor1.currentPosition
        targetX, targetY, targetZ = x, y, z
        targetq1, targetq2, success = inverseKinematics(targetX, targetY)
        minMaxAnglesCheck1 = (targetZ >= robotArm1MinLengthmm) and (targetZ <= robotArm1MaxLengthmm)
        minMaxAnglesCheck2 = (targetq1 >= robotArm2MinAngledeg) and (targetq1 <= robotArm2MaxAngledeg)
        minMaxAnglesCheck3 = (targetq2 >= robotArm3MinAngledeg) and (targetq2 <= robotArm3MaxAngledeg)
        print(currentX, currentY, currentZ, targetX, targetY, targetZ)
        print(currentq1,currentq2, currentZ, targetq1, targetq2, targetZ)
        if(success and minMaxAnglesCheck1 and minMaxAnglesCheck2 and minMaxAnglesCheck3 ):
                motor1.move_relative(targetZ - currentZ)
                motor2.move_relative(targetq1 - currentq1)
                motor3.move_relative(targetq2 - currentq2)
                if(panLock):
                        servo1.set_angle(180-targetq2-targetq1)

def goToHomePosition():
        servo1.set_angle_easing(90, 0.5)
        servo2.set_angle_easing(90, 0.5)
        GPIO.output(motorsEnablePin, True)
        GPIO.output(motor1.directionPin, False)
        GPIO.output(motor1.directionPin, True)
        GPIO.output(motor1.directionPin, False)
        while(not(GPIO.input(motor1HomeSwitch))):
                GPIO.output(motor1.stepPin, True)
                sleep(motor1.pulseDelay)
                GPIO.output(motor1.stepPin, False)
                sleep(motor1.pulseDelay)
        for i in range(5*m1AxisStepsPermm):
                motor1.continuous_rotate(True)
        motor1.currentPosition = 0
        while(not(GPIO.input(motor2HomeSwitch))):
                GPIO.output(motor2.stepPin, True)
                sleep(motor2.pulseDelay)
                GPIO.output(motor2.stepPin, False)
                sleep(motor2.pulseDelay)
        motor2.move_relative(25)
        motor2.currentPosition = 0
        while(not(GPIO.input(motor3HomeSwitch))):
                GPIO.output(motor3.stepPin, True)
                sleep(motor3.pulseDelay)
                GPIO.output(motor3.stepPin, False)
                sleep(motor3.pulseDelay)
        motor3.move_relative(-50)
        motor3.currentPosition = 90
        GPIO.output(motorsEnablePin, False)

#Pin Declarations
GPIO.setmode(GPIO.BCM)
motorsEnablePin = 22
directionPinMtr1 = 27
stepPinMtr1 = 17
directionPinMtr2 = 5
stepPinMtr2 = 6
directionPinMtr3 = 23
stepPinMtr3 = 24
microstepPins = (-1,-1,-1)
servo1Pin = 12
servo2Pin = 13
motor1HomeSwitch = 1
motor2HomeSwitch = 7
motor3HomeSwitch = 8

#Variable Declarations
#Robot Parameters
robotArm1MinLengthmm = 0
robotArm1MaxLengthmm = 110
robotArm2MinAngledeg = -15
robotArm2MaxAngledeg = 195 # -10 to 190 degrees
robotArm3MinAngledeg = -130
robotArm3MaxAngledeg = 130 # +/- 135 degrees to Arm2
robotArm2Lengthmm = 92
robotArm3Lengthmm = 106
baseToArm2OffsetLengthmm = {"x":6.8,"y":0,"z":40}
panTiltOffsetLengthmm = {"x":10,"y":0,"z":36}
panLock = False

m1AxisStepsPermm = 200 # 45 deg = 1mm, 1 deg = 4.44 steps
m2AxisStepsPerDeg = 16 #Actual- 20, Steps per rev = 1600, Gear ratio = 4.5 --> 1600/360 * 4.5
m3AxisStepsPerDeg = 25 #Actual- 32.357, Steps per rev = 1600, Gear ratio = 7.2803 --> 1600/360 * 7.2803

#Motor Parameters
CCW = 0
CW = 1
motor1 = stepperNEMA17('Motor1', directionPinMtr1, stepPinMtr1, m1AxisStepsPermm, robotArm1MinLengthmm, robotArm1MaxLengthmm, 0.0003)
motor2 = stepperNEMA17('Motor2', directionPinMtr2, stepPinMtr2, m2AxisStepsPerDeg, robotArm2MinAngledeg, robotArm2MaxAngledeg, 0.001)
motor3 = stepperNEMA17('Motor3', directionPinMtr3, stepPinMtr3, m3AxisStepsPerDeg, robotArm3MinAngledeg, robotArm3MaxAngledeg, 0.001)
servo1 = servoSG90(servo1Pin)
servo2 = servoSG90(servo2Pin)
GPIO.setup(motor1HomeSwitch, GPIO.IN)
GPIO.setup(motor2HomeSwitch, GPIO.IN)
GPIO.setup(motor3HomeSwitch, GPIO.IN)
GPIO.setup(motorsEnablePin, GPIO.OUT)
GPIO.output(motorsEnablePin, False)

def main():
        goToHomePosition()
        choice = input('1. Teleoperate Individual Motors\n2. Teleoperate TCP\n3. Go to point\n4. Go Home')
        match choice:
                case '1':
                        GPIO.output(motorsEnablePin, True)
                        print('Individual Axis Teleop')
                        pygame.init()
                        pygame.key.set_repeat(1)
                        display = pygame.display.set_mode((300,300))
                        font = pygame.font.SysFont("Arial", 20)
                        axis1Text = font.render("Linear - Up  - W  Down - S", True, (255,255,255))
                        axis2Text = font.render("Arm 1  - Left- A  Right- D", True, (255,255,255))
                        axis3Text = font.render("Arm 2  - Left- Q  Right- E", True, (255,255,255))
                        axis4Text = font.render("Pan    - Left- J  Right- L", True, (255,255,255))
                        axis5Text = font.render("Tilt   - Up  - I  Down - K", True, (255,255,255))
                        display.blit(axis1Text,(150 - axis1Text.get_width() // 2, 50 - axis1Text.get_height() // 2))
                        display.blit(axis2Text,(150 - axis1Text.get_width() // 2, 100 - axis1Text.get_height() // 2))
                        display.blit(axis3Text,(150 - axis1Text.get_width() // 2, 150 - axis1Text.get_height() // 2))
                        display.blit(axis4Text,(150 - axis1Text.get_width() // 2, 200 - axis1Text.get_height() // 2))
                        display.blit(axis5Text,(150 - axis1Text.get_width() // 2, 250 - axis1Text.get_height() // 2))
                        pygame.display.update()
                        while True:
                                if pygame.event.get(pygame.QUIT): break
                                pygame.event.clear()
                                pygame.event.get()

                                keys = pygame.key.get_pressed()
                                if keys[pygame.K_w]: motor1.continuous_rotate(True) #Motor1 - Up
                                if keys[pygame.K_s]: motor1.continuous_rotate(False) #Motor1 - Down
                                if keys[pygame.K_a]: motor2.continuous_rotate(False) #Motor2 - Left
                                if keys[pygame.K_d]: motor2.continuous_rotate(True)     #Motor2 - Right
                                if keys[pygame.K_q]: motor3.continuous_rotate(False) #Motor3 - Left
                                if keys[pygame.K_e]: motor3.continuous_rotate(True) #Motor3 - Right
                                if keys[pygame.K_j]: servo1.set_angle_easing(servo1.feedbackAngle + 5, 0.5) #Servo1 - Left
                                if keys[pygame.K_l]: servo1.set_angle_easing(servo1.feedbackAngle - 5, 0.5) #Servo1 - Right
                                if keys[pygame.K_i]: servo2.set_angle_easing(servo2.feedbackAngle - 5, 0.5) #Servo2 - Left
                                if keys[pygame.K_k]: servo2.set_angle_easing(servo2.feedbackAngle + 5, 0.5) #Servo2 - Right
                                sleep(0.0001)
                case '2':
                        GPIO.output(motorsEnablePin, True)
                        print('TCP Teleop')
                        pygame.init()
                        pygame.key.set_repeat(1)
                        display = pygame.display.set_mode((300,300))
                        font = pygame.font.SysFont("Arial", 20)
                        axis1Text = font.render("X    - +ve - D  -ve  - A", True, (255,255,255))
                        axis2Text = font.render("Y    - +ve - W  -ve  - S", True, (255,255,255))
                        axis3Text = font.render("Z    - +ve - Q  -ve  - E", True, (255,255,255))
                        axis4Text = font.render("Pan  - Left- J  Right- L", True, (255,255,255))
                        axis5Text = font.render("Tilt - Up  - I  Down - K", True, (255,255,255))
                        display.blit(axis1Text,(150 - axis1Text.get_width() // 2, 50 - axis1Text.get_height() // 2))
                        display.blit(axis2Text,(150 - axis1Text.get_width() // 2, 100 - axis1Text.get_height() // 2))
                        display.blit(axis3Text,(150 - axis1Text.get_width() // 2, 150 - axis1Text.get_height() // 2))
                        display.blit(axis4Text,(150 - axis1Text.get_width() // 2, 200 - axis1Text.get_height() // 2))
                        display.blit(axis5Text,(150 - axis1Text.get_width() // 2, 250 - axis1Text.get_height() // 2))
                        pygame.display.update()
                        while True:
                                if pygame.event.get(pygame.QUIT): break
                                pygame.event.clear()
                                pygame.event.get()

                                keys = pygame.key.get_pressed()
                                if keys[pygame.K_w]: moveRelativePosition(0,0.5) #y +ve
                                if keys[pygame.K_s]: moveRelativePosition(0,-0.5) #y -ve
                                if keys[pygame.K_a]: moveRelativePosition(-0.5,0) #x +ve
                                if keys[pygame.K_d]: moveRelativePosition(0.5,0) #x -ve
                                if keys[pygame.K_q]: motor1.continuous_rotate(True) #Motor1 - Up
                                if keys[pygame.K_e]: motor1.continuous_rotate(False) #Motor1 - Down
                                if keys[pygame.K_j]: servo1.set_angle_easing(servo1.feedbackAngle + 5, 1) #Servo1 - Left
                                if keys[pygame.K_l]: servo1.set_angle_easing(servo1.feedbackAngle - 5, 1) #Servo1 - Right
                                if keys[pygame.K_i]: servo2.set_angle_easing(servo2.feedbackAngle - 5, 1) #Servo2 - Left
                                if keys[pygame.K_k]: servo2.set_angle_easing(servo2.feedbackAngle + 5, 1) #Servo2 - Right

                case '3':
                        GPIO.output(motorsEnablePin, True)
                        print('Go to')
                        x, y, z = input("Enter x, y and z values (mm): ").split()
                        print(x, y, z)
                        moveToPosition(int(x),int(y),int(z))

        servo1.close()
        servo2.close()
        GPIO.output(motorsEnablePin, False)
        motor1.motor_stop()
        motor2.motor_stop()
        motor3.motor_stop()
        GPIO.cleanup()

if __name__ == "__main__":
        try:
                main()
        except KeyboardInterrupt:
                servo1.close()
                servo2.close()
                GPIO.output(motorsEnablePin, False)
                motor1.motor_stop()
                motor2.motor_stop()
                motor3.motor_stop()
                GPIO.cleanup()
