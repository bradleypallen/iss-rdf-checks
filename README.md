# Machine checks for *Implication-Space Semantics for RDF*

[![checks](https://github.com/bradleypallen/iss-rdf-checks/actions/workflows/checks.yml/badge.svg)](https://github.com/bradleypallen/iss-rdf-checks/actions/workflows/checks.yml)

Companion code for Bradley P. Allen, *Implication-Space Semantics for RDF* (working paper, University of Amsterdam, September 2026). The paper gives RDF an inferentialist semantics in the implication-space framework of Hlobil and Brandom (2025) and Hlobil (2026), and proves that, for every entailment regime presented by closure under Horn rules (false-concluding rules included), the entailment relation the fit models sanction between the contents of two graphs is exactly the one a compliant reasoner establishes by materializing the first graph and querying the result for the second.

This repository contains the scripts used to check those results by computation. Nothing here is a proof; the proofs are in the paper. What the scripts do is compute both sides of each theorem literally from the paper's definitions, run them on many inputs, and confirm that they never disagree — and, as importantly, confirm that they *do* disagree when a hypothesis of the theorem is deliberately removed.

## What was done, in plain terms

The main check asks one question many times: do the two ways of deciding whether `G` entails `H` agree? The first way is the Semantic Web's: apply the regime's rules to `G` until nothing new appears, then look for a copy of `H` in the result, or for *false*. The second way is the paper's: build `G`'s content and `H`'s content as the definitions say, combine them, and ask whether every resulting pair is a good implication of the frame the regime induces. Both are written as short programs straight from the definitions, without using any of the paper's lemmas. Then the programs are run on the same inputs and the answers compared. Two kinds of inputs are used: random small regimes and graphs, thousands of them, with blank nodes on either side; and, separately, every possible pair of small graphs over a fixed tiny vocabulary for seventy fixed regimes, so that on that universe the answer is not "no counterexample was found" but "there is none". They always agreed. The same is done for Proposition 2, comparing "`G` is incoherent in the semantics" with "the rules derive false from `G`".

The controls ask the opposite question: does the check notice when something is wrong? Two of the paper's hypotheses are deliberately broken, once by restricting rule instances to `N` (the mistake an earlier draft's Corollary 3 made), and once by making a regime non-uniform. In both cases the two programs start to disagree, in the direction the theory predicts.

The Theorem 1 check asks whether the Herbrand model is really enough. It takes a tiny world of eight triples, a random base with no nice properties at all, and every possible way of mapping those triples onto two or three bearers, including all the ways that send different triples to the same bearer. For each mapping it builds the smallest frame fit for the base and asks whether everything the Herbrand model says entails still entails there. It always did.

The Lemma 1 check asks whether the paper's definition of simple entailment is the standard one, by comparing it with rdflib's SPARQL engine on thousands of ordinary RDF graphs.

The end-to-end check asks whether the paper's operational claim is true with a real tool: that recovery means "materialize, then query". It uses `owlrl`, an off-the-shelf RDFS and OWL 2 RL reasoner, on one side, and the semantics computed from the definitions on the other, on random graphs including ones built to be inconsistent.

## Layout

```
issrdf/                      The paper's definitions as code, one module per group:
  universe.py                Convention 1, Def. 12 (the fragment N, admissibility)
  regime.py                  Defs 1–4 (triples, simple entailment, regimes, cl_R)
  roles.py                   Def. 6 (⊔, ⊓, ∇ on generating sets, R⁺, R⁻)
  content.py                 Defs 9–11 (contents of ground and blank-node graphs)
  frame.py                   Defs 7, 8, 13–15 (the base, the frame, entailment)
  show.py                    Display helpers for the notebooks (no definitions).
DEFINITIONS.md               Table: every numbered definition → module.function.
notebooks/
  01_walkthrough.ipynb       One example (tweety, Bird, Flier; rdfs9 + cax-dw) taken through both
                             sides with every intermediate object printed: ground graphs, a blank
                             node in H, a blank node in G (the Skolem instance decides), an
                             incoherent G (Proposition 2). Executed outputs are committed.
  02_make_it_fail.ipynb      The controls: the Corollary 3 slip, a non-uniform regime, and owlrl
                             with an undersized V; each hypothesis removed, the disagreement
                             shown with its reason, and agreement restored.
checks/
  generate.py                Random regimes and graphs for the randomized checks.
  pruning.py                 The two monotonicity prunings (the only borrowed reasoning).
  check_recovery.py          Theorem 2 / Lemma 7 and Proposition 2, random cases, one blank node
                             each side, Lemma 3's pairs enumerated in full; Lemma 2 on random
                             tiny frames; the two negative controls.
  check_recovery_2bn.py      Same, two blank nodes in G, full enumeration (correct but slow).
  check_recovery_2bn_fast.py Same, positive side pruned to singleton mapping sets
                             (justified by monotonicity of the closure alone).
  check_exhaustive.py        Every pair of graphs up to size 2 or 3 over a fixed universe,
                             for 65 enumerated single-rule regimes + 5 multi-rule regimes.
  check_theorem1.py          Theorem 1 over every bearer map onto 2 or 3 bearers.
  check_lemma1.py            Definition 3 vs rdflib SPARQL ASK (needs rdflib).
  check_owlrl.py             End to end vs owlrl materialization + ASK (needs rdflib, owlrl).
tests/                       pytest: hand-built examples against the definitions (tweety, the clash,
                             the Cor. 3 counterexample, ∇ shapes, Lemma 2 exhaustively on a tiny
                             frame, N-independence) and quick subsets of every check script.
results/                     Logs of the runs reported in the paper's ledger, of the notebooks, and
                             of the test suite (tests.txt).
tools/                       reproduce.sh re-creates every log in results/; compare_logs.py
                             diffs a fresh set against it (timing lines ignored).
run_all.sh                   Reproduces the quick runs (a few minutes); see comments for the rest.
```

The scripts import `issrdf` from the repository root (each starts with a two-line path bootstrap), so run them from `checks/` as shown below; nothing needs installing. `issrdf` and the first five scripts need only the Python standard library. The last two need `pip install -r requirements.txt` (rdflib, owlrl). The notebooks need `pip install -r requirements-dev.txt` and run from `notebooks/`; they import from `issrdf` and compute nothing themselves.

## What is computed from what

The following are implemented directly from the paper's definitions, and no lemma of the paper is used in computing them:

* closure `cl_R`, `R`-inconsistency and `R`-entailment (Definitions 3–4; simple entailment by searching instance mappings);
* adjunction, symjunction and power-symjunction on generating sets of pairs (Definition 6; Hlobil 2026, Def. 10);
* contents of ground and blank-node graphs over a fixed `N` (Definitions 10–11);
* the base `B_R` and the frame `I_R` in the Herbrand model (Definitions 13–14);
* content entailment as "every generating pair of `[[G]]+ ⊔ [[H]]-` lies in `I_R`" (Definition 7 together with Lemma 2; Lemma 2 itself is checked numerically on random three-bearer frames in `check_recovery.py`).

Two prunings are used in the larger runs, both resting only on the fact that membership in `I_R` is monotone in both coordinates (a one-line consequence of Definition 13): the positive side of Lemma 3 may be restricted to singleton sets of instance mappings, and the negative side to one triple per mapping. `check_recovery.py` and `check_recovery_2bn.py` use no pruning.

## Results

| Check | Inputs | Outcome |
|---|---|---|
| Theorem 2 / Prop. 2, random, one blank node per side, full enumeration | 5 seeds × 1000 cases | 0 mismatches |
| Theorem 2 / Prop. 2, random, two blank nodes in G, full enumeration | 12 cases | 0 mismatches |
| Theorem 2 / Prop. 2, random, two blank nodes in G, pruned | 4 seeds × 1000 cases | 0 mismatches |
| Theorem 2 / Prop. 2, exhaustive, graphs ≤ 2 triples per side | 70 regimes × 29,584 pairs = 2,070,880 | 0 mismatches |
| Theorem 2 / Prop. 2, exhaustive, graphs ≤ 3 triples per side | 5 regimes × 976,144 pairs = 4,880,720 | 0 mismatches |
| Control: rule instances restricted to `N` | 1000-case runs | 18–65 mismatches per 1000 (semantics yes / rules no) |
| Control: non-uniform regime | 1000-case runs | 4–29 mismatches per 1000 (rules yes / semantics no) |
| Theorem 1, every bearer map onto 2 bearers | 256 maps, 210 cases, 53,760 checks | 0 violations |
| Theorem 1, every bearer map onto 3 bearers | 6,561 maps, 113 cases, 741,393 checks | 0 violations |
| Lemma 1 / Def. 3 vs rdflib SPARQL | 3,000 standard-graph pairs | 0 mismatches |
| End to end vs owlrl, RDFS | 300 cases | 0 mismatches |
| End to end vs owlrl, OWL 2 RL (with clash templates) | 3 seeds, 592 cases, 197 inconsistent | 0 mismatches; 8 cases skipped where owlrl itself crashed or exceeded 30 s |

Two lessons from the runs are worth recording. The only mismatches ever seen in the owlrl run came from taking the vocabulary `V` smaller than the regime's real vocabulary (owlrl adds 106 axiomatic triples over 54 IRIs even with axiomatic triples switched off); they vanished once `V` contained those IRIs, which is the paper's admissibility hypothesis showing itself in practice. And the "instances over `N`" control is the exact failure of an earlier draft's Corollary 3, found by reading and then confirmed here.

## What this does not check

Theorem 1 beyond toy size; that owlrl's rule set is the published OWL 2 RL/RDF tables; anything about the datatype (`D`-entailment) side, which the paper sets aside; and of course anything a random or small exhaustive search cannot reach. A formal proof would close those; this does not.

## Reproducing

```
cd checks
python3 check_recovery.py 1            # ~15 s
python3 check_recovery_2bn_fast.py 1   # ~1 min
python3 check_exhaustive.py all        # ~1 min, graphs ≤ 2
python3 check_exhaustive.py multi 3    # ~7 min, graphs ≤ 3
python3 check_theorem1.py 1 2          # seconds;  "1 3" takes ~1 min
pip install rdflib owlrl
python3 check_lemma1.py 1              # ~6 s
python3 check_owlrl.py 1 rdfs 300      # ~20 s
python3 check_owlrl.py 2 owl 200       # ~15 min
```

Seeds are the first argument; any integer works. `run_all.sh` runs the quick subset. `pytest` (from the repository root, about 5 s) runs the hand-built examples and a quick subset of every check, skipping the rdflib/owlrl ones if those are not installed, and writes `results/tests.txt`; `pytest --nbmake notebooks/` re-executes the notebooks. GitHub Actions runs both on every push, on the standard library alone and with the full toolchain, and keeps the executed notebooks and logs as build artifacts. To check that a change to the code leaves every number in the table as it is, `tools/reproduce.sh <dir> all` re-creates every log in `results/` (about 25 minutes) and `python3 tools/compare_logs.py <dir>` diffs them, ignoring timing lines only. The OWL logs were produced with owlrl 7.6.2 and `PYTHONHASHSEED=0`; the check sorts the pool it samples `H` from, so they are independent of the hash seed.

## License

MIT. If you use this, cite the paper.
