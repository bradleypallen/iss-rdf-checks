#!/usr/bin/env bash
# Reproduce the logs in results/ into a directory, one file per reference log,
# using the same commands (see README "Reproducing"). Then compare with
#     python3 tools/compare_logs.py <outdir>
#
# Usage:  tools/reproduce.sh <outdir> [quick|stdlib|owl|all]
#   quick  : everything under ~2 min each (run_*, fast_*, exhaustive_2, theorem1
#            2-bearer rows, run2bn_*, lemma1)                       [default]
#   full   : quick plus exhaustive_3_multi and the theorem1 3-bearer row
#   owl    : the three check_owlrl.py OWL runs (~7 min each). Run these on an
#            otherwise idle machine: the 30 s per-case timeout is wall-clock,
#            so CPU contention can change the recorded timeout count.
#            PYTHONHASHSEED is pinned for these: check_owlrl.py samples H from
#            an rdflib graph whose iteration order is hash-seed dependent, so
#            without the pin the bnH counter (not the verdicts) varies.
#   all    : full, then owl
# Runs are launched in parallel (one process per log) and waited for.
# Each log is written when its run completes; a *.err file holds stderr.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$(mkdir -p "$1" && cd "$1" && pwd)"; MODE="${2:-quick}"
PY="${PYTHON:-$ROOT/.venv/bin/python}"; [ -x "$PY" ] || PY=python3
cd "$ROOT/checks"
run() { local log="$1"; shift; ( "$PY" "$@" > "$OUT/$log" 2> "$OUT/${log%.txt}.err" ) & }
echo "python: $PY  mode: $MODE  out: $OUT"
if [ "$MODE" != owl ]; then
  for s in 1 2 3 4 5; do run run_$s.txt check_recovery.py $s; done
  for s in 1 2 3 4; do run fast_$s.txt check_recovery_2bn_fast.py $s; done
  for s in 4 9; do run run2bn_$s.txt check_recovery_2bn.py $s; done
  run exhaustive_2.txt check_exhaustive.py all
  run lemma1.txt check_lemma1.py 1
  if [ "$MODE" = full ] || [ "$MODE" = all ]; then
    run exhaustive_3_multi.txt check_exhaustive.py multi 3
    ( { "$PY" check_theorem1.py 1 2; "$PY" check_theorem1.py 2 2; "$PY" check_theorem1.py 1 3; } \
        > "$OUT/theorem1.txt" 2> "$OUT/theorem1.err" ) &
  else
    ( { "$PY" check_theorem1.py 1 2; "$PY" check_theorem1.py 2 2; } \
        > "$OUT/theorem1.txt" 2> "$OUT/theorem1.err" ) &
  fi
fi
wait
if [ "$MODE" = owl ] || [ "$MODE" = all ]; then
  export PYTHONHASHSEED=0
  for s in 2 3 4; do run owl_$s.txt check_owlrl.py $s owl 200; done
  wait
fi
echo "done: $(ls "$OUT"/*.txt | wc -l | tr -d ' ') logs in $OUT"
