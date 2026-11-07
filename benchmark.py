"""Benchmark Sokoban: mỗi map chạy trong một tiến trình mới có timeout."""
import argparse, collections, json, os, subprocess, sys, time 


def load_maps(set_name):
    """Trả về danh sách trạng thái đầu của bộ map được chọn."""
    if set_name == "custom":
        from custom_maps import MAPS
        return [state for _, state, _ in MAPS]
    from sokoban import PROBLEMS
    return list(PROBLEMS)

def load_meta(set_name):
    """Tên map và số bước mong đợi (chỉ có ở bộ custom), ngược lại trả None."""
    if set_name == "custom":
        from custom_maps import MAPS
        return [(name, expected) for name, _, expected in MAPS]
    return None


def so_sanh(expected, r):
    """Đối chiếu kết quả với số bước mong đợi (chỉ dùng cho bộ custom).
    expected = None nghĩa là map vô nghiệm."""
    if r["status"] == "CRASH":
        return "LỖI: crash"
    if r["status"] == "TIMEOUT":
        return "không kết luận"            # hết giờ: chưa biết đúng hay sai
    if r["valid"] is False:
        return "LỖI: lời giải sai"
    if expected is None:                   # map vô nghiệm: không tính hiệu số
        if r["steps"] is None:
            return "khớp vô nghiệm"
        return "BẤT THƯỜNG: tìm được nghiệm"
    if r["steps"] is None:
        return "KHÔNG KHỚP: không giải được"
    hieu = r["steps"] - expected
    return "khớp" if hieu == 0 else f"lệch {hieu:+d}"


def run_worker(index, timebound, solver, map_set):
    """Chạy TRONG tiến trình con: giải map số index, in 1 dòng RESULT."""
    import importlib
    solution = importlib.import_module(solver)
    from validation import validate_solution

    initial = load_maps(map_set)[index]
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


def run_one(index, timebound, solver, map_set):
    """Chạy 1 map trong tiến trình con, trả về dict kết quả."""
    cmd = [sys.executable, __file__, "--worker", str(index),
           "--timebound", str(timebound), "--solver", solver, "--set", map_set]
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

def to_markdown(maps, results, meta=None):
    """Bảng Markdown căn cột. meta (chỉ bộ custom): danh sách (tên, số bước mong đợi)."""
    cot = [("Map", False)]
    if meta:
        cot.append(("Name", False))
    cot += [("Status", False), ("Steps", True)]
    if meta:
        cot += [("Expected", False), ("Check", False)]
    cot += [("Expanded", True), ("Generated", True), ("Unique", True),
            ("Time (s)", True), ("Valid", False)]
    header = [ten for ten, _ in cot]
    right = {c for c, (_, phai) in enumerate(cot) if phai}

    rows = []
    for i, r in zip(maps, results):
        steps = "-" if r["steps"] is None else r["steps"]
        row = [str(i)]
        if meta:
            row.append(meta[i][0])
        row += [str(r["status"]), str(steps)]
        if meta:
            exp = meta[i][1]
            row += ["vô nghiệm" if exp is None else str(exp), so_sanh(exp, r)]
        row += [str(r.get("expanded", "-")), str(r.get("generated", "-")),
                str(r.get("unique", "-")), f"{r['time']:.3f}", str(r["valid"])]
        rows.append(row)

    widths = [max([len(header[c])] + [len(row[c]) for row in rows])
              for c in range(len(header))]

    def fmt(cells):
        out = [cell.rjust(widths[c]) if c in right else cell.ljust(widths[c])
               for c, cell in enumerate(cells)]
        return "| " + " | ".join(out) + " |"

    sep = ["-" * (widths[c] - 1) + ":" if c in right else "-" * widths[c]
           for c in range(len(header))]
    lines = [fmt(header), "| " + " | ".join(sep) + " |"]
    lines += [fmt(row) for row in rows]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=int)
    parser.add_argument("--timebound", type=float, default=30)
    parser.add_argument("--maps", type=int, nargs="*", help="chỉ chạy các map này")
    parser.add_argument("--md", action="store_true", help="in thêm bảng Markdown")
    parser.add_argument("--out", type=str, default=None, help="ghi bảng Markdown vào file này")
    parser.add_argument("--solver", type=str, default="solution")
    parser.add_argument("--set", dest="map_set", choices=["problems", "custom"],
                        default="problems", help="bộ map: problems (20 map của thầy) hoặc custom")
    args = parser.parse_args()

    
    if args.worker is not None:
        run_worker(args.worker, args.timebound, args.solver, args.map_set)
        return


    maps = args.maps if args.maps else range(len(load_maps(args.map_set)))
    results = []

    # Tiêu đề bảng (in 1 lần, trước vòng lặp)
    print(f"{'Map':<5}{'Status':<9}{'Steps':>7}{'Expanded':>11}{'Generated':>11}{'Unique':>9}{'Time(s)':>10}  Valid")
    print("-" * 78)

    for i in maps:
        r = run_one(i, args.timebound, args.solver, args.map_set)
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

    md = to_markdown(maps, results, load_meta(args.map_set)) if (args.md or args.out) else None
    if args.md:
        print()
        print(md)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md + "\n")
        print("Da ghi:", args.out)
    
    


if __name__ == "__main__":
    main()    