import serial
import pandas as pd
from tabulate import tabulate
import os
from datetime import datetime
import serial.tools.list_ports  # 새로운 import 추가

# 사용 가능한 시리얼 포트 찾기
def find_arduino_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if 'Arduino' in port.description:  # Arduino가 포함된 포트 찾기
            return port.device
    return None

# 시리얼 포트 설정
arduino_port = find_arduino_port()
if arduino_port:
    ser = serial.Serial(arduino_port, 9600)
    print(f"Arduino가 {arduino_port}에 연결되었습니다.")
else:
    raise Exception("Arduino를 찾을 수 없습니다. 연결을 확인해주세요.")
    time.sleep(2)

# 바탕화면 경로 가져오기
desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
save_directory = os.path.join(desktop_path, "타임워치_데이터")

# 저장 폴더가 없다면 생성
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# 현재 시간 가져오기
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

# 전체 파일 경로 설정
file_name = f"타임워치_{current_time}.xlsx"
full_path = os.path.join(save_directory, file_name)
save_directory = os.path.join(desktop_path, "타임워치_데이터")

# 저장 폴더가 없다면 생성
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# 현재 시간 가져오기
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

# 전체 파일 경로 설정
file_name = f"타임워치_{current_time}.xlsx"
full_path = os.path.join(save_directory, file_name)

# 새로운 데이터프레임 생성
data = {
    "팀": [],
    "A 타임": [],
    "B 타임": []
}

# DataFrame 생성 및 저장
df = pd.DataFrame(data)
df.to_excel(full_path, index=False, sheet_name="Timer Data")

print(f"새로운 엑셀 파일 생성 완료: {full_path}")

# 초기 팀 번호 설정
team_number = 1
time_a = None  # A 타이머 결과
time_b = None  # B 타이머 결과


# 현재 DataFrame을 테이블 형식으로 출력하는 함수 수정
def print_table(df):
    print("\n=== 현재 기록된 데이터 ===")
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    print("========================\n")


try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(f"\n수신된 데이터: {line}")

            if "Sending reset signal" in line:
                print("➡️ 리셋 신호 수신됨")
                
            elif "Received: A_FINAL:" in line:
                time_a = line.split("Received: A_FINAL:")[1].strip()
                print(f"➡️ A 타이머 정지 - 기록: {time_a}")
                
            elif "Received: B_FINAL:" in line:
                time_b = line.split("Received: B_FINAL:")[1].strip()
                print(f"➡️ B 타이머 정지 - 기록: {time_b}")
                
                if time_a is not None or time_b is not None:
                    # None 값을 빈 문자열로 대체
                    time_a = time_a if time_a is not None else ""
                    time_b = time_b if time_b is not None else ""

                    df = pd.DataFrame(data)
                    try:
                        df.to_excel(full_path, index=False)
                        print(f"\n✅ 저장 완료!")
                    except PermissionError:
                        print(f"\n❌ 엑셀 파일이 열려있어 저장할 수 없습니다. 파일을 닫고 다시 시도해주세요.")
                        # 데이터를 다시 제거 (저장 실패)
                        data["팀"].pop()
                        data["A 타임"].pop()
                        data["B 타임"].pop()
                        continue

                    print(f"팀: {team_number}팀")
                    print(f"A 타임: {time_a}")
                    print(f"B 타임: {time_b}")
                    
                    # 테이블 형식으로 전체 데이터 출력
                    print_table(df)

                    team_number += 1
                    time_a = None
                    time_b = None

except KeyboardInterrupt:
    print("프로그램 종료")

finally:
    ser.close()
