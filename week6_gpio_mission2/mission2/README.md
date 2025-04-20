# 임베디드 통신시스템 프로젝트 - gpiozero 기반 Edge-triggered Button-LED 제어

이 프로젝트는 Raspberry Pi 5와 Python의 `gpiozero` 라이브러리를 활용하여 GPIO를 제어하는 것을 목표로 합니다.  
특히 이 프로젝트는 버튼을 눌렀을 때(상승 엣지)만 LED 상태가 반전(ON/OFF 토글)되는 구조로,  
단순 입력 판별을 넘어 **엣지 트리거 이벤트 처리**를 실습하는 데 중점을 둡니다.

---

## 시연 영상

버튼을 누를 때마다 LED가 토글되는 동작을 아래 영상에서 확인할 수 있습니다:

[![시연 영상 바로가기](http://img.youtube.com/vi/N0Kje5kXbfY/0.jpg)](https://youtube.com/shorts/N0Kje5kXbfY)

---

## 동작 원리 상세 설명

- **버튼 상승 엣지 감지:**  
  GPIO 25번 핀의 입력값이 LOW에서 HIGH로 변할 때(=사용자가 버튼을 눌렀을 때),  
  `prev_state → curr_state` 변화를 감지하여 LED의 상태를 반전시킵니다.

- **LED 제어:**  
  GPIO 20번 핀에 연결된 LED는 `led.toggle()` 명령어를 통해 ON ↔ OFF 상태를 번갈아가며 유지합니다.

- **디바운싱 처리:**  
  버튼 튐 현상을 방지하기 위해 50ms 간격의 상태 비교 방식 polling을 사용합니다.

- **안전 종료 처리:**  
  `SIGINT`, `SIGTERM` 등의 시그널이 발생하면 LED를 소등하고 프로그램이 정상 종료되도록 처리합니다.

---

## 하드웨어 구성 설명

### GPIO 핀 연결 표

| 핀 번호 (BCM) | 연결된 부품 | 설명                        |
|---------------|--------------|-----------------------------|
| GPIO 25       | 버튼         | 입력 신호 감지, 풀업 구성     |
| GPIO 20       | LED          | 출력 제어용 핀               |

> **핵심:**  
> 이 프로젝트는 GPIO 입력의 상승 엣지를 트리거로 LED를 반전시키는 동작을 구현합니다.  
> 단순한 상태 읽기보다 한층 발전된 이벤트 기반 제어 방식입니다.

---

## 코드 설명 및 로직

아래 코드는 Python의 `gpiozero` 라이브러리를 사용하여  
버튼 입력의 상승 엣지(버튼 누름)를 감지하고, LED 상태를 토글하는 기능을 구현합니다.

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
    print("\nShutting down: Releasing GPIO resources...")
    led.off()
    sys.exit(0)

# ----------------------------------------------------------
# 4. 시그널 핸들러 등록 (Ctrl+C 또는 종료 요청 대응)
# ----------------------------------------------------------
signal(SIGINT, cleanup)
signal(SIGTERM, cleanup)

# ----------------------------------------------------------
# 5. 메인 루프: 버튼 상승 엣지 감지 시 LED 토글
# ----------------------------------------------------------
try:
    prev_state = button.is_pressed  # 이전 상태 저장

    while True:
        curr_state = button.is_pressed  # 현재 상태 읽기

        # 상승 엣지 검출: False → True
        if not prev_state and curr_state:
            led.toggle()

        prev_state = curr_state
        sleep(0.05)  # 디바운싱을 위한 지연 시간 (50ms)

except KeyboardInterrupt:
    cleanup(None, None)
```
---

## 라이선스
이 프로젝트는 [MIT License](../LICENSE) 하에 오픈소스로 공개됩니다.