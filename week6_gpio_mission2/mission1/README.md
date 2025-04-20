# 임베디드 통신시스템 프로젝트 - gpiozero 기반 Button-LED 제어

이 프로젝트는 Raspberry Pi 5와 Python의 `gpiozero` 라이브러리를 활용하여 GPIO를 제어하는 것을 목표로 합니다.  
특히 이 프로젝트는 **버튼을 누르면 LED가 켜지고, 떼면 꺼지는 기본 I/O 반응형 제어**를 구현합니다.  
시그널 처리 및 디바운싱까지 고려된 구조로, GPIO 제어의 기초를 실습하기에 적합한 프로젝트입니다.

---

## 시연 영상

아래 영상에서는 버튼을 누를 때마다 LED가 켜지고, 떼면 꺼지는 동작을 확인할 수 있습니다:

[![시연 영상 바로가기](http://img.youtube.com/vi/1306bdldeCU/0.jpg)](https://youtube.com/shorts/1306bdldeCU)

---

## 동작 원리 상세 설명

- **버튼 입력 감지:**  
  GPIO 25번 핀은 내부 풀업(pull_up=True)이 활성화된 버튼 입력용으로 설정되어 있습니다.  
  버튼이 눌리면 LOW 신호가 들어오고, 이를 통해 입력을 감지합니다.

- **LED 제어:**  
  GPIO 20번 핀은 LED 출력용 핀으로 설정되어 있습니다.  
  버튼이 눌리면 LED를 ON, 버튼을 떼면 OFF 되도록 제어합니다.

- **디바운싱 처리:**  
  입력 신호의 튐을 방지하기 위해 50ms 간격의 polling을 적용했습니다.

- **안전 종료:**  
  `SIGINT`, `SIGTERM` 등의 시그널이 발생하면 LED를 소등하고 안전하게 종료합니다.

---

## 하드웨어 구성 설명
### GPIO 핀 연결 표

| 핀 번호 (BCM) | 연결된 부품 | 설명                        |
|---------------|--------------|-----------------------------|
| GPIO 25       | 버튼         | 입력 신호 감지, 풀업 구성     |
| GPIO 20       | LED          | 출력 제어용 핀               |

> **핵심:**  
> 이 프로젝트는 GPIO 입력을 통해 실시간 출력 제어를 수행하며, 시스템 이벤트 발생 시 GPIO 정리를 자동 수행합니다.

---

## 코드 설명 및 로직

아래 코드는 Python의 `gpiozero` 라이브러리를 사용하여  
버튼 입력(GPIO 25)에 따라 LED(GPIO 20)를 ON/OFF 하는 기능을 구현합니다.

```python
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
```
---

## 라이선스
이 프로젝트는 [MIT License](../LICENSE) 하에 오픈소스로 공개됩니다.