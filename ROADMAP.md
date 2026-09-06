# Roadmap

Each numbered item is one focused session. The order is the execution order:
the package refactor (item 1) comes first so that the notebooks (items 2, 3, 5)
are written once, against `issrdf`, rather than against the module-global
override pattern and then rewritten. Items 1–3 change what a reader learns from
the repository; 4–6 make it maintainable; 7 tracks the paper.

Conventions that apply throughout:

- Examples, tutorials and walkthroughs are Jupyter notebooks under
  `notebooks/`, committed with executed outputs and re-executed in CI. They
  import from `issrdf` and never reimplement a definition. The check scripts in
  `checks/` stay plain, standard-library Python.
- Every run — script, notebook or test — writes a plain-text summary to
  `results/`, in the existing one-line style, so that directory remains the
  single ledger for post-run analysis. CI uploads executed notebooks and logs
  as build artifacts.
- Nothing in `issrdf/` may use a lemma of the paper (CLAUDE.md, "The one
  rule"). The two monotonicity prunings live outside the package, in
  `checks/pruning.py`.

## 0. Baseline (before any code change)

- A virtual environment with `rdflib` and `owlrl` pinned to the versions the
  logs in `results/` were produced with (owlrl 7.6).
- `tools/compare_logs.py`: diff a fresh log against the matching file in
  `results/`, ignoring timing lines.
- Rerun the quick subset and confirm every log reproduces on this machine.
  This establishes that the runs are deterministic, which the refactor
  verification in item 1 relies on.
- Tag the commit (`baseline`).

Outcome (6 Sept 2026): all 15 standard-library and rdflib logs reproduce line
for line. The three OWL logs reproduce in every verdict-bearing number
(`cases`, `entail`, `inconsistent`, `bnG`, `mismatch`, `timeout`,
`owlrl_crash`) but not in `bnH`, and one TIMEOUT line shows a different H.
Cause, confirmed by probe: when H is sampled from owlrl's closure of G,
`check_owlrl.py` iterates the rdflib graph, whose order depends on
`PYTHONHASHSEED`, so `rng.sample` sees a differently ordered pool. The
reference logs were made under an unknown hash seed. `tools/reproduce.sh`
now pins `PYTHONHASHSEED=0` for OWL runs so future reruns agree with each
other. The proper fix — sort the pool by string before sampling — changes the
random stream and therefore the logs, so it is scheduled for item 1 with a
rerun. Also noticed: the README's OWL row says 742 cases, but the three logs
sum to 197 + 196 + 199 = 592 (the 197 inconsistent and 8 skipped do match);
correct it in the same rerun.

## 1. Package structure mirroring the paper

Goal: the code ↔ definition map is visible in the file tree.

```
issrdf/
  universe.py  Convention 1 / Def. 12: V, INDIV, SPARE, N, BN_G, BN_H as an
               explicit Universe object, with an `admissible(G, H)` check
  regime.py    Defs 3–4: closure, simply_entails, r_entails, r_inconsistent
  roles.py     Def. 6 / Hlobil Def. 10: adj, adj_many, symj, nabla, pos_role, neg_role
  content.py   Defs 10–11: ground_content, instances, content_pos, content_neg
  frame.py     Defs 8, 13–15: make_good (Herbrand), Lemma-2 style entailment
               test, and the RSR helper used to check Lemma 2 numerically
  show.py      display helpers for the notebooks (pretty-print generating sets,
               the reason a pair lies in I_R); no computation of its own
checks/        the seven scripts, importing from issrdf; pruning.py holds
               pos_singletons and neg_minimal with the monotonicity argument
DEFINITIONS.md table: every numbered definition → module.function, with the
               definition quoted in the docstring
```

Design points:

- Only five functions read the universe: the closure and regime generator
  read `V`; the graph generator reads `INDIV` and `V`; `instances` and the two
  content functions read `N`. The algebra (adjunction, symjunction, ∇, roles,
  ground content, the frame test, simple and `R`-entailment) is universe-free.
  Say so in DEFINITIONS.md.
- `admissible(G, H)` is a method, not a constructor assertion: the Theorem 1
  check runs with no spare IRI, legitimately, since Theorem 1 does not assume
  Definition 12. The closure-regime checks call it.
- Keep the order of random-number calls byte for byte so seeds reproduce.
- Each check keeps a two-line path bootstrap so `python3 check_x.py 1` from
  `checks/` works without installing anything.
- `check_exhaustive.py` builds its graph lists at import time from `argv`;
  wrap that in a `main(which, maxsize)` so the tests in item 4 can call it.
- `check_owlrl.py` does not import the core module. The one change to make
  is to sort the closure pool by string before H is sampled from it, so the
  run is independent of `PYTHONHASHSEED` (see item 0). That changes the OWL
  logs: rerun `owl_2`, `owl_3`, `owl_4` and the RDFS run, replace them in
  `results/`, and fix the README's OWL case count at the same time.

Outcome (6 Sept 2026): done in one commit. All 15 stdlib/rdflib logs
reproduce exactly (`tools/compare_logs.py`). `check_owlrl.py` now sorts the
pool by string; the OWL logs were regenerated (same 592 cases, 197
inconsistent, 8 skipped; `bnH` and one `entail` count moved with the
re-sampled H) and verified identical under three hash seeds; `rdfs_1.txt`
added (300 cases, 0 mismatches). README's OWL row corrected to 592 cases.

Do it in one commit, all scripts at once. Before merging, rerun `run_1–5`,
`fast_1–4`, `exhaustive_2`, `exhaustive_3_multi`, `theorem1` (2 and 3
bearers), `run2bn_4`, `run2bn_9` and `lemma1`, and verify every number with
`tools/compare_logs.py`. The OWL runs are rerun for the pool-order fix above.

## 2. `notebooks/01_walkthrough.ipynb` — one example, end to end

Goal: a first-time reader watches a single case happen on both sides.

- Universe: `V` = {`type`, `subClassOf`, `disjointWith`}, individuals
  {`tweety`, `Bird`, `Flier`}, one spare IRI `s`; so `N` has 7 names.
- Regime: rdfs9 `{(X, type, Y), (Y, subClassOf, Z)} → (X, type, Z)` plus the
  clash rule cax-dw `{(X, type, Y), (X, type, Z), (Y, disjointWith, Z)} → ⊥`,
  named as in the paper (question 2 and Remark 6).
- Case A (ground): G = {(tweety, type, Bird), (Bird, subClassOf, Flier)},
  H = {(tweety, type, Flier)}.
- Case B (blank node in H): H = {(_:y, type, Flier)} — print the 7 instance
  mappings, ⟦H⟧⁻ (one pair whose succedent holds all 7 instances), the
  adjunction with ⟦G⟧⁺, and the pair's test against 𝕀_R with the reason
  ("(tweety, type, Flier) ∈ cl_R(Γ)").
- Case C (blank node in G): G = {(_:x, type, Bird), (Bird, subClassOf, Flier)}
  — print the 7 instances ν(G) and the 127 generating pairs of ⟦G⟧⁺. Run it
  against both H's: the ground H of case A, where the verdict is *no* and the
  Skolem instance ν_sk(_:x) = s (Lemma 5, Remark 9) is the failing witness,
  the pair being the one Lemma 7's only-if direction constructs; and the
  blank-node H of case B, where the verdict is *yes*.
- Case D (incoherent): add (Bird, disjointWith, Flier); show ⊥ appearing in
  the closure and ⟦G⟧ ⊨ ∅ coming out true (Proposition 2).
- One markdown cell per case, then the code cell, then the printed objects.
  A notebook is always the explained version; the summary is the last cell,
  which also writes `results/walkthrough.txt`.
- Display helpers go in `issrdf/show.py`; the notebook computes nothing itself.

Outcome (6 Sept 2026): `notebooks/01_walkthrough.ipynb`, 16 cells, cases A,
B, C1, C2, D plus two comparisons (the consistent G is not incoherent;
the incoherent G entails an unrelated H). Executed outputs committed;
identical across executions under different hash seeds; passes `pytest
--nbmake`. `issrdf/show.py` added, and `content.mappings` factored out of
`instances` (logs unchanged). Writes `results/walkthrough.txt`.

## 3. `notebooks/02_make_it_fail.ipynb` — the controls, with reasons

Goal: show that the check can see errors. Three sections, each with a verdict
table (both sides, both configurations) followed by the explanation.

- The Corollary 3 counterexample (G = {(_:x, type, C), (C, subClassOf, D)},
  H = {(_:y, type, D)} — H's blank node gets its own name, and the notebook
  says why) under (a) all instances and (b) instances over `N` only; both
  verdicts on both sides and *why* they differ (the cax-sco instance at `_:x`
  is missing in (b)).
- A hand-crafted non-uniform regime: a single rule from `Bird` to `Flier`
  that fires only for blank-node subjects, G = {(_:x, type, Bird)},
  H = {(_:y, type, Flier)}. Rules say yes, semantics says no; explain in terms
  of the ground instances, which the rule never sees.
- The owlrl check with an undersized `V` on a case that fails, then with the
  full `V`; explain by Definition 12 and the sentence in Definition 13 that
  `V ⊆ N` ensures no rule instance is excluded by the restriction to `N`.
  Find the smallest failing case beforehand with a logged scratch search;
  only the found case goes in the notebook. The section skips cleanly when
  owlrl is not installed.
- Last cell writes `results/make_it_fail.txt`.

Outcome (6 Sept 2026): `notebooks/02_make_it_fail.ipynb`, 10 cells, six
verdict rows (1a/1b, 2/2', 3 hand-listed V / 3 V_full); the three
disagreements are in the predicted directions and each restored hypothesis
restores agreement. Section 2 also prints the failing instance of Lemma 6.
The RDFS profile adds nothing to the empty graph, so the undersized-V
failure is OWL-only; the search (`results/undersized_V_search.txt`, 120
cases, 1 mismatch) minimized to G = ∅, H = {(owl:deprecated, type, _:y)},
whose witness owl:AnnotationProperty is outside the hand list. The
natural-looking variants ("something is an AnnotationProperty / Datatype")
agree because the hand list happens to contain a witness. Executed outputs
identical across hash seeds; passes nbmake; the owlrl section prints a skip
line under a Python without owlrl (tested).

## 4. Tests and CI

- `tests/test_examples.py`: tweety entails; clash is incoherent; Cor. 3
  counterexample agrees under all instances and disagrees under
  instances-over-`N`; Lemma 2 on a hand-built 4-element frame; ∇ of two
  singleton roles is the three-pair set {⟨a⟩, ⟨b⟩, ⟨a,b⟩} on the relevant
  coordinate; `N`-independence — the paragraph after Theorem 2 says the
  verdict is the same for every admissible `N`, so the same case with one
  spare IRI and with two must agree.
- `tests/test_quick.py`: `check_recovery` with 4 regimes × 25 pairs = 100
  cases, 0 mismatches; `check_exhaustive` on the five multi-rule regimes at
  size 2 (about 4 s).
- GitHub Actions, two jobs: a standard-library job (pytest + the quick
  subset) and a full job (rdflib, owlrl, notebook toolchain; pytest plus
  `nbmake` over `notebooks/`, uploading executed notebooks and `results/`
  logs as artifacts). Badge in README.
- A second requirements file for the notebook and test toolchain, so
  `requirements.txt` keeps saying that the checks need only rdflib and owlrl.

Outcome (6 Sept 2026): `tests/test_examples.py` (8 tests, including
N-independence and an exhaustive Lemma 2 over all generating sets of at
most two candidates on a 2-bearer frame) and `tests/test_quick.py` (6
quick subsets, two of them skipping without rdflib/owlrl); 14 pass in ~5 s.
`run()` in the check scripts now returns its statistics (logs unchanged,
spot-checked). `tests/conftest.py` writes `results/tests.txt`, one
deterministic line per test, skipped on partial (`-k`) runs.
`.github/workflows/checks.yml`: a stdlib job on Python 3.10 and 3.12 and a
full job that also runs nbmake and uploads the executed notebooks and
logs. Badge in README. The non-uniform control fires 0 times in the
100-case quick run, so only the over-N control is asserted there.

## 5. `examples/` and `notebooks/03_owlrl_example.ipynb`

- `examples/tweety.ttl`, `examples/tweety_query.ttl`, `examples/clash.ttl` in
  Turtle.
- The notebook loads the Turtle with rdflib, maps terms to the short-name
  convention, runs owlrl materialize + ASK under OWL 2 RL semantics (the RDFS
  profile has no disjointness rule) and the semantics side from the
  definitions with the walkthrough's regime, and prints both verdicts side by
  side for the entailment case and the clash case. Last cell writes
  `results/owlrl_example.txt`.

Outcome (6 Sept 2026): four Turtle files (a blank-node query added) and
`notebooks/03_owlrl_example.ipynb`, 10 cells, five cases (ground query,
blank-node query, non-entailed query, the clash under Proposition 2, and
explosion from the clash); all agree. rdflib gives blank nodes a random
label per parse, so the term conversion renames them `_x`, `_y`, ... in
order of appearance; outputs are identical across hash seeds. The notebook
says explicitly that its semantics' side uses the two-rule fragment and
that the full rule set's agreement is `check_owlrl.py`'s business. Passes
nbmake with the other two; prints a skip line without rdflib/owlrl.

## 6. README reading order

Add at the top: plain-language account → `notebooks/01_walkthrough.ipynb` →
`notebooks/02_make_it_fail.ipynb` → `notebooks/03_owlrl_example.ipynb` →
`issrdf/roles.py` and `content.py` → the check scripts → results table.
Link each notebook by its GitHub path so it renders in place. Move "What is
computed from what" after the walkthrough. Update the layout block for
`issrdf/`, `notebooks/`, `tests/`, `examples/` and `tools/`.

## 7. Track the paper

- **Corollary 4 (ontology-relative regimes)** when it is written: add an
  `ontology` parameter to the closure (cl_{R_O}(X) = cl_R(X ∪ O)). By range
  restriction (Def. 4, clause 1) a rule ⟨∅, t⟩ needs names(t) ⊆ V, so the
  regime's vocabulary is V ∪ names(O) and by Def. 12 those names must lie in
  `N`; the parameter extends `V` itself rather than leaving it to the caller.
  Rerun `check_exhaustive.py` and `check_owlrl.py` with a fixed ground O, and
  a Skolemized-ontology variant whose fresh IRIs enter `V` the same way. Add
  the numbers to the README table. Hold the reruns until the corollary's
  statement is fixed.
- When the arXiv version exists: add the identifier to README and CITATION.cff.
- After TGDK acceptance: pin the definition numbering in CLAUDE.md to the
  published version.

## Not on the roadmap

- Performance work that trades independence for speed (see CLAUDE.md, "The one
  rule").
- A formal (Lean) proof — separate project.
- Mechanical extraction of Motik's OWL 2 RL/RDF tables to check Def. 4 clause by
  clause — worth doing, but it is a paper-side task, not a repository one.
