import time
import serial

# 시리얼 포트 설정
ser = serial.Serial(
    port='/dev/ttyAMA0',  # 라즈베리파이의 시리얼 포트
    baudrate=9600,        # Arduino와 동일한 속도로 설정
    timeout=1,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE
)

# 시리얼 데이터 송신 함수
def send_serial_data(data):
    ser.write((data + '\n').encode())  # 문자열을 바이트로 인코딩하여 전송, 줄바꿈 추가

# 시리얼 데이터 수신 함수
def receive_serial_data():
    if ser.in_waiting > 0:
        try:
            # UTF-8 디코딩 시도
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"수신된 데이터: {data}")
            return data
        except UnicodeDecodeError:
            try:
                # UTF-8 실패시 ASCII 디코딩 시도
                data = ser.readline().decode('ascii', errors='ignore').strip()
                print(f"ASCII로 디코딩된 데이터: {data}")
                return data
            except Exception as e:
                print(f"디코딩 오류: {e}")
                # 오류 발생시 버퍼 비우기
                ser.reset_input_buffer()
        except Exception as e:
            print(f"시리얼 통신 오류: {e}")
            # 오류 발생시 버퍼 비우기
            ser.reset_input_buffer()
    return None

# 스톱워치 제어 함수
def toggle_stopwatch_a():
    print("타이머 A 토글됨")
    send_serial_data("타이머 A 토글")

def toggle_stopwatch_b():
    print("타이머 B 토글됨")
    send_serial_data("타이머 B 토글")

def reset_stopwatches():
    print("타이머 리셋 완료")
    send_serial_data("타이머 리셋 완료")

# 테스트 실행 루프
try:
    while True:
        # 시리얼 데이터 수신 처리
        received_data = receive_serial_data()
        if received_data:
            received_data = received_data.strip()  # 추가 공백 제거
            print(f"처리할 데이터: {received_data}")  # 디버깅용 출력

            if "toggle_a" in received_data.lower():  # 대소문자 구분 없이
                toggle_stopwatch_a()
            elif "toggle_b" in received_data.lower():  # 대소문자 구분 없이
                toggle_stopwatch_b()
            elif "reset" in received_data.lower():  # 대소문자 구분 없이
                reset_stopwatches()

        time.sleep(0.01)  # 딜레이 시간 감소
except KeyboardInterrupt:
    ser.close()  # 시리얼 포트 닫기
    print("프로그램을 종료합니다.")
