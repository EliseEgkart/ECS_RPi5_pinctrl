# 임베디드 통신시스템 프로젝트 - gpiozero 기반 counter8

이 프로젝트는 Raspberry Pi 5와 Python의 `gpiozero` 라이브러리를 활용하여 GPIO를 제어하는 것을 목표로 합니다.  
본 문서에서는 전체 코드의 로직, 하드웨어 연결 구성에 대해 기술합니다.  
특히 `counter8`은 LED를 활용하여 0부터 7까지의 3비트 이진수를 시각적으로 표현하는 프로젝트입니다.

---

## 시연 영상

실제 작동하는 모습을 아래 영상을 통해 확인할 수 있습니다:

[![시연 영상 바로가기](http://img.youtube.com/vi/h-crQeahjCs/0.jpg)](https://youtu.be/z2csX5kX4zo)

### 핀맵과 GPIO에 대한 추가 설명입니다.
[![시연 영상 바로가기](http://img.youtube.com/vi/bRw7eX6XiOk/0.jpg)](https://youtu.be/bRw7eX6XiOk)

---

## 동작 원리 상세 설명

- **1초 간격 카운트:**  
  메인 루프에서 0부터 7까지의 숫자를 순차적으로 출력하며,  
  각 숫자는 1초 동안 유지되고, 연결된 LED들은 해당 이진수의 각 비트에 맞춰 점등됩니다.

- **비트에 따른 LED 제어:**  
  - GPIO 5: LSB (최하위 비트)  
  - GPIO 6: 중간 비트  
  - GPIO 13: MSB (최상위 비트)

- **변환 과정:**  
  Python 코드의 `set_pin_states()` 함수는 전달된 숫자 값을 이진수로 변환하여  
  각 비트를 해당 GPIO 핀에 매핑합니다.  
  예: 숫자 5 → 이진수 `101` → GPIO 5: ON, GPIO 6: OFF, GPIO 13: ON

- **종료 처리:**  
  `SIGINT` 또는 `SIGTERM` 시그널이 감지되면 `cleanup()` 함수가 호출되어  
  모든 LED를 안전하게 소등하고 프로그램을 종료합니다.

---

## 하드웨어 구성 설명

### 실제 구성 이미지
![실제 하드웨어 구성 이미지](../image/ECS_count8_domino4_real.png.jpg)

### 하드웨어 구성 도식화
![하드웨어 구성 도식화](../image/ECS_count8_domino4.png)

### Raspberry Pi5 pinmap
![라즈베리파이5 핀맵](../image/RaspberryPi5pin_map.png)

### GPIO 핀 연결 표

| 핀 번호 (BCM) | 연결된 부품 | 설명                    |
|---------------|------------|-------------------------|
| GPIO 5        | LED 1      | 최하위 비트 (LSB)       |
| GPIO 6        | LED 2      | 중간 비트               |
| GPIO 13       | LED 3      | 최상위 비트 (MSB)       |

> **핵심:**  
> 이 구성은 3개의 핀으로 0부터 7까지의 3비트 이진수 값을 출력하는 데 사용됩니다.  
> 각 LED는 대응하는 비트의 상태에 따라 켜지거나 꺼지며, 이를 통해 디지털 카운터의 역할을 수행합니다.

---

## 코드 설명 및 로직

다음은 Python `gpiozero` 기반의 전체 코드입니다:

```python
#!/usr/bin/env python3
# 이 스크립트는 Python 3 인터프리터를 사용하여 실행됨을 명시합니다.
# /usr/bin/env를 사용하는 이유는 사용자의 PATH 환경변수에서 python3의 위치를 자동으로 탐색하게 하기 위함입니다.

from gpiozero import LED
# gpiozero는 Raspberry Pi의 GPIO 핀을 간편하게 제어하기 위한 고수준 라이브러리입니다.
# 여기서 LED는 출력 핀 제어를 위한 클래스이며, 실제 LED뿐 아니라 논리적으로 HIGH/LOW를 전환하는 데에도 사용됩니다.

from signal import signal, SIGINT, SIGTERM
# signal 모듈은 운영체제에서 보내는 시그널(종료 요청 등)을 감지하고 처리할 수 있도록 도와줍니다.
# SIGINT: 사용자가 Ctrl+C를 눌렀을 때 발생하는 인터럽트 시그널
# SIGTERM: 시스템에서 프로세스를 정상 종료시키기 위해 보내는 시그널

from time import sleep
# sleep(seconds)는 지정된 시간(초) 동안 실행을 일시 중지합니다.
# 여기서는 각 상태 변경 간의 지연(=LED 변화 관찰을 위한 대기 시간)으로 사용됩니다.

import sys
# sys 모듈은 인터프리터와 관련된 기능을 제공합니다. 여기서는 `sys.exit()`를 사용하여 프로그램을 종료합니다.

# ------------------------
# 1. GPIO 핀 설정
# ------------------------

# 사용할 GPIO 핀 번호를 리스트로 정의합니다.
# 번호는 BCM 번호 체계에 따르며, 물리 핀 번호와는 다릅니다.
# 순서대로 LSB, 중간 비트, MSB를 나타내도록 배열합니다.
gpio_pins = [5, 6, 13]

# 각 핀 번호에 대해 LED 객체를 생성합니다.
# 각 LED 객체는 해당 GPIO 핀을 제어할 수 있게 해주는 핸들입니다.
# 예: LED(5)는 BCM 5번 핀에 연결된 출력을 제어합니다.
leds = [LED(pin) for pin in gpio_pins]

# ------------------------
# 2. 종료 처리 함수
# ------------------------

def cleanup(signum, frame):
    """
    프로그램 종료 시 모든 핀을 LOW(=LED 끄기)로 설정하여 안전하게 종료하는 함수입니다.
    이 함수는 시그널 핸들러에 의해 자동으로 호출됩니다.
    
    Parameters:
        signum: 시그널 번호 (예: SIGINT)
        frame: 현재 실행 중인 스택 프레임 (디버깅 목적)
    """
    print("\n종료 중: GPIO 핀 LOW로 초기화 중...")
    for led in leds:
        led.off()  # 해당 핀을 LOW로 설정 (LED OFF)
    sys.exit(0)   # 프로그램 정상 종료

# ------------------------
# 3. 시그널 핸들링 등록
# ------------------------

# Ctrl+C 또는 시스템 종료 요청이 발생하면 cleanup() 함수를 실행하도록 설정합니다.
signal(SIGINT, cleanup)   # 사용자 인터럽트 (Ctrl+C)
signal(SIGTERM, cleanup)  # 시스템 종료 요청 (kill 명령 등)

# ------------------------
# 4. 비트값에 따른 핀 상태 설정 함수
# ------------------------

def set_pin_states(value):
    """
    0~7 사이의 값을 받아서 이진수로 해석하고,
    각 비트를 GPIO 핀에 대응시켜 LED를 ON/OFF 합니다.

    예:
        value = 5 (이진수 101)
        → LSB(5번 핀) = ON, 중간(6번 핀) = OFF, MSB(13번 핀) = ON
    """
    for i, led in enumerate(leds):
        # i번째 LED를 제어 (i는 0부터 시작)
        # value >> i: 해당 비트를 LSB로 옮기기 (오른쪽 시프트)
        # & 1: 최하위 비트만 추출하여 0 또는 1을 얻음
        if (value >> i) & 1:
            led.on()   # 비트가 1이면 LED ON
        else:
            led.off()  # 비트가 0이면 LED OFF

# ------------------------
# 5. 메인 루프 (3비트 카운터)
# ------------------------

try:
    # 무한 루프: 프로그램이 수동으로 종료되기 전까지 계속 실행
    while True:
        # 0부터 7까지 반복하며 각 숫자를 이진수로 표현
        for i in range(8):
            set_pin_states(i)  # 현재 숫자의 각 비트를 LED에 반영
            sleep(1)           # 1초 동안 해당 상태 유지

except KeyboardInterrupt:
    # 사용자가 Ctrl+C를 누르면 여기로 이동하여 cleanup()을 실행
    cleanup(None, None)

```

---

## 라이선스

이 프로젝트는 [MIT License](../LICENSE) 하에 오픈소스로 공개됩니다.
