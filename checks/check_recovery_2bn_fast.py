"""Two blank nodes in G, pruned positive side.

The pruning (pruning.pos_singletons) uses only Definition 13, no lemma:
membership of <Gam, Del> in I_R is monotone in Gam, since cl_R is monotone
(Gam ⊆ Gam' gives cl_R(Gam) ⊆ cl_R(Gam'), ⊥ included) and Gam ∩ Del ≠ ∅ is
monotone. Lemma 3's positive pairs are <⋃_{v∈x} v(G), ·> for non-empty x,
each of which contains the singleton pair <v(G), ·> for any v ∈ x. So
"every x" holds iff "every singleton x" holds. The negative side (∇ over
H's instances) is still enumerated in full."""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.dirname(_HERE), _HERE]
import random
from issrdf import (Universe, bnodes, make_closure, r_inconsistent, r_entails,
                    make_good, content_neg, adj_iter, UNIT)
from generate import gen_regime, gen_graph
from pruning import pos_singletons

# 5 names, 25 mappings for two blank nodes
U = Universe(V=('p', 'q'), INDIV=('a',), SPARE=('s1', 's2'), BN_G=('_x', '_y'), BN_H=('_z',))

def iss_entails(good, G, H):
    neg = content_neg(H, U)
    return all(good(pr) for P in pos_singletons(G, U) for pr in adj_iter(P, neg))

def iss_incoherent(good, G):
    return all(good(pr) for P in pos_singletons(G, U) for pr in adj_iter(P, UNIT))

def run(seed, n_regimes=40, n_pairs=25):
    rng = random.Random(seed)
    st = dict(cases=0, two=0, entail=0, inconsistent=0, thm2=0, prop2=0, overN_cases=0, overN=0)
    for _ in range(n_regimes):
        R = gen_regime(rng, rng.randint(2, 5), U)
        cl = make_closure(R, U.V); clN = make_closure(R, U.V, instances_over=U.N)
        good = make_good(cl)
        for _ in range(n_pairs):
            G = set(gen_graph(rng, rng.randint(1, 3), U.BN_G, U, p_bnode=0.6))
            if not {'_x', '_y'} <= bnodes(G):
                G.add(('_x', rng.choice(U.V), '_y'))
            G = frozenset(G)
            H = gen_graph(rng, rng.randint(0, 2), U.BN_H if rng.random() < 0.6 else (), U)
            assert U.admissible(G, H)
            st['cases'] += 1; st['two'] += len(bnodes(G)) == 2
            a = iss_entails(good, G, H); b = r_entails(cl, G, H); st['entail'] += b
            if a != b:
                st['thm2'] += 1; print("THEOREM 2 MISMATCH", R, sorted(G), sorted(H), a, b)
            a2 = iss_incoherent(good, G); b2 = r_inconsistent(cl, G); st['inconsistent'] += b2
            if a2 != b2:
                st['prop2'] += 1; print("PROPOSITION 2 MISMATCH", R, sorted(G), a2, b2)
            st['overN_cases'] += 1
            if a != r_entails(clN, G, H):
                st['overN'] += 1
    print(f"seed {seed}: " + ", ".join(f"{k} {v}" for k, v in st.items()))

if __name__ == '__main__':
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
