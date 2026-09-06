"""Exhaustive check of Theorem 2 / Lemma 7 and Proposition 2 over a small universe.

Universe: V = {p, q}; individuals {a, b}; spare IRI s; N = {a, b, p, q, s}.
Graphs: G ranges over ALL graphs of at most 2 triples with subject/object in
{a, b, _x} and predicate in {p, q} (172 graphs); H likewise with _y (172).
So every (G, H) pair is tested: 29,584 per regime, blank nodes on either
side or both.

Regimes: ALL single-rule regimes with premise (X, p, Y) and conclusion any
pattern over {X, Y, p, q} (64) or ⊥ (1): 65 regimes; then a handful of
multi-rule regimes (transitivity-like, RDFS-like, with ⊥ rules).

Semantics side is pruned by monotonicity only (Def 13; see pruning.py):
positive side to singleton mapping sets, negative side to one triple per
mapping mu. Everything else is computed from the definitions (issrdf).

Usage: python3 check_exhaustive.py [single|multi|all] [maxsize]"""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.dirname(_HERE), _HERE]
import itertools, time
from issrdf import Universe, BOT, make_closure, r_inconsistent, r_entails, make_good, instances
from pruning import neg_minimal

U = Universe(V=('p', 'q'), INDIV=('a', 'b'), SPARE=('s',), BN_G=('_x',), BN_H=('_y',))

def all_graphs(bn, maxsize):
    so = list(U.INDIV) + [bn]
    triples = [(s, p, o) for s in so for p in U.V for o in so]
    gs = [frozenset()]
    for k in range(1, maxsize + 1):
        gs += [frozenset(c) for c in itertools.combinations(triples, k)]
    return gs

def iss_entails(good, G, H, negs):
    if not H:
        return True
    for g in instances(G, U):
        for D in negs:
            if not good((g, D)):
                return False
    return True

def iss_incoherent(good, G):
    return all(good((g, frozenset())) for g in instances(G, U))

def check_regime(R, label, GS, HS):
    cl = make_closure(R, U.V); good = make_good(cl)
    negs = {H: neg_minimal(H, U) for H in HS}
    n = ent = inc = m2 = mp = 0
    t0 = time.time()
    for G in GS:
        a2 = iss_incoherent(good, G); b2 = r_inconsistent(cl, G); inc += b2
        if a2 != b2:
            mp += 1; print("PROP 2 MISMATCH", label, sorted(G), a2, b2, flush=True)
        for H in HS:
            n += 1
            a = iss_entails(good, G, H, negs[H]); b = r_entails(cl, G, H); ent += b
            if a != b:
                m2 += 1; print("THM 2 MISMATCH", label, sorted(G), sorted(H), a, b, flush=True)
    print(f"{label}: pairs {n}, entail {ent}, inconsistent G {inc}/{len(GS)}, "
          f"thm2 mismatches {m2}, prop2 mismatches {mp}, {time.time()-t0:.0f}s", flush=True)
    return m2, mp

def single_rule_regimes():
    prem = (('X', 'p', 'Y'),)
    concs = [BOT] + [c for c in itertools.product(('X', 'Y', 'p', 'q'), repeat=3)]
    return [((prem, c),) for c in concs]

MULTI = {
    'trans+bot': ((( ('X','p','Y'), ('Y','p','Z') ), ('X','p','Z')), ((( 'X','p','X'),), BOT)),
    'rdfs-like': ((( ('X','q','Y'), ('Y','p','Z') ), ('X','q','Z')), ((( 'X','p','Y'), ('Y','p','Z') ), ('X','p','Z'))),
    'sym+irrefl': ((( ('X','p','Y'),), ('Y','p','X')), ((( 'X','p','X'),), BOT)),
    'disjoint': ((( ('X','p','Y'),), ('X','q','Y')), ((( 'X','q','p'),), BOT)),
    'axiom+bot': (((), ('p','q','p')), ((( 'p','q','X'), ('X','p','Y')), BOT)),
}

def main(which='all', maxsize=2):
    """Returns [thm2 mismatches, prop2 mismatches] summed over the regimes run."""
    GS = all_graphs('_x', maxsize); HS = all_graphs('_y', maxsize)
    total = [0, 0]
    if which in ('single', 'all'):
        for i, R in enumerate(single_rule_regimes()):
            m = check_regime(R, f"single[{i}] {R[0][1]}", GS, HS)
            total[0] += m[0]; total[1] += m[1]
    if which in ('multi', 'all'):
        for name, R in MULTI.items():
            m = check_regime(R, name, GS, HS)
            total[0] += m[0]; total[1] += m[1]
    print("TOTAL mismatches thm2/prop2:", total, flush=True)
    return total

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'all',
         int(sys.argv[2]) if len(sys.argv) > 2 else 2)
