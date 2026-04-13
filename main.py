import json
import time
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
                "cross_5_1": {"input": cross(5), "expected": "+"},
                "x_5_1": {"input": x(5), "expected": "x"},
                "cross_13_1": {"input": cross(13), "expected": "cross"},
                "x_13_1": {"input": x(13), "expected": "x"},
                "cross_25_1": {"input": cross(25), "expected": "+"},
                "x_25_1": {"input": x(25), "expected": "+"},
            }
        }

        with open("data.json", "w") as f:
            json.dump(data, f, indent=2)

        print("[알림] data.json 자동 생성 완료")

    # -----------------------------
    def normalize_label(self, label):
        label = str(label).lower().strip()
        if label in ['+', 'cross']:
            return "Cross"
        elif label == 'x':
            return "X"
        return label

    # -----------------------------
    def mac_operation(self, m1, m2):
        total = 0.0
        for i in range(m1.size):
            for j in range(m1.size):
                total += m1.get_value(i, j) * m2.get_value(i, j)
        return total

    # -----------------------------
    def measure_time(self, m1, m2, repeat=10):
        start = time.time()
        for _ in range(repeat):
            self.mac_operation(m1, m2)
        end = time.time()
        return ((end - start) / repeat) * 1000

    # -----------------------------
    def build_matrix(self, raw, n):
        m = Matrix(n)
        for i in range(n):
            for j in range(n):
                m.set_value(i, j, float(raw[i][j]))
        return m

    # -----------------------------
    def performance(self, filters):
        print("\n[성능 분석]")
        print("크기\t시간(ms)\t연산수")

        for n in [5, 13, 25]:
            key = f"cross_{n}"
            if key not in filters:
                continue

            m = self.build_matrix(filters[key], n)
            t = self.measure_time(m, m)

            print(f"{n}x{n}\t{t:.6f}\t{n*n}")

    # -----------------------------
    def run(self):
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

            # 크기 추출
            match = re.search(r'\d+', key)
            if not match:
                print("FAIL: 키 파싱 실패")
                failed += 1
                fail_list.append((key, "키 파싱 실패"))
                continue

            n = int(match.group())

            # 필터 존재 확인
            if f"cross_{n}" not in filters or f"x_{n}" not in filters:
                print("FAIL: 필터 없음")
                failed += 1
                fail_list.append((key, "필터 없음"))
                continue

            pattern_raw = content.get("input", [])
            expected = self.normalize_label(content.get("expected"))

            # 크기 검증
            if len(pattern_raw) != n:
                print("FAIL: 크기 불일치")
                failed += 1
                fail_list.append((key, "크기 불일치"))
                continue

            try:
                cross = self.build_matrix(filters[f"cross_{n}"], n)
                x = self.build_matrix(filters[f"x_{n}"], n)
                p = self.build_matrix(pattern_raw, n)
            except Exception as e:
                print(f"FAIL: 데이터 오류 ({e})")
                failed += 1
                fail_list.append((key, "데이터 구조 오류"))
                continue

            # MAC 연산
            cs = self.mac_operation(cross, p)
            xs = self.mac_operation(x, p)

            # epsilon 비교
            if abs(cs - xs) < self.epsilon:
                pred = "UNDECIDED"
            elif cs > xs:
                pred = "Cross"
            else:
                pred = "X"

            # PASS / FAIL
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
if __name__ == "__main__":
    sim = MiniNPUSimulator()
    sim.run()
