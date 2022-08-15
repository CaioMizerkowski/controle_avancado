import RPi.GPIO as gpio
from time import time, sleep

pin_out = 12
frequency = 50
start_dc = 10
target = 30.0
gpio_TRIGGER = 32
gpio_ECHO = 36

p_gain = 0.2
i_gain = 0.05
d_gain = 0.1

gpio.setmode(gpio.BOARD)
gpio.setup(gpio_TRIGGER, gpio.OUT)
gpio.setup(gpio_ECHO, gpio.IN)
gpio.setup(pin_out, gpio.OUT)

def distance():
    # set Trigger to HIGH
    gpio.output(gpio_TRIGGER, True)
    # set Trigger after 0.01ms to LOW
    sleep(0.00001)
    gpio.output(gpio_TRIGGER, False)
    StartTime = time()
    StopTime = time()
    # save StartTime
    while gpio.input(gpio_ECHO) == 0:
        StartTime = time()
    # save time of arrival
    while gpio.input(gpio_ECHO) == 1:
        StopTime = time()
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    return distance

class pid():
    def __init__(self, p_gain, i_gain, d_gain):
        self.last_error = 0.0
        self.last_time = time()

        self.p_gain = p_gain
        self.i_gain = i_gain
        self.d_gain = d_gain

        self.i_error = 0.0

    def compute(self, value, target):
        dt = (time() - self.last_time)

        error = -(target - value)

        p_error = error

        self.i_error += (error + self.last_error) * dt
        i_error = self.i_error

        d_error = (error - self.last_error) / dt

        p_output = self.p_gain * p_error
        i_output = self.i_gain * i_error
        d_output = self.d_gain * d_error

        self.last_error = error
        self.last_time = time()
        return sum([p_output, i_output, d_output])

fan_pid = pid(p_gain, i_gain, d_gain)
fan = gpio.PWM(pin_out, frequency)
fan.start(start_dc)

while True:
    value = distance()
    update = fan_pid.compute(value, target)
    print(f'distancia: {value:0.2f}cm e pid: {update}')
    update = max(min(update,100),0)
    fan.ChangeDutyCycle(update)
    sleep(2/frequency)
