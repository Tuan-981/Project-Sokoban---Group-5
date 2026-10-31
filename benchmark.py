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

    stats = dict(getattr(solution, "LAST_STATS", {}))
    if final is False:
        result = {"status": stats.get("status", "NOSOL"), "steps": None,
                  "time": elapsed, "valid": "-", **stats}
    else:
        valid, msg = validate_solution(initial, final)
        result = {"status": "SOLVED", "steps": final.gval, "time": elapsed,
                  "valid": valid, "msg": msg, **stats}
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


def to_markdown(maps, results):
    """Biến danh sách kết quả thành bảng Markdown."""
    lines = [
        "| Map | Trạng thái | Số bước | Thời gian (s) | Validate |",
        "|-----|------------|---------|---------------|----------|",
    ]
    for i, r in zip(maps, results):
        steps = "-" if r["steps"] is None else r["steps"]
        lines.append(f"| {i} | {r['status']} | {steps} | {r['time']:.2f} | {r['valid']} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=int)
    parser.add_argument("--timebound", type=float, default=30)
    parser.add_argument("--maps", type=int, nargs="*", help="chỉ chạy các map này")
    parser.add_argument("--md", action="store_true", help="in thêm bảng Markdown")
    parser.add_argument("--out", type=str, default=None, help="ghi bảng Markdown vào file này")
    args = parser.parse_args()

    
    if args.worker is not None:
        run_worker(args.worker, args.timebound)
        return


    maps = args.maps if args.maps else range(20)
    results = []

    # Tiêu đề bảng (in 1 lần, trước vòng lặp)
    print(f"{'Map':<5}{'Status':<9}{'Steps':>7}{'Expanded':>11}{'Generated':>11}{'Unique':>9}{'Time(s)':>10}  Valid")
    print("-" * 78)

    for i in maps:
        r = run_one(i, args.timebound)
        results.append(r)
        print(f"{i:<5}{r['status']:<9}{str(r['steps']):>7}"
              f"{r.get('expanded', '-'):>11}{r.get('generated', '-'):>11}"
              f"{r.get('unique', '-'):>9}{r['time']:>10.3f}  {r['valid']}",
              flush=True)
        if r["valid"] is False:
            print("      ->", r.get("msg", ""))
   
    counts = collections.Counter(r["status"] for r in results)
    print("-" * 78)
    print("Tong:", ", ".join(f"{k}={v}" for k, v in counts.items()))

    if args.md:
        md = to_markdown(maps, results)
        print()
        print(md)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(md + "\n")
            print("Da ghi:", args.out)
    
    


if __name__ == "__main__":
    main()    