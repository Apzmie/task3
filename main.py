import json
import time
import re
import os


# -----------------------------
# Matrix 클래스
# -----------------------------
class Matrix:
    def __init__(self, size):
        self.size = size
        self.data = [[0.0 for _ in range(size)] for _ in range(size)]

    def set_value(self, r, c, value):
        self.data[r][c] = value

    def get_value(self, r, c):
        return self.data[r][c]


# -----------------------------
# Mini NPU Simulator
# -----------------------------
class MiniNPUSimulator:
    def __init__(self):
        self.epsilon = 1e-9

    # -----------------------------
    # JSON 자동 생성
    # -----------------------------
    def create_json(self):
        def cross(n):
            m = [[0.0]*n for _ in range(n)]
            mid = n//2
            for i in range(n):
                m[mid][i] = 1.0
                m[i][mid] = 1.0
            return m

        def x(n):
            m = [[0.0]*n for _ in range(n)]
            for i in range(n):
                m[i][i] = 1.0
                m[i][n-i-1] = 1.0
            return m

        data = {
            "filters": {
                "cross_5": cross(5),
                "x_5": x(5),
                "cross_13": cross(13),
                "x_13": x(13),
                "cross_25": cross(25),
                "x_25": x(25)
            },
            "patterns": {
                "size_5_1": {"input": cross(5), "expected": "+"},
                "size_5_2": {"input": x(5), "expected": "x"},
                "size_13_1": {"input": cross(13), "expected": "cross"},
                "size_13_2": {"input": x(13), "expected": "x"},
                "size_25_1": {"input": cross(25), "expected": "+"},
                "size_25_2": {"input": x(25), "expected": "+"},
            }
        }

        with open("data.json", "w") as f:
            json.dump(data, f, indent=2)

        print("[알림] data.json 생성 완료")

    # -----------------------------
    # 라벨 정규화
    # -----------------------------
    def normalize_label(self, label):
        label = str(label).lower().strip()
        if label in ['+', 'cross']:
            return "Cross"
        elif label == 'x':
            return "X"
        return label

    # -----------------------------
    # MAC 연산
    # -----------------------------
    def mac_operation(self, m1, m2):
        total = 0.0
        for i in range(m1.size):
            for j in range(m1.size):
                total += m1.get_value(i, j) * m2.get_value(i, j)
        return total

    # -----------------------------
    # 시간 측정
    # -----------------------------
    def measure_time(self, func, repeat=10):
        start = time.time()
        for _ in range(repeat):
            func()
        end = time.time()
        return ((end - start) / repeat) * 1000

    # -----------------------------
    # Matrix 생성
    # -----------------------------
    def build_matrix(self, raw, n):
        m = Matrix(n)
        for i in range(n):
            for j in range(n):
                m.set_value(i, j, float(raw[i][j]))
        return m

    # -----------------------------
    # 사용자 입력
    # -----------------------------
    def input_matrix(self, name, size=3):
        print(f"\n{name} ({size}줄 입력, 공백 구분)")

        m = Matrix(size)

        for i in range(size):
            while True:
                try:
                    row = input().strip().split()
                    if len(row) != size:
                        raise ValueError

                    for j in range(size):
                        m.set_value(i, j, float(row[j]))
                    break
                except:
                    print(f"입력 오류: {size}개의 숫자를 입력하세요.")

        return m

    # -----------------------------
    # 모드 1 (사용자 입력)
    # -----------------------------
    def run_mode1(self):
        print("\n=== 사용자 입력 모드 (3x3) ===")

        filter_a = self.input_matrix("필터 A")
        filter_b = self.input_matrix("필터 B")
        pattern = self.input_matrix("패턴")

        def mac_pair():
            a = self.mac_operation(filter_a, pattern)
            b = self.mac_operation(filter_b, pattern)
            return a, b

        # 시간 측정
        start = time.time()
        for _ in range(10):
            a_score, b_score = mac_pair()
        end = time.time()

        avg_time = ((end - start) / 10) * 1000

        # 판정
        if abs(a_score - b_score) < self.epsilon:
            result = "UNDECIDED"
        elif a_score > b_score:
            result = "A"
        else:
            result = "B"

        print("\n[결과]")
        print(f"A 점수: {a_score}")
        print(f"B 점수: {b_score}")
        print(f"연산 시간(ms): {avg_time:.6f}")
        print(f"판정: {result}")

    # -----------------------------
    # 성능 분석
    # -----------------------------
    def performance(self, filters):
        print("\n[성능 분석]")
        print("크기\t평균 시간(ms)\t연산 수(N^2)")

        for n in [3, 5, 13, 25]:
            if n == 3:
                # 더미 3x3
                m = Matrix(3)
                for i in range(3):
                    for j in range(3):
                        m.set_value(i, j, 1.0)
            else:
                key = f"cross_{n}"
                if key not in filters:
                    continue
                m = self.build_matrix(filters[key], n)

            t = self.measure_time(lambda: self.mac_operation(m, m))
            print(f"{n}x{n}\t{t:.6f}\t{n*n}")

    # -----------------------------
    # 모드 2 (JSON 분석)
    # -----------------------------
    def run_mode2(self):
        if not os.path.exists("data.json"):
            self.create_json()

        with open("data.json") as f:
            data = json.load(f)

        filters = data["filters"]
        patterns = data["patterns"]

        total, passed, failed = 0, 0, 0
        fail_list = []

        print("\n=== data.json 분석 ===")

        for key, content in patterns.items():
            total += 1
            print(f"\n--- {key} ---")

            match = re.search(r'\d+', key)
            if not match:
                print("FAIL: 키 파싱 실패")
                failed += 1
                fail_list.append((key, "키 파싱 실패"))
                continue

            n = int(match.group())

            if f"cross_{n}" not in filters or f"x_{n}" not in filters:
                print("FAIL: 필터 없음")
                failed += 1
                fail_list.append((key, "필터 없음"))
                continue

            pattern_raw = content.get("input", [])
            expected = self.normalize_label(content.get("expected"))

            if len(pattern_raw) != n:
                print("FAIL: 크기 불일치")
                failed += 1
                fail_list.append((key, "크기 불일치"))
                continue

            try:
                cross = self.build_matrix(filters[f"cross_{n}"], n)
                x = self.build_matrix(filters[f"x_{n}"], n)
                p = self.build_matrix(pattern_raw, n)
            except:
                print("FAIL: 데이터 오류")
                failed += 1
                fail_list.append((key, "데이터 오류"))
                continue

            cs = self.mac_operation(cross, p)
            xs = self.mac_operation(x, p)

            if abs(cs - xs) < self.epsilon:
                pred = "UNDECIDED"
            elif cs > xs:
                pred = "Cross"
            else:
                pred = "X"

            if pred == expected:
                status = "PASS"
                passed += 1
            else:
                status = "FAIL"
                failed += 1
                fail_list.append((key, f"예측:{pred}, 기대:{expected}"))

            print(f"Cross: {cs}")
            print(f"X: {xs}")
            print(f"판정: {pred} | expected: {expected} | {status}")

        # 성능 분석
        self.performance(filters)

        # 결과 요약
        print("\n[결과 요약]")
        print(f"총: {total}, 통과: {passed}, 실패: {failed}")

        if fail_list:
            print("\n[실패 케이스]")
            for case, reason in fail_list:
                print(f"- {case}: {reason}")

    # -----------------------------
    # 실행
    # -----------------------------
    def run(self):
        print("=== Mini NPU Simulator ===")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")

        choice = input("선택: ").strip()

        if choice == '1':
            self.run_mode1()
        elif choice == '2':
            self.run_mode2()
        else:
            print("잘못된 입력입니다.")


# -----------------------------
# main
# -----------------------------
if __name__ == "__main__":
    sim = MiniNPUSimulator()
    sim.run()
