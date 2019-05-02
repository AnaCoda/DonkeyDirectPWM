left_val = 63
right_val = 83

max_throttle_pulse = 77
min_throttle_pulse = 65
no_throttle_pulse = 73

import time
import wiringpi
import math


def fscale(originalMin, originalMax, newBegin, newEnd, inputValue, curve):

    OriginalRange = 0
    NewRange = 0
    zeroRefCurVal = 0
    normalizedCurVal = 0
    rangedValue = 0
    invFlag = 0

    if (curve > 10):
        curve = 10
    if (curve < -10):
        curve = -10

    curve = (curve * -.1)
    curve = pow(10, curve)

    if (inputValue < originalMin):
        inputValue = originalMin
    if (inputValue > originalMax):
        inputValue = originalMax

    OriginalRange = originalMax - originalMin

    if (newEnd > newBegin):
        NewRange = newEnd - newBegin
    else:
        NewRange = newBegin - newEnd 
        invFlag = 1

    zeroRefCurVal = inputValue - originalMin
    normalizedCurVal  =  zeroRefCurVal / OriginalRange

    if (originalMin > originalMax ):
        return 0

    if (invFlag == 0):
        rangedValue =  (pow(normalizedCurVal, curve) * NewRange) + newBegin
    else:   
        rangedValue =  newBegin - (pow(normalizedCurVal, curve) * NewRange); 
    return rangedValue

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

class piDirectPWM:
    """
    PWM motor controller
    """
    def __init__(self, channel, frequency=60):
        wiringpi.wiringPiSetupGpio()
        self.channel = channel
        wiringpi.pinMode(channel, 2)
        #wiringpi.pinMode(pin, wiringpi.GPIO.PWM_OUTPUT)
        wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS) #put PWM in mark-space mode, required to set frequency
        wiringpi.pwmSetClock(400) #pwmFrequency in Hz = 19.2e6 Hz / pwmSetClock / pwmSetRange.
        wiringpi.pwmSetRange(800) # TOP value for PWM counter

    def set_pulse(self, pulse):
        wiringpi.pwmWrite(self.channel, int(round(pulse)))

    def run(self, pulse):
        self.set_pulse(pulse)


class PWMSteering:
    """
    Wrapper over a PWM motor cotnroller to convert angles to PWM pulses.
    """
    LEFT_ANGLE = -1
    RIGHT_ANGLE = 1

    class Settings:
        inputs = ['angle']
        left_pulse = left_val
        right_pulse = right_val

    def __init__(self, controller=None,
                 left_pulse=left_val, right_pulse=right_val):

        self.controller = controller
        self.left_pulse = left_pulse
        self.right_pulse = right_pulse

    def run(self, angle):
        # map absolute angle to angle that vehicle can implement.
        pulse = translate(
            angle,
            self.LEFT_ANGLE, self.RIGHT_ANGLE,
            self.left_pulse, self.right_pulse
        )

        self.controller.set_pulse(pulse)

    def shutdown(self):
        self.run(0)  # set steering straight


class PWMThrottle:
    """
    Wrapper over a PWM motor cotnroller to convert -1 to 1 throttle
    values to PWM pulses.
    """
    MIN_THROTTLE = -1
    MAX_THROTTLE =  1

    def __init__(self, controller=None,
                       max_pulse=max_throttle_pulse,
                       min_pulse=min_throttle_pulse,
                       zero_pulse=no_throttle_pulse):

        self.controller = controller
        self.max_pulse = max_pulse
        self.min_pulse = min_pulse
        self.zero_pulse = zero_pulse

        # send zero pulse to calibrate ESC
        self.controller.set_pulse(self.zero_pulse)
        time.sleep(1)

    def run(self, throttle):
        pulse = translate(throttle, self.MIN_THROTTLE, self.MAX_THROTTLE, 0, 200)
        if(pulse > 120):
            pulse = fscale(100, 200, no_throttle_pulse, max_throttle_pulse, pulse, 4)  
        elif(pulse < 80):
            pulse = fscale(0, 100, no_throttle_pulse, min_throttle_pulse, pulse, 6)
        else:
            pulse = translate(pulse, 0, 200, min_throttle_pulse, max_throttle_pulse)
        self.controller.set_pulse(pulse)
        return pulse
    def shutdown(self):
        self.run(0) #stop vehicle
