# 임베디드 통신시스템 프로젝트 - 핀컨트롤(2) counter8

이 프로젝트는 Raspberry Pi 5와 `pinctrl`을 활용하여 쉘 스크립트 내에서 GPIO를 제어하는 것을 목표로 합니다. 본 문서에서는 전체 코드의 로직, 하드웨어 연결 구성에 대해 기술합니다.
특히 counter8은 LED를 활용하여 0부터 7까지의 3비트 이진수를 시각적으로 표현하는 프로젝트입니다. 

---
## 시연 영상
실제 작동하는 모습을 아래 영상을 통해 확인할 수 있습니다:

[![시연 영상 바로가기](http://img.youtube.com/vi/9MFR2cRm7uk/0.jpg)](https://youtu.be/9MFR2cRm7uk)

### 핀맵과 GPIO에 대한 추가 설명입니다.
[![시연 영상 바로가기](http://img.youtube.com/vi/bRw7eX6XiOk/0.jpg)](https://youtu.be/bRw7eX6XiOk)

---
## 동작 원리 상세 설명

프로젝트의 핵심 동작은 **1초 간격**으로 LED의 상태를 변경하여 이진 카운터의 값을 표현하는 것입니다.  
다음과 같이 동작합니다:

- **1초 간격 카운트:**  
  메인 루프에서 0부터 7까지의 숫자를 순차적으로 출력합니다.  
  각 숫자는 1초 동안 유지되며, 그 동안 연결된 LED들이 해당 이진수의 각 비트에 맞춰 켜지거나 꺼집니다.

- **비트에 따른 LED 제어:**  
  - **LSB (최하위 비트):**  
    배열의 첫 번째 요소인 GPIO 5에 해당하며, 0 또는 1의 상태로 켜짐/꺼짐을 결정합니다.
  - **중간 비트:**  
    배열의 두 번째 요소인 GPIO 6이 해당하며, 1초마다 변화하는 값의 중간 비트 역할을 합니다.
  - **MSB (최상위 비트):**  
    배열의 세 번째 요소인 GPIO 13이 해당하며, 가장 큰 자리수로 LED를 제어합니다.

- **변환 과정:**  
  스크립트 내부의 `set_pin_states` 함수는 전달받은 숫자 값을 이진수로 변환한 후, 각 비트를 개별 GPIO 핀에 할당합니다.  
  예를 들어, 숫자 5는 이진수 `101`로 표현되며,  
  - GPIO 5 (LSB)는 1 → LED 점등  
  - GPIO 6 (중간 비트)는 0 → LED 소등  
  - GPIO 13 (MSB)는 1 → LED 점등  
  이러한 방식으로 LED들이 1초 간격으로 변화하면서 카운터 값을 시각적으로 표시합니다.

- **종료 처리:**  
  SIGINT나 SIGTERM과 같은 종료 시그널이 발생하면, `cleanup` 함수가 실행되어 모든 GPIO 핀을 LOW 상태로 초기화합니다. 
  이를 통해 안전하게 시스템이 종료됩니다.
---

## 하드웨어 구성 설명

### 실제 구성 이미지
![실제 하드웨어 구성 이미지](../image/ECS_count8_domino4_real.png.jpg)

### 하드웨어 구성 도식화
![하드웨어 구성 도식화](../image/ECS_count8_domino4.png)

### Raspberry Pi5 pinmap
![라즈베리파이5 핀맵](../image/RaspberryPi5pinmap.png)

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

아래는 GPIO 제어를 위한 전체 쉘 스크립트 코드입니다. 이 스크립트는 지정된 GPIO 핀을 출력 모드로 설정하고, 0부터 7까지의 이진수 값을 순차적으로 LED에 출력하여 이진 카운터를 구현합니다.

```bash
#!/usr/bin/env bash
# 스크립트가 실행될 때 사용할 Bash 인터프리터를 시스템의 PATH에서 찾아 실행합니다.
# 특히 /env 명령어를 사용해 환경변수 내에서 Bash 인터프리터를 찾기에, 
# 시스템마다 올바른 인터프리터 경로를 찾아 실행가능한 Portable입니다.

# 사용할 GPIO 핀 번호를 배열에 저장합니다.
# 배열 순서대로 각 핀이 이진수의 각 비트 (index 0: LSB, index 1: 중간, index 2: MSB) 역할을 합니다.
pins=(5 6 13)

# 현재 사용자가 root 권한으로 스크립트를 실행하는지 확인합니다.
# pinctrl이 GPIO핀 레지스터에 직접 쓰기에, 하드웨어적 위험을 동반하기에 sudo명령어 사용이 바람직합니다.
if [[ $EUID -ne 0 ]]; then
    echo "이 스크립트는 root 권한이 필요합니다. sudo로 실행하세요."
    exit 1
fi

# 'pinctrl' 명령어가 시스템에 설치되어 있는지 확인합니다.
# pinctrl는 GPIO 제어를 위한 명령어로, 존재하지 않으면 스크립트를 종료합니다.
if ! command -v pinctrl &> /dev/null; then
    echo "'pinctrl' 명령어가 설치되어 있지 않습니다."
    exit 1
fi

# 각 GPIO 핀을 출력 모드로 설정합니다.
# for 루프를 사용하여 배열 pins에 저장된 모든 핀에 대해 동작합니다.
# pinctrl set <핀 번호> op 명령어를 사용하여 해당 핀을 출력 모드(op)로 전환합니다.
# 만약 설정 실패 시, 에러 메시지를 출력하고 스크립트를 종료합니다.
for pin in "${pins[@]}"; do
    pinctrl set "$pin" op || { echo "GPIO $pin 설정 실패"; exit 1; }
done

# 스크립트 종료 시 호출될 cleanup 함수 정의
# 이 함수는 모든 GPIO 핀을 LOW(dl) 상태로 초기화하여 안전하게 종료하도록 합니다.
cleanup() {
    echo "종료 중: GPIO 핀 LOW로 초기화 중..."
    # 배열 pins에 저장된 모든 핀을 순회하면서 LOW 상태로 설정합니다.
    for pin in "${pins[@]}"; do
        pinctrl set "$pin" dl
    done
    exit 0
}

# SIGINT (Ctrl+C) 또는 SIGTERM 시그널이 발생하면 cleanup 함수를 실행하도록 trap 명령어로 설정합니다.
trap cleanup SIGINT SIGTERM

# 핀 상태를 설정하는 함수 정의
# 이 함수는 전달된 정수값(value)을 받아, 비트 단위 연산을 통해 각 GPIO 핀의 상태를 결정합니다.
set_pin_states() {
    local value=$1  # 함수 인자로 받은 값을 로컬 변수로 저장합니다.
    # 배열 pins의 각 인덱스와 값을 사용하여 반복합니다.
    # ${!pins[@]} 는 배열의 인덱스 목록을 반환합니다.
    for index in "${!pins[@]}"; do
        pin=${pins[$index]}  # 현재 인덱스에 해당하는 핀 번호를 가져옵니다.
        # 비트 연산을 사용하여 value의 해당 비트가 1인지 0인지 확인합니다.
        # (value >> index)는 value를 index만큼 오른쪽으로 시프트 하여, 해당 위치의 비트를 LSB로 만듭니다.
        # & 1 은 그 결과의 최하위 비트만 추출합니다.
        if (( (value >> index) & 1 )); then
            # 해당 비트가 1이면, pinctrl 명령어로 핀을 HIGH(dh) 상태로 설정합니다.
            pinctrl set "$pin" dh
        else
            # 해당 비트가 0이면, pinctrl 명령어로 핀을 LOW(dl) 상태로 설정합니다.
            pinctrl set "$pin" dl
        fi
    done
}

# 메인 실행 루프
# 무한 루프를 돌면서 0부터 7까지의 값을 순차적으로 출력합니다.
# 이진수 3비트(0~7)를 각 LED에 매핑하여, 각 핀의 상태를 업데이트합니다.
while true; do
    # 0부터 7까지의 숫자를 반복합니다.
    for ((i=0; i<8; i++)); do
        # 현재 숫자 i를 set_pin_states 함수에 전달하여, 이진수 비트에 따라 핀 상태를 변경합니다.
        set_pin_states "$i"
        # 각 상태 출력 후 1초 동안 대기하여 LED 상태 변화를 확인할 수 있도록 합니다.
        sleep 1
    done
done
```

---
## 라이선스
이 프로젝트는 [MIT License](../LICENSE) 하에 오픈소스로 공개됩니다.