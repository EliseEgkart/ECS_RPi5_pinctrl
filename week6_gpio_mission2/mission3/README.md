# 임베디드 통신시스템 프로젝트 - gpiozero 기반 순차 점멸 LED 제어

이 프로젝트는 Raspberry Pi 5와 Python의 `gpiozero` 라이브러리를 활용하여 GPIO를 제어하는 것을 목표로 합니다. 특히 이 프로젝트는 **버튼을 누르면 4개의 LED가 순차적으로 켜졌다가 꺼지는 도미노 스타일의 동작**을 구현합니다.  
입력 엣지 트리거 처리, 다중 출력 핀 제어, 시그널 기반 종료 등 다양한 GPIO 제어 요소가 포함되어 있습니다.

---

## 시연 영상

아래 영상에서는 버튼을 누를 때마다 LED가 1초 간격으로 순차 점등/소등되는 동작을 확인할 수 있습니다:

[![시연 영상 바로가기](http://img.youtube.com/vi/sItclSGZrT4/0.jpg)](https://youtube.com/shorts/sItclSGZrT4)

---

## 동작 원리 상세 설명

- **버튼 상승 엣지 감지:**  
  GPIO 25번 핀의 상태 변화를 이용하여 **LOW → HIGH 전환(버튼 눌림 시작)** 시점을 감지합니다.

- **LED 순차 점멸:**  
  4개의 LED(GPIO 8, 7, 16, 20)가 순서대로 켜지고 1초 후 꺼지는 방식으로 동작합니다.  
  도미노처럼 이어지는 시각적 효과를 구현합니다.

- **디바운싱 처리:**  
  잘못된 엣지 감지를 방지하기 위해 50ms polling 방식의 디바운싱 로직을 적용했습니다.

- **안전 종료 처리:**  
  `Ctrl+C` 또는 시스템 종료 요청(SIGINT, SIGTERM) 시, 모든 LED를 OFF시키고 프로그램을 정상 종료합니다.

---

## 하드웨어 구성 설명

### GPIO 핀 연결 표

| 핀 번호 (BCM) | 연결된 부품 | 설명                        |
|---------------|--------------|-----------------------------|
| GPIO 25       | 버튼         | 입력 신호 감지, 풀업 구성     |
| GPIO 8        | LED 1        | 첫 번째 순차 점등 LED         |
| GPIO 7        | LED 2        | 두 번째 순차 점등 LED         |
| GPIO 16       | LED 3        | 세 번째 순차 점등 LED         |
| GPIO 20       | LED 4        | 네 번째 순차 점등 LED         |

> **핵심:**  
> 이 구성은 단일 버튼 입력을 이용하여 **4개의 LED를 순차적으로 점멸**시키는 도미노 동작을 구현합니다.

---

## 코드 설명 및 로직

아래 코드는 Python의 `gpiozero` 라이브러리를 사용하여  
버튼 입력의 상승 엣지를 감지하고, 등록된 4개의 LED를 순차적으로 1초 간격으로 ON/OFF 시키는 기능을 구현합니다.

```python
#!/usr/bin/env python3
# 시스템 PATH에서 python3 인터프리터를 탐색하여 실행합니다.
# 다양한 플랫폼에서 호환성을 보장하기 위한 권장 방식입니다.

from gpiozero import LED, Button
# gpiozero는 Raspberry Pi 전용 고수준 GPIO 제어 라이브러리입니다.
# Button: 입력 핀(스위치) 제어용 클래스
# LED: 출력 핀 제어용 클래스

from signal import signal, SIGINT, SIGTERM
# signal 모듈은 시스템 종료, Ctrl+C 같은 시그널을 감지하여 사용자 정의 함수를 실행할 수 있도록 합니다.
# SIGINT: 키보드 인터럽트 (Ctrl+C), SIGTERM: 시스템 종료 요청 (예: kill 명령)

from time import sleep
# sleep 함수는 프로그램 실행을 지정된 시간(초)만큼 지연시킵니다.

import sys
# sys.exit()를 사용하여 프로그램을 명시적으로 종료합니다.

# ----------------------------------------------------------
# 1. GPIO 핀 번호 설정 (BCM 기준)
# ----------------------------------------------------------
SWPIN = 25                  # 스위치 입력 핀
LEDPINS = [8, 7, 16, 20]    # 출력 LED 핀 목록

# ----------------------------------------------------------
# 2. Button 및 LED 객체 생성
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
# 5. 메인 루프: 버튼 상승 엣지 감지 시 LED 순차 점멸
# ----------------------------------------------------------
try:
    prev_state = False  # 버튼 이전 상태 저장

    while True:
        curr_state = button.is_pressed

        # 상승 엣지 감지 (버튼 눌림 시작 시점)
        if curr_state and not prev_state:
            for led in leds:
                led.on()
                sleep(1)
                led.off()

        prev_state = curr_state
        sleep(0.05)  # 디바운싱을 위한 지연 시간

except KeyboardInterrupt:
    cleanup(None, None)
```
---

## 라이선스
이 프로젝트는 [MIT License](../LICENSE) 하에 오픈소스로 공개됩니다.