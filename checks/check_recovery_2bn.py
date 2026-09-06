"""Second configuration: G with up to two blank nodes, H ground or with one.
N = {a, p, s1, s2}: two spare IRIs so N is admissible (Def 12) for two blank
nodes in G. 16 instance mappings, so [[G]]+ has 2^16 - 1 generating pairs."""
import random, sys, itertools
import check_recovery as C

C.V = ('p',)
C.INDIV = ('a',)
C.SPARE = ('s1', 's2')
C.N = C.INDIV + C.V + C.SPARE
C.BN_G = ('_x', '_y')
C.BN_H = ('_z',)

def run(seed, n_regimes=2, n_pairs=2):
    rng = random.Random(seed)
    cases = mism = mism2 = ent = inc = two = 0
    for _ in range(n_regimes):
        R = C.gen_regime(rng, rng.randint(2, 4))
        cl = C.make_closure(R)
        good = C.make_good(cl)
        for _ in range(n_pairs):
            # force two blank nodes into G
            G = set(C.gen_graph(rng, rng.randint(1, 3), C.BN_G, p_bnode=0.6))
            if not {'_x', '_y'} <= C.bnodes(G):
                G.add(('_x', 'p', '_y'))
            G = frozenset(G)
            H = C.gen_graph(rng, rng.randint(0, 2), C.BN_H if rng.random() < 0.5 else ())
            cases += 1; two += len(C.bnodes(G)) == 2
            a = C.iss_entails(good, G, H); b = C.r_entails(cl, G, H)
            ent += b
            if a != b:
                mism += 1; print("THEOREM 2 MISMATCH", R, sorted(G), sorted(H), a, b)
            a = C.iss_incoherent(good, G); b = C.r_inconsistent(cl, G)
            inc += b
            if a != b:
                mism2 += 1; print("PROPOSITION 2 MISMATCH", R, sorted(G), a, b)
    print(f"seed {seed}: cases {cases} (two-bnode G {two}), entail {ent}, inconsistent {inc}, "
          f"thm2 mismatches {mism}, prop2 mismatches {mism2}")

if __name__ == '__main__':
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
