import RPi.GPIO as gpio
from time import time, sleep
from controlador import controler
import numpy as np
import sys

identificacao = True
A = 0.5

if len(sys.argv) > 1:
    identificacao = False
    A = sys.argv[1]

# Pinos
pin_out = 12
gpio_TRIGGER = 32
gpio_ECHO = 36

frequency = 60
start_dc = 10
target = 30.0


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

0.809
0.901
0.969


control = controler(A)
fan = gpio.PWM(pin_out, frequency)
fan.start(start_dc)

if identificacao:
    print("Identificação")
    min_erro = 10000000
    A_min = 0
    for i in range(0, 50):
        A = 2 * i / (50 + i)
        control = controler(A)
        erros = []
        print(f'A={A}')
        try:
            for k in range(200):
                value = distance()
                update = control.controlador(value, target)
                fan.ChangeDutyCycle(update)
                erros.append(target - value)
                sleep(2 / frequency)

            if np.abs(min_erro) > np.abs(np.mean(erros[100:])):
                A_min = A
                min_erro = np.mean(erros[100:])
                print(f"Novo menor erro: {min_erro:.03f} com A = {A_min:0.03f}")
                if np.abs(min_erro) < 0.01:
                    break

            fan.ChangeDutyCycle(start_dc)
            sleep(1)
        except Exception as e:
            print('interrompido')
    print(f"A_min: {A_min:.03f} erro: {min_erro:.02f}")
    A = A_min
    _ = input(f"Sistema identificado com A = {A:.04f}")


control = controler(A)
try:
    while True:
        value = distance()
        update = control.controlador(value, target)
        print(f"distancia: {value:0.2f}cm e pid: {update}")
        fan.ChangeDutyCycle(max(min(update, 100), 0))
        sleep(2 / frequency)
except:
    gpio.cleanup()
