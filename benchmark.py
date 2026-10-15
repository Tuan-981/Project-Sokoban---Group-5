"""Benchmark Sokoban: mỗi map chạy trong một tiến trình mới có timeout."""
import argparse, collections, json, os, subprocess, sys, time


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
                           errors="replace", timeout=timebound + 10,
                           cwd=os.path.dirname(os.path.abspath(__file__)))
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
        if r["valid"] is False:
            print("      ->", r.get("msg", ""))
   
    counts = collections.Counter(r["status"] for r in results)
    print("-" * 50)
    print("Tong:", ", ".join(f"{k}={v}" for k, v in counts.items()))
    
    


if __name__ == "__main__":
    main()    