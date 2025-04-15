#!/usr/bin/env python3
from gpiozero import LED
from signal import signal, SIGINT, SIGTERM
from time import sleep
import sys

# BCM 기준 GPIO 핀 번호 리스트
gpio_pins = [5, 6, 13, 19]

# 각 핀에 대응하는 LED 객체 리스트 생성
leds = [LED(pin) for pin in gpio_pins]

# 종료 시 모든 핀을 LOW로 설정
def cleanup(signum, frame):
    print("\n종료 중: GPIO 핀 LOW로 초기화 중...")
    for led in leds:
        led.off()
    sys.exit(0)

# SIGINT(Ctrl+C) 및 SIGTERM 수신 시 cleanup 실행
signal(SIGINT, cleanup)
signal(SIGTERM, cleanup)

# 핀들을 순차적으로 ON/OFF하는 함수
def toggle_sequence():
    for led in leds:
        led.on()
        sleep(1)
        led.off()

# 무한 루프 실행
try:
    while True:
        toggle_sequence()
except KeyboardInterrupt:
    cleanup(None, None)