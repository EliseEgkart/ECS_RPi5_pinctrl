# 임베디드 통신시스템 프로젝트 - gpiozero 기반 4비트 이진 카운터 출력

이 프로젝트는 Raspberry Pi 5와 Python의 `gpiozero` 라이브러리를 활용하여  
**단일 버튼 입력으로 4개의 LED에 이진 카운터 값을 출력**하는 시스템을 구현합니다.  
버튼이 눌릴 때마다 내부 카운터가 0~15 범위에서 1씩 증가하며,  
그 값을 4개의 LED에 **LSB → MSB** 순으로 이진 출력합니다.

---

## 시연 영상

버튼을 누를 때마다 LED 패턴이 이진수 형태로 증가하는 모습을 확인할 수 있습니다:

[![시연 영상 바로가기](http://img.youtube.com/vi/z2csX5kX4zo/0.jpg)](https://youtu.be/z2csX5kX4zo)

---

## 동작 원리 상세 설명

- **버튼 상승 엣지 감지:**  
  `gpiozero.Button`의 상태 변화를 이용해 **LOW → HIGH** 시점(=버튼 눌림)만 인식합니다.

- **4비트 이진 출력:**  
  내부 카운터 값(`0~15`)을 각 비트로 분해하여 LED(GPIO 8, 7, 16, 20)에 출력합니다.  
  - `GPIO 8`: LSB (1의 자리)  
  - `GPIO 20`: MSB (8의 자리)

- **디바운싱 처리:**  
  버튼 튐 현상 방지를 위해 50ms 간격의 polling 구조로 안정된 입력을 처리합니다.

- **안전 종료 처리:**  
  `SIGINT`(Ctrl+C), `SIGTERM` 시 발생 시, 모든 LED를 끄고 종료합니다.

---

## 하드웨어 구성 설명

### GPIO 핀 연결 표

| 핀 번호 (BCM) | 연결된 부품 | 설명                         |
|---------------|--------------|------------------------------|
| GPIO 25       | 버튼         | 입력 신호 감지, 풀업 구성      |
| GPIO 8        | LED 0        | LSB (2⁰ 자리)                |
| GPIO 7        | LED 1        | 2ⁱ 자리                      |
| GPIO 16       | LED 2        | 2² 자리                      |
| GPIO 20       | LED 3        | MSB (2³ 자리)                |

> **핵심:**  
> 이 구성은 버튼을 누를 때마다 내부 카운터를 증가시키고,  
> 그 값을 **4비트 이진수로 LED에 시각적으로 출력**합니다.

---

## 코드 설명 및 로직

아래 코드는 Python의 `gpiozero` 라이브러리를 활용하여  
버튼 입력을 감지하고 4개의 GPIO 핀을 이진수 형태로 제어합니다.

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
```
---

## 라이선스
이 프로젝트는 [MIT License](../LICENSE) 하에 오픈소스로 공개됩니다.