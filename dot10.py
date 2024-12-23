import time
import serial

# 시리얼 포트 설정
ser = serial.Serial(
    port='/dev/ttyAMA1',  # 라즈베리파이의 시리얼 포트
    baudrate=9600,        # Arduino와 동일한 속도로 설정
    timeout=1,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE
)

# 현재 시간을 포맷팅해서 반환하는 함수
def get_current_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

# 스톱워치 상태 변수
timer_a_running = False
timer_b_running = False
timer_a_start = 0
timer_b_start = 0

def get_elapsed_time(start_time):
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    milliseconds = int((elapsed * 1000) % 1000)
    return f"{minutes:02}:{seconds:02}.{milliseconds:03}"

# 시리얼 데이터 송신 함수
def send_serial_data(data):
    ser.write((data + '\n').encode())  # 문자열을 바이트로 인코딩하여 전송, 줄바꿈 추가

# 시리얼 데이터 수신 함수
def receive_serial_data():
    if ser.in_waiting > 0:
        try:
            # UTF-8 디코딩 시도
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"{get_current_time()} - 수신된 데이터: {data}")
            return data
        except UnicodeDecodeError:
            try:
                # UTF-8 실패시 ASCII 디코딩 시도
                data = ser.readline().decode('ascii', errors='ignore').strip()
                print(f"{get_current_time()} - ASCII로 디코딩된 데이터: {data}")
                return data
            except Exception as e:
                print(f"{get_current_time()} - 디코딩 오류: {e}")
                # 오류 발생시 버퍼 비우기
                ser.reset_input_buffer()
        except Exception as e:
            print(f"{get_current_time()} - 시리얼 통신 오류: {e}")
            # 오류 발생시 버퍼 비우기
            ser.reset_input_buffer()
    return None

# 스톱워치 제어 함수
def toggle_stopwatch_a():
    global timer_a_running, timer_a_start
    if timer_a_running:
        elapsed_time = get_elapsed_time(timer_a_start)
        print(f"{get_current_time()} - 타이머 A 중지: {elapsed_time}")
        send_serial_data(f"타이머 A 중지: {elapsed_time}")
        timer_a_running = False
    else:
        timer_a_start = time.time()
        print(f"{get_current_time()} - 타이머 A 시작")
        send_serial_data("타이머 A 시작")
        timer_a_running = True

def toggle_stopwatch_b():
    global timer_b_running, timer_b_start
    if timer_b_running:
        elapsed_time = get_elapsed_time(timer_b_start)
        print(f"{get_current_time()} - 타이머 B 중지: {elapsed_time}")
        send_serial_data(f"타이머 B 중지: {elapsed_time}")
        timer_b_running = False
    else:
        timer_b_start = time.time()
        print(f"{get_current_time()} - 타이머 B 시작")
        send_serial_data("타이머 B 시작")
        timer_b_running = True

def reset_stopwatches():
    global timer_a_running, timer_b_running, timer_a_start, timer_b_start
    timer_a_running = False
    timer_b_running = False
    timer_a_start = 0
    timer_b_start = 0
    print(f"{get_current_time()} - 타이머 리셋 완료")
    send_serial_data("타이머 리셋 완료")

# 테스트 실행 루프
try:
    while True:
        # 시리얼 데이터 수신 처리
        received_data = receive_serial_data()
        if received_data:
            received_data = received_data.strip()  # 추가 공백 제거
            print(f"{get_current_time()} - 처리할 데이터: {received_data}")  # 디버깅용 출력

            if "toggle_a" in received_data.lower():  # 대소문자 구분 없이
                toggle_stopwatch_a()
            elif "toggle_b" in received_data.lower():  # 대소문자 구분 없이
                toggle_stopwatch_b()
            elif "reset" in received_data.lower():  # 대소문자 구분 없이
                reset_stopwatches()

        time.sleep(0.01)  # 딜레이 시간 감소
except KeyboardInterrupt:
    ser.close()  # 시리얼 포트 닫기
    print(f"{get_current_time()} - 프로그램을 종료합니다.")
