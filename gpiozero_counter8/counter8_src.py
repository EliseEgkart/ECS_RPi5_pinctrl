#!/usr/bin/env python3
from gpiozero import LED
from signal import signal, SIGINT, SIGTERM
from time import sleep
import sys

# GPIO 핀 번호 설정 (BCM 기준)
gpio_pins = [5, 6, 13]  # BCM 번호 기준으로 작성

# LED 객체 생성
leds = [LED(pin) for pin in gpio_pins]

# 종료 시 모든 핀 LOW
def cleanup(signum, frame):
    print("\n종료 중: GPIO 핀 LOW로 초기화 중...")
    for led in leds:
        led.off()
    sys.exit(0)

# 시그널 핸들링 등록
signal(SIGINT, cleanup)
signal(SIGTERM, cleanup)

# 3비트 값을 핀 상태로 설정
def set_pin_states(value):
    for i, led in enumerate(leds):
        if (value >> i) & 1:
            led.on()
        else:
            led.off()

# 메인 루프
try:
    while True:
        for i in range(8):
            set_pin_states(i)
            sleep(1)
except KeyboardInterrupt:
    cleanup(None, None)