"""
Brute-force check of the recovery results in "Implication-Space Semantics for RDF".

What is computed literally from the definitions (no lemma is assumed; the
implementations are in the issrdf package, one module per group of
definitions — see DEFINITIONS.md):
  * Def 4   : closure cl_R, R-inconsistency, R-entailment (simple entailment by
              searching instance mappings, Def 3).
  * Def 6   : adjunction (coordinatewise union of one pair per member),
              symjunction (union of generating sets), power symjunction
              (symjunction over adjunctions of non-empty subsets).
  * Def 10/11: contents of ground and blank-node graphs, over a fixed N.
  * Def 13/14: the base B_R and the frame I_R (Herbrand model, B = identity).
  * Def 7   : content entailment = every pair of the generating set of
              [[G]]+ ⊔ [[H]]- lies in I_R  (this uses Lemma 2, which is
              itself checked numerically below on tiny frames).

What is then compared:
  * Theorem 2 / Lemma 7 : [[G]] |~ [[H]] in M_R  vs  G R-entails H.
  * Proposition 2       : [[G]] |~ ∅            vs  G R-inconsistent.
  * Lemma 2             : ⋃R(F) = RSR(RSR(F)) ⊆ I  iff  F ⊆ I, on random tiny frames.

Negative controls (hypotheses shown to be needed):
  * "instances over N only" (the Corollary 3 slip): closure on the Def 4 side
    uses only rule instances over N, so blank-node instances never fire.
  * non-uniform regime: a rule that fires only for blank-node subjects.

No pruning: Lemma 3's pairs are enumerated in full on both sides.
"""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.dirname(_HERE), _HERE]
import itertools, random
from issrdf import (Universe, bnodes, make_closure, r_inconsistent, r_entails,
                    make_good, iss_entails, iss_incoherent, rsr)
from generate import gen_regime, gen_graph

# The universe of the reported runs (results/run_*.txt): V = {p, q},
# individuals {a, b}, one spare IRI s for Skolemization (Def 12), one blank
# node on each side. N = (a, b, p, q, s).
DEFAULT = Universe(V=('p', 'q'), INDIV=('a', 'b'), SPARE=('s',), BN_G=('_x',), BN_H=('_y',))

# --------------------------------------------------------- Lemma 2 on tiny frames

def check_lemma2(rng, trials=200):
    bearers = ('t1', 't2', 't3')
    subsets = [frozenset(s) for r in range(4) for s in itertools.combinations(bearers, r)]
    S = [(A, B) for A in subsets for B in subsets]          # 64 candidate implications
    bad = 0
    for _ in range(trials):
        I = frozenset(p for p in S if (p[0] & p[1]) or rng.random() < 0.4)   # Containment + noise
        F = frozenset(rng.sample(S, rng.randint(0, 4)))
        closed = rsr(S, I, rsr(S, I, F))
        # ⋃R(F) is the union of all X with RSR(X) = RSR(F); check it equals RSR(RSR(F))
        # by verifying the latter is a member with the same RSR and contains F.
        assert F <= closed and rsr(S, I, closed) == rsr(S, I, F)
        if (closed <= I) != (F <= I):
            bad += 1
    return bad

# --------------------------------------------------------- main runs

def run(seed=1, n_regimes=40, n_pairs=25, U=DEFAULT):
    rng = random.Random(seed)
    print(f"Lemma 2 on random 3-bearer frames: {check_lemma2(rng)} failures")

    stats = dict(cases=0, entail=0, inconsistent=0, bn_G=0, bn_H=0,
                 mismatch_thm2=0, mismatch_prop2=0,
                 overN_cases=0, overN_mismatch=0, nonunif_cases=0, nonunif_mismatch=0)
    examples = dict(overN=None, nonunif=None)

    for r in range(n_regimes):
        R = gen_regime(rng, rng.randint(2, 5), U)
        cl_all = make_closure(R, U.V)
        cl_N = make_closure(R, U.V, instances_over=U.N)
        cl_bn = make_closure(R, U.V, bnode_only=True)
        good = make_good(cl_all)
        for _ in range(n_pairs):
            G = gen_graph(rng, rng.randint(0, 3), U.BN_G, U)
            H = gen_graph(rng, rng.randint(0, 2 if rng.random() < 0.7 else 3), U.BN_H, U)
            if bnodes(H) and len(H) > 2:
                H = frozenset(sorted(H)[:2])
            assert U.admissible(G, H)                      # Def 12
            stats['cases'] += 1
            stats['bn_G'] += bool(bnodes(G)); stats['bn_H'] += bool(bnodes(H))

            # Theorem 2 / Lemma 7
            a = iss_entails(good, G, H, U); b = r_entails(cl_all, G, H)
            stats['entail'] += b
            if a != b:
                stats['mismatch_thm2'] += 1
                print("THEOREM 2 MISMATCH", R, G, H, a, b)
            # Proposition 2
            a = iss_incoherent(good, G, U); b = r_inconsistent(cl_all, G)
            stats['inconsistent'] += b
            if a != b:
                stats['mismatch_prop2'] += 1
                print("PROPOSITION 2 MISMATCH", R, G, a, b)

            # control 1: instances over N only (the Corollary 3 slip)
            if bnodes(G):
                stats['overN_cases'] += 1
                a = iss_entails(good, G, H, U); b = r_entails(cl_N, G, H)
                if a != b:
                    stats['overN_mismatch'] += 1
                    examples['overN'] = examples['overN'] or (R, G, H, a, b)
            # control 2: non-uniform regime (rules fire only for blank-node X)
            if bnodes(G):
                stats['nonunif_cases'] += 1
                good_bn = make_good(cl_bn)
                a = iss_entails(good_bn, G, H, U); b = r_entails(cl_bn, G, H)
                if a != b:
                    stats['nonunif_mismatch'] += 1
                    examples['nonunif'] = examples['nonunif'] or (R, G, H, a, b)

    print()
    for k, v in stats.items():
        print(f"{k:18s} {v}")
    print()
    for k, ex in examples.items():
        if ex:
            R, G, H, a, b = ex
            print(f"example {k}: ISS={a} Def4={b}\n  R={R}\n  G={sorted(G)}\n  H={sorted(H)}")
    return stats

if __name__ == '__main__':
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    run(seed)
