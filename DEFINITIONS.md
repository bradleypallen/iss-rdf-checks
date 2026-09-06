# Definitions → code

Every numbered definition of *Implication-Space Semantics for RDF* (6 Sept 2026
version) and where it is computed. The definition is quoted in the docstring of
the function named. Nothing in `issrdf/` uses a lemma of the paper; the two
places where a lemma or a pruning enters are listed at the end.

| Paper | Statement (short) | Code |
|---|---|---|
| Def. 1 | RDF triple; names I ∪ L, blank nodes B | a triple is a 3-tuple of strings; `issrdf.regime.is_bnode` (strings starting with `_`), `terms` |
| Def. 2 | RDF graph; instance mapping μ; ground instance; bnodes(G), names(G) | a graph is a `frozenset` of triples; `regime.inst`, `regime.bnodes`, `regime.names` |
| Def. 3 | Simple entailment: some μ with μ(H) ⊆ G | `regime.simply_entails` |
| Def. 4 | Entailment regime over V: range restriction, uniformity; cl_R; R-inconsistent; R-entails | rule schemas (Remark 5) as `(premises, conclusion)` with `BOT` = ⊥; `regime.make_closure` (cl_R), `regime.r_inconsistent`, `regime.r_entails` |
| Def. 5 | Bearers 𝔹, implication space S = 𝒫(𝔹) × 𝒫(𝔹), frame ⟨𝔹, 𝕀⟩ | a candidate implication is a pair of `frozenset`s of bearers; a frame is the membership function `good` (below) |
| Def. 6 | RSR, roles R(H), R⁺(a), R⁻(a); adjunction ⊔, symjunction ⊓, power-symjunction ∇; generating sets | `frame.rsr`; `roles.pos_role`, `roles.neg_role`, `roles.adj` / `adj_many`, `roles.symj`, `roles.nabla` |
| Def. 7 | Content entailment 𝔊 ⊨ 𝔇 iff ⋃(⊔g⁺ ⊔ ⊔d⁻) ⊆ 𝕀; implication-space model | `frame.iss_entails` (via Lemma 2, see below), `frame.iss_incoherent` for 𝔇 = ∅ |
| Def. 8 | Canonical frame 𝕀_C = overlapping pairs | the first test in `frame.make_good` |
| Def. 9 | Triples as bearers: 𝔅(t) = T⟨⟦s⟧, ⟦p⟧, ⟦o⟧⟩ | Herbrand: 𝔅 is the identity, so a triple is its own bearer (`roles.pos_role` / `neg_role`); `checks/check_theorem1.py::content_pairs` takes an arbitrary bearer map |
| Def. 10 | Content of a ground graph ⟨⊔ R⁺(t), ∇ R⁻(t)⟩ | `content.ground_content` |
| Def. 11 | Content of a blank-node graph ⟨∇{⟦μH⟧⁺}, ⊔{⟦μH⟧⁻}⟩, μ : bnodes(H) → N | `content.instances`, `content.content_pos`, `content.content_neg`, `content.content` |
| Conv. 1 | Finite vocabulary fragment N | `universe.Universe` (`N` = `INDIV + V + SPARE`) |
| Def. 12 | N admissible for G, H, R | `universe.Universe.admissible` |
| Def. 13 | Base; fitness; the base 𝓑_R specified by R: Γ ⊨ Δ iff Γ R-inconsistent or Δ ∩ cl_R(Γ) ≠ ∅ | the second test in `frame.make_good` |
| Def. 14 | Frame induced by a base, 𝕀_𝓑 = 𝕀_C ∪ {⟨𝔅Γ, 𝔅Δ⟩ : Γ ⊨_𝓑 Δ} | `frame.make_good` (the two tests together) |
| Def. 15 | Herbrand model: 𝔅 injective, every triple its own bearer | assumed throughout `issrdf`: pairs are built from triples directly |

Universe dependence. Only `make_closure` (reads `V`), `instances` and the
content functions (read `N`), the two entailment tests (through the contents),
and the random generators in `checks/generate.py` (read `INDIV`, `V`) take a
`Universe`. The algebra of roles, `ground_content`, `make_good`,
`simply_entails` and `r_entails` are universe-free.

## What is used beyond the definitions

| Where | What | Why it is allowed |
|---|---|---|
| `frame.iss_entails`, `frame.iss_incoherent` | Lemma 2: 𝔊 ⊨ 𝔇 can be checked on any generating set | Lemma 2 is checked numerically on random 3-bearer frames by `checks/check_recovery.py::check_lemma2`, using `frame.rsr` only |
| `checks/pruning.py` | Monotonicity of membership in 𝕀_R in both coordinates (a one-line consequence of Def. 13) | used by `check_recovery_2bn_fast.py`, `check_exhaustive.py`; not by `check_recovery.py` or `check_recovery_2bn.py`, which enumerate Lemma 3's pairs in full |
| `checks/check_owlrl.py` | Lemma 7's witness form on the negative side | documented in its docstring; owlrl is the closure oracle on both sides there |

## Negative controls (deliberately wrong, for showing the check can fail)

| Control | Code | What it breaks |
|---|---|---|
| Instances over N only | `make_closure(R, V, instances_over=U.N)` | the closure of Def. 4 (the slip of an earlier draft's Corollary 3) |
| Non-uniform regime | `make_closure(R, V, bnode_only=True)` | uniformity, Def. 4(2) |
| Undersized V | `check_owlrl.py` with V the hand list only | admissibility, Def. 12, and V ⊆ N in Def. 13 |
