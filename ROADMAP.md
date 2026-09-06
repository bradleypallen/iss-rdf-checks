# Roadmap

In priority order. Each item is meant to be one focused session. Items 1–3
change what a reader learns from the repository; 4–6 make it maintainable;
7 tracks the paper.

## 1. `walkthrough.py` — one example, end to end, everything printed

Goal: a first-time reader watches a single case happen on both sides.

- Regime: `{(X, rdf:type, Y), (Y, rdfs:subClassOf, Z)} → (X, rdf:type, Z)` plus
  a false-concluding rule, e.g. `{(X, type, Y), (X, type, Z), (Y, disjointWith, Z)} → ⊥`.
- Case A (ground): G = {(tweety, type, Bird), (Bird, subClassOf, Flier)},
  H = {(tweety, type, Flier)}.
- Case B (blank node in H): H = {(_:y, type, Flier)} — print the instance
  mappings, the ∇-pairs of ⟦H⟧⁻, the adjunction with ⟦G⟧⁺, and each pair's test
  against 𝕀_R with the reason ("(tweety, type, Flier) ∈ cl_R(Γ)").
- Case C (blank node in G): G = {(_:x, type, Bird), (Bird, subClassOf, Flier)} —
  print the instances ν(G) over N, and point at the Skolem instance
  ν(_:x) = s as the one that decides the only-if direction.
- Case D (incoherent): add (Bird, disjointWith, Flier); show ⊥ appearing in the
  closure and ⟦G⟧ ⊨ ∅ coming out true (Proposition 2).
- `--explain` prints every intermediate object; default prints the summary.
- Reuse the functions in `check_recovery.py`; do not reimplement.

## 2. `make_it_fail.py` — the controls, with reasons

Goal: show that the check can see errors.

- Run the Corollary 3 counterexample
  (G = {(_:x, type, C), (C, subClassOf, D)}, H = {(_:x, type, D)}) under
  (a) all instances and (b) instances over N only; print both verdicts on both
  sides and *why* they differ (the cax-sco instance at `_:x` is missing in (b)).
- Run a non-uniform regime (rules firing only for blank-node X) on a case where
  the rules say yes and the semantics says no; explain in terms of the missing
  ground instances.
- Run the owlrl check with an undersized V on a case that fails, then with the
  full V; explain in terms of admissibility (Def. 12).

## 3. Package structure mirroring the paper

Goal: the code ↔ definition map is visible in the file tree.

```
issrdf/
  regime.py    Defs 3–4: closure, simply_entails, r_entails, r_inconsistent
  roles.py     Def. 6 / Hlobil Def. 10: adj, adj_many, symj, nabla, pos_role, neg_role
  content.py   Defs 10–11: ground_content, instances, content_pos, content_neg
  frame.py     Defs 13–14: make_good (Herbrand), Lemma-2 style entailment test
  universe.py  V, INDIV, SPARE, N, BN_G, BN_H as an explicit Universe object
checks/        the seven scripts, importing from issrdf
DEFINITIONS.md table: every numbered definition → module.function, with the
                definition quoted in the docstring
```

Replace the module-global override pattern with an explicit `Universe` passed
to the functions. Do it in one commit, all scripts at once; verify every
`results/` number reproduces before merging.

## 4. Tests and CI

- `tests/test_examples.py`: tweety entails; clash is incoherent; Cor. 3
  counterexample agrees under all instances and disagrees under instances-over-N;
  Lemma 2 on a hand-built 4-element frame; ∇ of two singleton roles is the
  three-pair set {⟨a⟩, ⟨b⟩, ⟨a,b⟩} on the relevant coordinate.
- `tests/test_quick.py`: `check_recovery.py 1` with 100 cases, 0 mismatches;
  `check_exhaustive.py` on the five multi-rule regimes at size 2.
- GitHub Actions: pytest + the quick subset on push; badge in README.

## 5. `examples/` for the Semantic Web reader

- `tweety.ttl`, `tweety_query.ttl`, `clash.ttl` in Turtle.
- `run_owlrl_example.py`: load the Turtle, run owlrl materialize + ASK, run the
  semantics side, print both verdicts.

## 6. README reading order

Add at the top: plain-language account → `walkthrough.py` → `make_it_fail.py`
→ `issrdf/roles.py` and `content.py` → the check scripts → results table.
Move "What is computed from what" after the walkthrough.

## 7. Track the paper

- **Corollary 4 (ontology-relative regimes)** when it is written: add an
  `ontology` parameter to the closure (cl_{R_O}(X) = cl_R(X ∪ O)), rerun
  `check_exhaustive.py` and `check_owlrl.py` with a fixed ground O, and a
  Skolemized-ontology variant. Add the numbers to the README table.
- When the arXiv version exists: add the identifier to README and CITATION.cff.
- After TGDK acceptance: pin the definition numbering in CLAUDE.md to the
  published version.

## Not on the roadmap

- Performance work that trades independence for speed (see CLAUDE.md, "The one
  rule").
- A formal (Lean) proof — separate project.
- Mechanical extraction of Motik's OWL 2 RL/RDF tables to check Def. 4 clause by
  clause — worth doing, but it is a paper-side task, not a repository one.
