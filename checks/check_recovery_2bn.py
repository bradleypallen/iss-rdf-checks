"""Second configuration: G with up to two blank nodes, H ground or with one.
N = {a, p, s1, s2}: two spare IRIs so N is admissible (Def 12) for two blank
nodes in G. 16 instance mappings, so [[G]]+ has 2^16 - 1 generating pairs.
No pruning (correct but slow)."""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.dirname(_HERE), _HERE]
import random
from issrdf import (Universe, bnodes, make_closure, r_inconsistent, r_entails,
                    make_good, iss_entails, iss_incoherent)
from generate import gen_regime, gen_graph

U = Universe(V=('p',), INDIV=('a',), SPARE=('s1', 's2'), BN_G=('_x', '_y'), BN_H=('_z',))

def run(seed, n_regimes=2, n_pairs=2):
    rng = random.Random(seed)
    cases = mism = mism2 = ent = inc = two = 0
    for _ in range(n_regimes):
        R = gen_regime(rng, rng.randint(2, 4), U)
        cl = make_closure(R, U.V)
        good = make_good(cl)
        for _ in range(n_pairs):
            # force two blank nodes into G
            G = set(gen_graph(rng, rng.randint(1, 3), U.BN_G, U, p_bnode=0.6))
            if not {'_x', '_y'} <= bnodes(G):
                G.add(('_x', 'p', '_y'))
            G = frozenset(G)
            H = gen_graph(rng, rng.randint(0, 2), U.BN_H if rng.random() < 0.5 else (), U)
            assert U.admissible(G, H)
            cases += 1; two += len(bnodes(G)) == 2
            a = iss_entails(good, G, H, U); b = r_entails(cl, G, H)
            ent += b
            if a != b:
                mism += 1; print("THEOREM 2 MISMATCH", R, sorted(G), sorted(H), a, b)
            a = iss_incoherent(good, G, U); b = r_inconsistent(cl, G)
            inc += b
            if a != b:
                mism2 += 1; print("PROPOSITION 2 MISMATCH", R, sorted(G), a, b)
    print(f"seed {seed}: cases {cases} (two-bnode G {two}), entail {ent}, inconsistent {inc}, "
          f"thm2 mismatches {mism}, prop2 mismatches {mism2}")
    return dict(cases=cases, two=two, entail=ent, inconsistent=inc, thm2=mism, prop2=mism2)

if __name__ == '__main__':
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
