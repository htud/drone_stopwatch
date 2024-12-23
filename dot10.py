from PIL import Image, ImageDraw, ImageFont
import time
import serial

# 시리얼 포트 설정 (테스트용으로 실제 포트 연결 필요)
# 테스트 시 포트 설정 부분 주석 처리 또는 가상 포트로 대체
 ser = serial.Serial(
     port='/dev/ttyAMA3',  # 라즈베리파이의 시리얼 포트
     baudrate=9600,        # Arduino와 동일한 속도로 설정
     timeout=1,
     bytesize=serial.EIGHTBITS,
     parity=serial.PARITY_NONE,
     stopbits=serial.STOPBITS_ONE
 )

# 폰트 설정 (TTF 폰트 사용)
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_pillow = ImageFont.truetype(font_path, 47)  # 폰트 크기 47로 설정

# 스톱워치 상태
running_a = False
running_b = False
start_time_a = 0
start_time_b = 0
elapsed_time_a = 0  # A의 누적 시간 저장
elapsed_time_b = 0  # B의 누적 시간 저장
last_time_a = "00:00:00"
last_time_b = "00:00:00"

# 스톱워치 텍스트 업데이트 함수
def update_stopwatch_texts():
    global last_time_a, last_time_b
    if running_a:
        elapsed_time_a = time.time() - start_time_a
        minutes_a = int(elapsed_time_a // 60)
        seconds_a = int(elapsed_time_a % 60)
        milliseconds_a = int((elapsed_time_a % 1) * 100)
        last_time_a = f"{minutes_a:02}:{seconds_a:02}.{milliseconds_a:02}"

    if running_b:
        elapsed_time_b = time.time() - start_time_b
        minutes_b = int(elapsed_time_b // 60)
        seconds_b = int(elapsed_time_b % 60)
        milliseconds_b = int((elapsed_time_b % 1) * 100)
        last_time_b = f"{minutes_b:02}:{seconds_b:02}.{milliseconds_b:02}"

# 텍스트 표시 함수 (콘솔 출력으로 대체)
def display_texts():
    print(f"A: {last_time_a} | B: {last_time_b}")

# 시리얼 데이터 송신 함수
def send_serial_data(data):
    print(f"송신 데이터: {data}")
    # 실제 송신 코드: ser.write((data + '\n').encode())

# 시리얼 데이터 수신 함수 수정 (테스트용)
def receive_serial_data():
    # 테스트 시 가상 데이터 반환
    test_data = input("수신 데이터 입력 (예: toggle_a, toggle_b, timers have been reset): ").strip()
    if test_data:
        print(f"수신된 데이터: {test_data}")
        return test_data
    return None

# 스톱워치 제어 함수
def toggle_stopwatch_a():
    global running_a, start_time_a, elapsed_time_a
    if not running_a:
        start_time_a = time.time() - elapsed_time_a  # 누적 시간을 고려하여 시작 시간 설정
        running_a = True
    else:
        running_a = False
        elapsed_time_a = time.time() - start_time_a  # 현재까지의 경과 시간 저장
        send_serial_data(last_time_a)

def toggle_stopwatch_b():
    global running_b, start_time_b, elapsed_time_b
    if not running_b:
        start_time_b = time.time() - elapsed_time_b  # 누적 시간을 고려하여 시작 시간 설정
        running_b = True
    else:
        running_b = False
        elapsed_time_b = time.time() - start_time_b  # 현재까지의 경과 시간 저장
        send_serial_data(last_time_b)

# 리셋 함수
def reset_stopwatch_a():
    global running_a, start_time_a, elapsed_time_a, last_time_a
    running_a = False
    start_time_a = 0
    elapsed_time_a = 0
    last_time_a = "00:00:00"

def reset_stopwatch_b():
    global running_b, start_time_b, elapsed_time_b, last_time_b
    running_b = False
    start_time_b = 0
    elapsed_time_b = 0
    last_time_b = "00:00:00"

# 테스트 실행 루프
try:
    while True:
        update_stopwatch_texts()
        display_texts()

        # 시리얼 데이터 수신 처리
        received_data = receive_serial_data()
        if received_data:
            if "toggle_a" in received_data.lower():  # A 타이머 토글
                toggle_stopwatch_a()
                print("타이머 A 토글됨")
            elif "toggle_b" in received_data.lower():  # B 타이머 토글
                toggle_stopwatch_b()
                print("타이머 B 토글됨")
            elif "timers have been reset" in received_data.lower():  # 리셋
                reset_stopwatch_a()
                reset_stopwatch_b()
                print("타이머 리셋 완료")

        time.sleep(0.01)  # 딜레이
except KeyboardInterrupt:
    print("프로그램 종료")
