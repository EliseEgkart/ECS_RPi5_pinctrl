#!/usr/bin/env python3
# 시스템 PATH에서 python3 인터프리터를 탐색하여 실행합니다.
# 다양한 플랫폼에서 호환성을 보장하기 위한 권장 방식입니다.

from gpiozero import LED, Button
# gpiozero는 Raspberry Pi 전용 고수준 GPIO 제어 라이브러리입니다.
# Button: 입력 핀(스위치) 제어용 클래스
# LED: 출력 핀 제어용 클래스

from signal import signal, SIGINT, SIGTERM
# signal 모듈은 시스템 종료, Ctrl+C 같은 시그널을 감지하여 사용자 정의 함수를 실행할 수 있도록 합니다.

from time import sleep
# sleep 함수는 프로그램 실행을 지정된 시간(초)만큼 지연시킵니다.

import sys
# sys.exit()를 사용하여 프로그램을 명시적으로 종료합니다.

# ----------------------------------------------------------
# 1. GPIO 핀 설정 (BCM 기준)
# ----------------------------------------------------------
SWPIN = 25                    # 스위치 입력 핀
LEDPINS = [8, 7, 16, 20]      # 출력 LED 핀 리스트 (LSB → MSB)

# ----------------------------------------------------------
# 2. 객체 생성
# ----------------------------------------------------------
try:
    button = Button(SWPIN, pull_up=True)
    leds = [LED(pin) for pin in LEDPINS]
except Exception as e:
    print(f"[ERROR] GPIO initialization failed: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# 3. 안전 종료 처리 함수 정의
# ----------------------------------------------------------
def cleanup(signum, frame):
    """
    프로그램 종료 시 모든 LED를 소등하고 안전하게 종료합니다.
    회로 보호 및 GPIO 상태 초기화를 위해 필수입니다.
    """
    print("\nShutting down: Releasing GPIO resources...")
    for led in leds:
        led.off()
    sys.exit(0)

# ----------------------------------------------------------
# 4. 시그널 핸들러 등록 (Ctrl+C 또는 종료 요청 대응)
# ----------------------------------------------------------
signal(SIGINT, cleanup)
signal(SIGTERM, cleanup)

# ----------------------------------------------------------
# 5. GPIO 비트 출력 함수
# ----------------------------------------------------------
def set_gpio_bits(value):
    """
    전달받은 정수값을 이진수로 해석하여 각 비트를 LED에 출력합니다.
    1 → ON, 0 → OFF
    """
    for i, led in enumerate(leds):
        if (value >> i) & 1:
            led.on()
        else:
            led.off()

# ----------------------------------------------------------
# 6. 메인 루프: 버튼 누를 때마다 카운터 증가 및 출력
# ----------------------------------------------------------
try:
    counter = 0
    prev_state = False

    while True:
        curr_state = button.is_pressed

        if curr_state and not prev_state:
            counter = (counter + 1) % 16  # 0~15 사이에서 반복
            set_gpio_bits(counter)
            print(f"counter: {counter}")

        prev_state = curr_state
        sleep(0.05)  # 디바운싱 대기 시간

except KeyboardInterrupt:
    cleanup(None, None)
