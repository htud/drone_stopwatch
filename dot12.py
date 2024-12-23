from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageDraw, ImageFont
import time
import serial

# 매트릭스 설정
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 10  # 10개의 패널 사용
options.parallel = 1       # 단일 행으로 설정
options.hardware_mapping = 'regular'
options.gpio_slowdown = 4
matrix = RGBMatrix(options=options)

# 시리얼 포트 설정
ser = serial.Serial(
    port='/dev/ttyAMA1',  # 라즈베리파이의 시리얼 포트
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
elapsed_time_a = 0  # 추가: A의 누적 시간 저장
elapsed_time_b = 0  # 추가: B의 누적 시간 저장
last_time_a = "00:00:00"
last_time_b = "00:00:00"

# 이전 텍스트 상태 저장
prev_time_a = None
prev_time_b = None

# 스톱워치 텍스트 업데이트 함수
def update_stopwatch_texts():
    global last_time_a, last_time_b
    if running_a:
        elapsed_time_a = time.time() - start_time_a
        # 밀리초 단위로 변환 (초 * 1000)
        elapsed_ms_a = int(elapsed_time_a * 1000)
        minutes_a = elapsed_ms_a // (1000 * 60)
        seconds_a = (elapsed_ms_a // 1000) % 60
        milliseconds_a = (elapsed_ms_a % 1000) // 10  # 밀리초를 10으로 나누어 2자리로
        last_time_a = f"{minutes_a:02}:{seconds_a:02}.{milliseconds_a:02}"

    if running_b:
        elapsed_time_b = time.time() - start_time_b
        # 밀리초 단위로 변환 ( * 1000)
        elapsed_ms_b = int(elapsed_time_b * 1000)
        minutes_b = elapsed_ms_b // (1000 * 60)
        seconds_b = (elapsed_ms_b // 1000) % 60
        milliseconds_b = (elapsed_ms_b % 1000) // 10  # 밀리초를 10으로 나누어 2자리로
        last_time_b = f"{minutes_b:02}:{seconds_b:02}.{milliseconds_b:02}"

# 텍스트 표시 함수
def display_texts():
    global prev_time_a, prev_time_b

    if last_time_a == prev_time_a and last_time_b == prev_time_b:
        return

    img = Image.new("RGB", (matrix.width, matrix.height), "black")
    draw = ImageDraw.Draw(img)

    # B 스톱워치 시간 표시
    img_b = Image.new("RGB", (matrix.width // 2, int(matrix.height * 0.8)), "black")
    draw_b = ImageDraw.Draw(img_b)
    text_bbox_b = draw_b.textbbox((0, 0), last_time_b, font=font_pillow)
    x_b = (img_b.width - (text_bbox_b[2] - text_bbox_b[0])) // 2
    y_b = (img_b.height - (text_bbox_b[3] - text_bbox_b[1])) // 2
    draw_b.text((x_b, y_b), last_time_b, font=font_pillow, fill=(255, 255, 255))
    img.paste(img_b, (matrix.width // 2, 0))

    # A 스톱워치 시간 표시
    img_a = Image.new("RGB", (matrix.width // 2, int(matrix.height * 1.3)), "black")
    draw_a = ImageDraw.Draw(img_a)
    text_bbox_a = draw_a.textbbox((0, 0), last_time_a, font=font_pillow)
    x_a = (img_a.width - (text_bbox_a[2] - text_bbox_a[0])) // 2
    y_a = (img_a.height - (text_bbox_a[3] - text_bbox_a[1])) // 2
    draw_a.text((x_a, y_a), last_time_a, font=font_pillow, fill=(255, 255, 255))
    rotated_img_a = img_a.transpose(Image.ROTATE_180)
    img.paste(rotated_img_a, (0, 0))

    matrix.SetImage(img)
    prev_time_a = last_time_a
    prev_time_b = last_time_b

# 시리얼 데이터 송신 함수
def send_serial_data(data):
    ser.write((data + '\n').encode())  # 문자열을 바이트��� 인코딩하여 전송, 줄바꿈 추가

# 시리얼 데이터 수신 함수 수정
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

# 리셋 함수 추가



# 시작할 때 타이머 초기화
def initialize_timer():
    global start_time
    start_time = 0  # 또는 원하는 시작 시간으로 설정
    
# 프로그램 시작 시 초기화 함수 호출
initialize_timer()

# 테스트 실행 루프
try:
    while True:
        update_stopwatch_texts()
        display_texts()

        # 시리얼 데이터 수신 처리
        received_data = receive_serial_data()
        if received_data:
            received_data = received_data.strip()  # 추가 공백 제거
            print(f"처리할 데이터: {received_data}")  # 디버깅용 출력
            
            if "toggle_a" in received_data.lower():  # 대소문자 구분 없이
                toggle_stopwatch_a()
                print("타이머 A 토글됨")
            elif "toggle_b" in received_data.lower():  # 대소문자 구분 없이
                toggle_stopwatch_b()
                print("타이머 B 토글됨")
            elif "timers have been reset" in received_data.lower():  # 대소문자 구분 없이
                # A와 B 타이머를 순차적으로 리셋
                reset_stopwatch_a()
                time.sleep(0.1)  # A와 B 리셋 사이에 지연 추가
                reset_stopwatch_b()
                print("타이머 리셋 완료")

        time.sleep(0.01)  # 딜레이 시간 감소
except KeyboardInterrupt:
    matrix.Clear()
    ser.close()  # 시리얼 포트 닫기
    print("프로그램을 종료합니다.")





