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
        """테스트를 위한 샘플 data.json 파일을 생성합니다."""
        
        # 5x5, 13x13, 25x25 데이터를 자동으로 생성하는 로직
        def generate_dummy_matrix(size, fill_value=1.0):
            return [[float(fill_value) for _ in range(size)] for _ in range(size)]

        sample_data = {
            "filters": {
                "size_5": generate_dummy_matrix(5, 1),
                "size_13": generate_dummy_matrix(13, 0.5),
                "size_25": generate_dummy_matrix(25, 0.1)
            },
            "patterns": {
                "size_5_test": {
                    "input": generate_dummy_matrix(5, 10),
                    "expected": 250.0
                },
                "size_13_01": {
                    "input": generate_dummy_matrix(13, 2),
                    "expected": 169.0
                },
                "size_25_final": {
                    "input": generate_dummy_matrix(25, 5),
                    "expected": 312.5
                },
                "size_5_error_case": { # 에러 검증용 (행 개수 부족)
                    "input": [[1, 2], [3, 4]], 
                    "expected": 0.0
                }
            }
        }

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, indent=2) # 보기 좋게 들여쓰기 포함
            print(f"[알림] 테스트용 {file_path} 파일이 생성되었습니다.")
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
            
            # 1. 키에서 N 추출 (정규표현식 사용)
            match = re.search(r'size_(\d+)', key)
            if not match:
                print(f"FAIL: 키 '{key}'에서 사이즈(N)를 추출할 수 없습니다.")
                continue
            
            n_str = match.group(1)
            filter_key = f"size_{n_str}"
            n_val = int(n_str) # 추출한 N을 숫자로 변환 (필터/패턴 크기)

            # 2. 필터 존재 여부 확인
            if filter_key not in filters_data:
                print(f"FAIL: '{filter_key}'에 해당하는 필터가 filters 항목에 없습니다.")
                continue

            # 3. 데이터 구조 가져오기
            filter_raw = filters_data[filter_key]
            pattern_raw = content.get("input", [])
            expected = content.get("expected")

            # 4. 크기 일치 검증 (N x N 인지 확인)
            # 필터와 패턴의 행(row) 수가 N과 맞는지 확인
            if len(filter_raw) != n_val or len(pattern_raw) != n_val:
                print(f"FAIL: 크기 불일치 (정의된 N:{n_val}, 필터 행:{len(filter_raw)}, 패턴 행:{len(pattern_raw)})")
                continue

            # 5. Matrix 객체로 변환 (기존 Matrix 클래스 활용)
            try:
                f_matrix = Matrix(n_val)
                p_matrix = Matrix(n_val)
                
                for r in range(n_val):
                    # 각 행의 열(column) 개수도 N인지 검증
                    if len(filter_raw[r]) != n_val or len(pattern_raw[r]) != n_val:
                        raise ValueError("열 개수 불일치")
                        
                    for c in range(n_val):
                        f_matrix.set_value(r, c, float(filter_raw[r][c]))
                        p_matrix.set_value(r, c, float(pattern_raw[r][c]))
                
                print(f"SUCCESS: {filter_key} 필터와 패턴 로드 완료 (Size: {n_val}x{n_val})")
                # TODO: 여기서 MAC 연산 및 expected 비교 로직 실행
                
            except (ValueError, IndexError):
                print(f"FAIL: 데이터 내부의 행렬 크기가 {n_val}x{n_val} 구조가 아닙니다.")
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