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

# 실행 테스트
if __name__ == "__main__":
    sim = MiniNPUSimulator()
    sim.run_mode_1()