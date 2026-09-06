#!/usr/bin/env bash
# Quick reproduction of the machine checks (a few minutes). The slow runs
# (check_exhaustive.py multi 3, check_owlrl.py ... owl 200, check_theorem1.py 1 3)
# are listed in README.md.
set -e
cd "$(dirname "$0")/checks"
python3 check_recovery.py 1
python3 check_recovery_2bn_fast.py 1
python3 check_exhaustive.py all
python3 check_theorem1.py 1 2
if python3 -c "import rdflib, owlrl" 2>/dev/null; then
  python3 check_lemma1.py 1
  python3 check_owlrl.py 1 rdfs 100
else
  echo "rdflib/owlrl not installed; skipping check_lemma1.py and check_owlrl.py (pip install rdflib owlrl)"
fi
