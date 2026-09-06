"""Two blank nodes in G, pruned positive side.

Justification of the pruning (uses only Definition 13, no lemma): membership
of <Gam, Del> in I_R is monotone in Gam, since cl_R is monotone (Gam ⊆ Gam'
gives cl_R(Gam) ⊆ cl_R(Gam'), ⊥ included) and Gam ∩ Del ≠ ∅ is monotone.
Lemma 3's positive pairs are <⋃_{v∈x} v(G), ·> for non-empty x, each of which
contains the singleton pair <v(G), ·> for any v ∈ x. So "every x" holds iff
"every singleton x" holds. The negative side (∇ over H's instances) is still
enumerated in full."""
import random, sys, itertools
import check_recovery as C

C.V = ('p', 'q')
C.INDIV = ('a',)
C.SPARE = ('s1', 's2')
C.N = C.INDIV + C.V + C.SPARE          # 5 names, 25 mappings for two blank nodes
C.BN_G = ('_x', '_y')
C.BN_H = ('_z',)

def pos_singletons(G):
    return [C.adj_many(C.pos_role(t) for t in sorted(g)) for g in C.instances(G)]

def iss_entails(good, G, H):
    neg = C.content_neg(H)
    return all(good(pr) for P in pos_singletons(G) for pr in C.adj_iter(P, neg))

def iss_incoherent(good, G):
    return all(good(pr) for P in pos_singletons(G) for pr in C.adj_iter(P, C.UNIT))

def run(seed, n_regimes=40, n_pairs=25):
    rng = random.Random(seed)
    st = dict(cases=0, two=0, entail=0, inconsistent=0, thm2=0, prop2=0, overN_cases=0, overN=0)
    for _ in range(n_regimes):
        R = C.gen_regime(rng, rng.randint(2, 5))
        cl = C.make_closure(R); clN = C.make_closure(R, universe=C.N)
        good = C.make_good(cl)
        for _ in range(n_pairs):
            G = set(C.gen_graph(rng, rng.randint(1, 3), C.BN_G, p_bnode=0.6))
            if not {'_x', '_y'} <= C.bnodes(G):
                G.add(('_x', rng.choice(C.V), '_y'))
            G = frozenset(G)
            H = C.gen_graph(rng, rng.randint(0, 2), C.BN_H if rng.random() < 0.6 else ())
            st['cases'] += 1; st['two'] += len(C.bnodes(G)) == 2
            a = iss_entails(good, G, H); b = C.r_entails(cl, G, H); st['entail'] += b
            if a != b:
                st['thm2'] += 1; print("THEOREM 2 MISMATCH", R, sorted(G), sorted(H), a, b)
            a2 = iss_incoherent(good, G); b2 = C.r_inconsistent(cl, G); st['inconsistent'] += b2
            if a2 != b2:
                st['prop2'] += 1; print("PROPOSITION 2 MISMATCH", R, sorted(G), a2, b2)
            st['overN_cases'] += 1
            if a != C.r_entails(clN, G, H):
                st['overN'] += 1
    print(f"seed {seed}: " + ", ".join(f"{k} {v}" for k, v in st.items()))

if __name__ == '__main__':
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
