import json
import re
import os

class Matrix:
    def __init__(self, size):
        self.size = size
        self.data = [[0.0 for _ in range(size)] for _ in range(size)]

    def set_value(self, r, c, value):
        self.data[r][c] = value

    def get_value(self, r, c):
        return self.data[r][c]

class MiniNPUSimulator:
    def __init__(self):
        self.epsilon = 1e-9

    # [추가] 과제 요구사항인 5, 13, 25 크기를 포함한 샘플 JSON 저장 기능
    def save_sample_json(self, file_path="data.json"):
        """십자가(Cross)와 X 모양을 자동으로 생성하여 JSON으로 저장합니다."""
        
        # 1. 십자가 모양 생성 함수
        def generate_cross(size):
            matrix = [[0.0 for _ in range(size)] for _ in range(size)]
            mid = size // 2
            for i in range(size):
                matrix[mid][i] = 1.0  # 가로줄
                matrix[i][mid] = 1.0  # 세로줄
            return matrix

        # 2. X 모양 생성 함수
        def generate_x(size):
            matrix = [[0.0 for _ in range(size)] for _ in range(size)]
            for i in range(size):
                matrix[i][i] = 1.0                # 왼쪽 위 -> 오른쪽 아래 대각선
                matrix[i][size - 1 - i] = 1.0     # 오른쪽 위 -> 왼쪽 아래 대각선
            return matrix

        # 데이터 구성
        sample_data = {
            "filters": {
                "cross_5": generate_cross(5),
                "x_13": generate_x(13),
                "cross_25": generate_cross(25)
            },
            "patterns": {
                "cross_5_test": {
                    "input": generate_cross(5),
                    "expected": "+"  # 'Cross'로 정규화됨
                },
                "x_13_case01": {
                    "input": generate_x(13),
                    "expected": "x"  # 'X'로 정규화됨
                },
                "cross_25_final": {
                    "input": generate_cross(25),
                    "expected": "cross" # 'Cross'로 정규화됨
                },
                "x_5_error": { # 검증용 에러 데이터 (행 부족)
                    "input": [[1.0, 0.0, 1.0]], 
                    "expected": "X"
                }
            }
        }

        try:
            # 가로 출력을 위한 정규식 처리 (이전 단계에서 배운 내용)
            import re
            json_string = json.dumps(sample_data, indent=2)
            json_string = re.sub(r'(\d+\.?\d*),\s*\n\s*', r'\1, ', json_string)
            json_string = re.sub(r'\[\s*\n\s*', r'[', json_string)
            json_string = re.sub(r',\s*\n\s*\]', r']', json_string)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_string)
            print(f"[알림] {file_path}에 진짜 모양(Cross, X) 데이터가 저장되었습니다.")
        except Exception as e:
            print(f"파일 저장 중 오류 발생: {e}")

    def get_user_input_matrix(self, size, name):
        """요구사항: 3x3 필터/패턴을 입력받고 검증하는 함수"""
        print(f"\n--- [{name} 입력] ---")
        matrix = Matrix(size)
        
        row_idx = 0
        while row_idx < size:
            try:
                # 1. 한 줄 입력받기 (공백 구분)
                line = input(f"{row_idx + 1}행 입력: ").split()
                
                # 2. 열 개수 검증 (3개가 맞는지)
                if len(line) != size:
                    print(f"입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요.")
                    continue  # 현재 줄 다시 입력
                
                # 3. 숫자 파싱 및 Matrix 저장
                for col_idx in range(size):
                    value = float(line[col_idx])  # 숫자 변환 실패 시 ValueError 발생
                    matrix.set_value(row_idx, col_idx, value)
                
                row_idx += 1  # 정상 입력 시 다음 행으로 이동
                
            except ValueError:
                # 숫자가 아닌 값이 들어왔을 때 안내 문구
                print("입력 형식 오류: 숫자만 입력 가능합니다. 다시 입력해주세요.")
        
        return matrix
    
    def normalize_label(self, label):
        """요구사항: '+', 'cross' -> 'Cross' / 'x' -> 'X'로 정규화"""
        label_str = str(label).lower().strip() # 소문자로 바꾸고 공백 제거
        
        if label_str in ['+', 'cross']:
            return "Cross"
        elif label_str == 'x':
            return "X"
        
        return label # 그 외의 경우 (예: 숫자인 경우 등) 그대로 반환

    def run_mode_1(self):
        """모드 1의 전체 흐름 제어"""
        print("=== 모드 1: 사용자 입력 (3x3) ===")
        
        # 필터 A, B 및 패턴 입력 (3x3 고정)
        filter_a = self.get_user_input_matrix(3, "필터 A")
        filter_b = self.get_user_input_matrix(3, "필터 B")
        pattern  = self.get_user_input_matrix(3, "패턴")
        
        print("\n[알림] 모든 데이터가 성공적으로 저장되었습니다.")
        # 이 다음 단계는 MAC 연산을 수행하는 코드가 들어갈 자리입니다.

    def run_mode_2(self, file_path="data.json"):
        print(f"\n=== 모드 2: JSON 로드 및 검증 ({file_path}) ===")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"파일 로드 실패: {e}")
            return

        filters_data = data.get("filters", {})
        patterns_data = data.get("patterns", {})

        for key, content in patterns_data.items():
            print(f"\n[Case: {key}] 검증 중...")
            
            # 1. 키에서 모양(Shape)과 사이즈(N) 추출
            # 정규표현식 설명: ([a-zA-Z\+]+) -> 영문자나 + 기호 추출 / (\d+) -> 숫자 추출
            match = re.search(r'([a-zA-Z\+]+)_(\d+)', key)
            if not match:
                print(f"FAIL: 키 '{key}'에서 형식(Shape_N)을 추출할 수 없습니다.")
                continue
            
            raw_shape = match.group(1)   # 예: 'cross', 'x', '+'
            n_str = match.group(2)       # 예: '5', '13'
            n_val = int(n_str)
            
            # [추가] 라벨 정규화 적용 (표준 라벨로 변환)
            standard_label = self.normalize_label(raw_shape)
            filter_key = f"{raw_shape}_{n_str}" # JSON의 filters에서 찾을 실제 키

            # 2. 필터 존재 여부 확인
            if filter_key not in filters_data:
                print(f"FAIL: '{filter_key}'에 해당하는 필터가 filters 항목에 없습니다.")
                continue

            # 3. 데이터 가져오기 및 expected 정규화
            filter_raw = filters_data[filter_key]
            pattern_raw = content.get("input", [])
            
            # [추가] expected 값 정규화 (+ -> Cross 등)
            raw_expected = content.get("expected")
            standard_expected = self.normalize_label(raw_expected)

            # 4. 크기 일치 검증 (행 검사)
            if len(filter_raw) != n_val or len(pattern_raw) != n_val:
                print(f"FAIL: 크기 불일치 (정의된 N:{n_val}, 필터 행:{len(filter_raw)}, 패턴 행:{len(pattern_raw)})")
                continue

            # 5. Matrix 객체로 변환 및 열 검증
            try:
                f_matrix = Matrix(n_val)
                p_matrix = Matrix(n_val)
                
                for r in range(n_val):
                    if len(filter_raw[r]) != n_val or len(pattern_raw[r]) != n_val:
                        raise ValueError(f"{r+1}행의 열 개수가 {n_val}이 아닙니다.")
                        
                    for c in range(n_val):
                        f_matrix.set_value(r, c, float(filter_raw[r][c]))
                        p_matrix.set_value(r, c, float(pattern_raw[r][c]))
                
                # [수정] 성공 메시지에 정규화된 라벨 표시
                print(f"SUCCESS: [{standard_label}] 필터(Size: {n_val}x{n_val}) 로드 완료")
                print(f"정보: 기대값(Expected) -> {standard_expected}")
                
                # 6. MAC 연산 수행 및 결과 도출
                # (가정: simulator 내부에 mac_operation 메서드가 있다고 가정합니다)
                score = self.mac_operation(f_matrix, p_matrix)
                
                # 점수에 따라 결과 라벨 결정 (예: 0보다 크면 해당 모양으로 판정)
                # 이 로직은 과제의 상세 기준에 따라 조정하세요.
                actual_result = standard_label if score > 0 else "Unknown"

                # 7. PASS/FAIL 판정 및 출력 (표준 라벨 기준)
                if actual_result == standard_expected:
                    result_status = "PASS"
                else:
                    result_status = "FAIL"

                print(f"[{result_status}] 연산 스코어: {score:.2f}")
                print(f"결과 라벨: {actual_result} | 기대 라벨: {standard_expected}")
                
            except (ValueError, IndexError) as e:
                print(f"FAIL: 데이터 구조 오류 ({e})")
                continue

# 실행 테스트
if __name__ == "__main__":
    sim = MiniNPUSimulator()
    
    # 1. 프로그램 실행 시 JSON 파일이 없으면 자동으로 생성
    if not os.path.exists("data.json"):
        sim.save_sample_json()
    
    print("\n--- Mini NPU Simulator ---")
    mode = input("실행할 모드를 선택하세요 (1: 수동, 2: JSON): ")
    if mode == "1":
        sim.run_mode_1()
    elif mode == "2":
        sim.run_mode_2()