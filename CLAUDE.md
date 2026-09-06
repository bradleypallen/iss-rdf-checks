# CLAUDE.md — context for working on this repository

This repository is the companion code for Bradley P. Allen, *Implication-Space
Semantics for RDF* (working paper, University of Amsterdam, Sept 2026; target
venue TGDK special issue "Rules and Reasoning for Graph-Based Data & Knowledge",
deadline 14 Dec 2026). The paper gives RDF an inferentialist semantics in the
implication-space framework of Hlobil & Brandom, *Reasons for Logic, Logic for
Reasons* (Routledge 2025) and Hlobil, "First-Order Implication-Space Semantics",
*J. Phil. Logic* 55(3):529–554 (2026). The code checks the paper's theorems by
computation. It is evidence, not proof; the proofs are in the paper.

## The one rule

**The semantics side must be computed from the paper's definitions only, never
from its lemmas.** The whole value of the check is that the two sides are
independent. In particular:

- Do not replace `nabla`/`adj_many` with a closed form of the generating pairs
  (that is Lemma 3 — using it would make the check circular).
- Do not decide content entailment by "some instance mapping μ has μ(H) ⊆
  cl_R(ν(G))" on the *unpruned* paths (that is Lemma 7's proof). The pruned
  paths (`check_recovery_2bn_fast.py`, `check_exhaustive.py`, `check_owlrl.py`)
  use exactly two facts and must not use more — see "Pruning" below.
- `check_recovery.py` and `check_recovery_2bn.py` must stay unpruned.

If a refactor makes a check faster by making it less independent, it is wrong.

## What the paper proves (numbering of the 6 Sept 2026 ROLE version)

- **Def. 3** simple entailment: G simply entails H iff some instance mapping
  μ : bnodes(H) → I ∪ B ∪ L has μ(H) ⊆ G. (Generalized RDF: any term in any
  position.)
- **Def. 4** entailment regime R over vocabulary V ⊆ I: rules ⟨A, c⟩, A finite
  set of triples, c a triple or ⊥; *range restriction* (names of c occur in A
  or V); *uniformity* (closed under every map ρ on I ∪ B ∪ L fixing L ∪ V
  pointwise, with ρ(⊥)=⊥). cl_R(X) least superset closed under R.
  X is *R-inconsistent* iff ⊥ ∈ cl_R(X). G *R-entails* H iff G is
  R-inconsistent or cl_R(G)∖{⊥} simply entails H.
- **Def. 6** (Hlobil 2026 Defs 5–10): RSR, roles 𝓡(H) as RSR-classes;
  adjunction ⊔ = coordinatewise union of one pair from each generating set;
  symjunction ⊓ = union of generating sets; power-symjunction
  ∇X = ⊓{⊔x : ∅≠x⊆X}. Roles are handled by *generating sets of pairs*.
- **Def. 7** content entailment: 𝔊 ⊨ 𝔇 iff ⋃(⊔g⁺ ⊔ ⊔d⁻) ⊆ 𝕀. With Lemma 2
  (checked numerically in `check_recovery.py::check_lemma2`) this is: every
  pair of a generating set of ⟦G⟧⁺ ⊔ ⟦H⟧⁻ lies in 𝕀.
- **Def. 10** ground graph content ⟦G⟧ = ⟨⊔{𝓡⁺(t)}, ∇{𝓡⁻(t)}⟩.
- **Def. 11** blank-node graph content ⟦H⟧ = ⟨∇{⟦μH⟧⁺ : μ}, ⊔{⟦μH⟧⁻ : μ}⟩,
  μ ranging over bnodes(H) → N. (Hlobil's derived ∃-clause with instances
  over N in place of objects.)
- **Def. 12** N is admissible for G, H, R iff names(G) ∪ names(H) ∪ V ⊆ N and
  there is an injection bnodes(G) → IRIs of N ∖ (names(G) ∪ names(H) ∪ V).
  **This is why `SPARE` exists and why V must be complete** (an undersized V
  produced the only mismatches ever seen — see README "lessons").
- **Def. 13** base 𝓑_R over N: Γ ⊨ Δ iff Γ R-inconsistent or Δ ∩ cl_R(Γ) ≠ ∅
  (ground triples over N).
- **Def. 14** frame 𝕀_R = 𝕀_C ∪ {⟨𝔅Γ, 𝔅Δ⟩ : Γ ⊨_{𝓑_R} Δ}, 𝕀_C = overlapping
  pairs. Herbrand model: 𝔅 = identity on triples.
- **Theorem 1** (Recovery): G ⊨^{b_𝓑} H in every fit model iff G ⊨ H in the
  Herbrand model over 𝓑. (Any base, no monotonicity/Cut assumed.)
- **Lemma 7 / Theorem 2** (Closure regimes): G ⊨^{b_R} H iff G R-entails H.
- **Proposition 2** (Incoherence recovery): ⟦G⟧ ⊨ ∅ iff G is R-inconsistent.
- **Cor. 1–3**: simple entailment, RDFS (consistent graphs), OWL 2 RL/RDF incl.
  false-concluding rules. **Cor. 4 (planned)**: ontology-relative regimes,
  R_O = R ∪ {⟨∅, t⟩ : t ∈ O}, O ground; cl_{R_O}(X) = cl_R(X ∪ O).

## Code ↔ definition map (`checks/check_recovery.py`)

| Function | Implements |
|---|---|
| `make_closure(R)` → `closure(X)` | cl_R (Def. 4); instances over terms(X) ∪ V |
| `simply_entails(X, H)` | Def. 3 |
| `r_inconsistent`, `r_entails` | Def. 4 |
| `adj`, `adj_iter` | ⊔ (Def. 6) on generating sets; `adj_many([])` = unit `{⟨∅,∅⟩}` |
| `symj` | ⊓ (Def. 6) |
| `nabla` | ∇ (Hlobil 2026 Def. 10) |
| `pos_role`, `neg_role` | 𝓡⁺(𝔅t), 𝓡⁻(𝔅t) |
| `ground_content` | Def. 10 |
| `instances`, `content_pos`, `content_neg` | Def. 11 |
| `make_good(closure)` → `good(pair)` | membership in 𝕀_R (Defs 13–14, Herbrand) |
| `iss_entails`, `iss_incoherent` | Def. 7 via Lemma 2 |
| `gen_regime` | random Def.-4 regimes (schemas, no side conditions ⇒ uniform) |
| `make_closure(R, universe=N)` | **control**: the Cor. 3 slip (breaks uniformity) |
| `make_closure(R, bnode_only=True)` | **control**: a non-uniform regime |

Conventions: blank nodes are strings starting with `_`; `BOT = 'BOT'` is ⊥;
variables in schemas are `'X','Y','Z'`; `V`, `INDIV`, `SPARE`, `N`, `BN_G`,
`BN_H` are module globals that other scripts override (`import check_recovery
as C; C.N = ...`) — keep that pattern or replace it with explicit parameters
everywhere at once, not piecemeal.

## Pruning (the only reasoning the pruned checks borrow)

Membership of ⟨Γ, Δ⟩ in 𝕀_R is monotone in Γ and in Δ (cl_R is monotone;
overlap is monotone). Hence:
1. Positive side: every Lemma-3 pair ⟨⋃_{ν∈x} ν(G), ·⟩ contains the singleton
   pair ⟨ν(G), ·⟩; so "all x" ⇔ "all singletons". (`pos_singletons`)
2. Negative side: every pair ⟨·, ⋃S_μ⟩ contains one with a single triple per μ;
   so "all choices" ⇔ "all one-triple-per-μ choices". (`neg_minimal`)
Nothing else. Do not add Lemma 7's "some μ with μ(H) ⊆ cl" as a shortcut in
`check_exhaustive.py`; in `check_owlrl.py` it *is* used (documented in the
docstring) because owlrl is the closure oracle on both sides and the point of
that check is the real rule set, not the combinatorics.

## Other checks

- `check_theorem1.py`: Theorem 1 over every bearer map onto 2 or 3 bearers;
  fit frames are supersets of I_min(𝔅) = 𝕀_C ∪ 𝔅(base), content entailment is
  monotone in the frame, so checking I_min suffices.
- `check_lemma1.py`: Def. 3 vs rdflib SPARQL ASK (H's bnodes as variables).
- `check_owlrl.py`: owlrl materialize + ASK vs semantics; V = list ∪ IRIs of
  owlrl's closure of the empty graph (**required**); owlrl crashes/timeouts are
  counted and skipped, never judged.

## Results as reported (do not silently change the configurations)

See README table. If a configuration changes, rerun and update the table and
`results/` together; the paper's ledger quotes these numbers.

## Style

Python ≥ 3.10, standard library only except `check_lemma1.py`/`check_owlrl.py`
(rdflib, owlrl). Keep scripts runnable as `python3 script.py <seed> ...` from
`checks/`. Deterministic given the seed. Print a one-line summary at the end of
every run in the existing format; the logs in `results/` are parsed by eye.
