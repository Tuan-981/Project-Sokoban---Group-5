"""Benchmark Sokoban: mỗi map chạy trong một tiến trình mới có timeout."""
import argparse, json, subprocess, sys, time


def run_worker(index, timebound):
    """Chạy TRONG tiến trình con: giải map số index, in 1 dòng RESULT."""
    import solution
    from sokoban import PROBLEMS
    from validation import validate_solution

    initial = PROBLEMS[index]
    start = time.time()
    final = solution.solve(initial, timebound)
    elapsed = time.time() - start

    if final is False:
        result = {"status": "NOSOL", "steps": None, "time": elapsed, "valid": "-"}
    else:
        valid, msg = validate_solution(initial, final)
        result = {"status": "SOLVED", "steps": final.gval, "time": elapsed, "valid": valid, "msg": msg}
    print("RESULT " + json.dumps(result))


def run_one(index, timebound):
    """Chạy 1 map trong tiến trình con, trả về dict kết quả."""
    cmd = [sys.executable, __file__, "--worker", str(index),
           "--timebound", str(timebound)]
    start = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           errors="replace", timeout=timebound + 10)
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "steps": None,
                "time": time.time() - start, "valid": "-"}
    
    for line in p.stdout.splitlines():
        if line.startswith("RESULT "):
            return json.loads(line[len("RESULT "):])
    # Không thấy dòng RESULT: worker đã chết trước khi in
    print(p.stderr[-300:])
    return {"status": "CRASH", "steps": None, "time": time.time() - start,
            "valid": "-", "msg": ""}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=int)
    parser.add_argument("--timebound", type=float, default=30)
    parser.add_argument("--maps", type=int, nargs="*", help="chỉ chạy các map này")
    args = parser.parse_args()

    if args.worker is not None:
        run_worker(args.worker, args.timebound)
        return

    
    # TODO: lấy danh sách chỉ số map (mặc định range(20)), gọi run_one cho từng map,
    #       in một hàng ngay sau mỗi map (đừng đợi chạy hết mới in)
    # TODO: in tiêu đề bảng: Map | Trạng thái | Số bước | Thời gian | Validate


    maps = args.maps if args.maps else range(20)
    results = []

    # Tiêu đề bảng (in 1 lần, trước vòng lặp)
    print(f"{'Map':<6}{'Trang thai':<10}{'So buoc':>8}{'Thoi gian':>11}  Validate")
    print("-" * 50)

    for i in maps:
        r = run_one(i, args.timebound)
        results.append(r)
        print(f"{i:<6}{r['status']:<10}{str(r['steps']):>8}{r['time']:>10.2f}s  {r['valid']}",
              flush=True)
    # TODO: cuối bảng in tổng: bao nhiêu map SOLVED / NOSOL / TIMEOUT / CRASH
    print(collections.Counter([r["status"] for r in results]))
    


if __name__ == "__main__":
    main()    