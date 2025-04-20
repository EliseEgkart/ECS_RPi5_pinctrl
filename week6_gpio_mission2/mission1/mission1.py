#!/usr/bin/env python3
# 시스템 PATH에서 python3 인터프리터를 탐색하여 실행합니다.
# 다양한 플랫폼에서 호환성을 보장하기 위한 권장 방식입니다.

from gpiozero import Button, LED
# gpiozero는 Raspberry Pi 전용 고수준 GPIO 제어 라이브러리입니다.
# Button: 입력 핀(스위치) 제어용 클래스
# LED: 출력 핀(LED) 제어용 클래스

from signal import signal, SIGINT, SIGTERM
# signal 모듈은 시스템 종료, Ctrl+C 같은 시그널을 감지하여 사용자 정의 함수를 실행할 수 있도록 합니다.
# SIGINT: 키보드 인터럽트 (Ctrl+C), SIGTERM: 시스템 종료 요청 (예: kill 명령)

from time import sleep
# sleep 함수는 프로그램 실행을 지정된 시간(초)만큼 지연시킵니다.

import sys
# sys.exit()를 사용하여 프로그램을 명시적으로 종료합니다.

# ----------------------------------------------------------
# 1. GPIO 핀 번호 설정 (BCM 번호 기준)
# ----------------------------------------------------------
SWPIN = 25    # 스위치 입력 핀
LEDPIN = 20   # LED 출력 핀

# ----------------------------------------------------------
# 2. Button 및 LED 객체 생성
# ----------------------------------------------------------
try:
    button = Button(SWPIN, pull_up=True)
    led = LED(LEDPIN)
except Exception as e:
    print(f"[ERROR] GPIO initialization failed: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# 3. 안전 종료 처리 함수 정의
# ----------------------------------------------------------
def cleanup(signum, frame):
    """
    프로그램 종료 시 LED를 소등하고 안전하게 종료합니다.
    회로 보호 및 GPIO 상태 초기화를 위해 필수입니다.
    """
    print("\nShutting down: Turning off LED and releasing resources...")
    led.off()
    sys.exit(0)

# ----------------------------------------------------------
# 4. 시그널 핸들러 등록 (Ctrl+C 또는 종료 요청 대응)
# ----------------------------------------------------------
signal(SIGINT, cleanup)
signal(SIGTERM, cleanup)

# ----------------------------------------------------------
# 5. 메인 루프: 버튼 입력에 따른 LED 제어
# ----------------------------------------------------------
try:
    while True:
        if button.is_pressed:
            led.on()
        else:
            led.off()
        sleep(0.05)  # 디바운싱 간격 (50ms)

except KeyboardInterrupt:
    cleanup(None, None)
