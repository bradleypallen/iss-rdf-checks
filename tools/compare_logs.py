"""Compare freshly produced logs against the reference logs in results/.

Usage:  python3 tools/compare_logs.py <fresh_dir> [<reference_dir>]

Every *.txt in <fresh_dir> is compared line by line with the file of the same
name in <reference_dir> (default: results/), after normalizing away everything
that legitimately varies between runs:

  * trailing per-regime timings such as ", 138s" or "} 386s";
  * the `real`/`user`/`sys` lines printed by `time`.

Nothing else is ignored: counts, examples, TIMEOUT lines and crash counters
must all match. Prints one line per file and exits non-zero on any difference,
so it can gate a commit. The differing lines are shown, which is the
post-run analysis a refactor needs.
"""
import re, sys, pathlib

TIMING = re.compile(r'[,}]?\s*\d+s$')
TIME_LINES = re.compile(r'^(real|user|sys)\s')

def normalize(text):
    out = []
    for line in text.splitlines():
        if TIME_LINES.match(line):
            continue
        line = TIMING.sub(lambda m: '}' if m.group(0).lstrip().startswith('}') else '', line.rstrip())
        out.append(line.rstrip())
    while out and not out[-1]:
        out.pop()
    return out

def main(fresh, ref):
    fresh, ref = pathlib.Path(fresh), pathlib.Path(ref)
    files = sorted(fresh.glob('*.txt'))
    if not files:
        print(f"no *.txt in {fresh}"); return 2
    bad = 0
    for f in files:
        r = ref / f.name
        if not r.exists():
            print(f"{f.name:24s} NO REFERENCE"); bad += 1; continue
        a, b = normalize(f.read_text()), normalize(r.read_text())
        if a == b:
            print(f"{f.name:24s} ok ({len(a)} lines)")
        else:
            bad += 1
            print(f"{f.name:24s} DIFFERS")
            for i, (x, y) in enumerate(zip(a, b)):
                if x != y:
                    print(f"  line {i+1}:\n    fresh: {x}\n    ref:   {y}")
            if len(a) != len(b):
                print(f"  length: fresh {len(a)} lines, ref {len(b)} lines")
    print(f"{len(files) - bad}/{len(files)} logs reproduce")
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'results'))
