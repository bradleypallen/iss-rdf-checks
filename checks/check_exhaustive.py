"""Exhaustive check of Theorem 2 / Lemma 7 and Proposition 2 over a small universe.

Universe: V = {p, q}; individuals {a, b}; spare IRI s; N = {a, b, p, q, s}.
Graphs: G ranges over ALL graphs of at most 2 triples with subject/object in
{a, b, _x} and predicate in {p, q} (172 graphs); H likewise with _y (172).
So every (G, H) pair is tested: 29,584 per regime, blank nodes on either
side or both.

Regimes: ALL single-rule regimes with premise (X, p, Y) and conclusion any
pattern over {X, Y, p, q} (64) or ⊥ (1): 65 regimes; then a handful of
multi-rule regimes (transitivity-like, RDFS-like, with ⊥ rules).

Semantics side is pruned by monotonicity only (Def 13): positive side to
singleton mapping sets, negative side to one triple per mapping mu. Both
prunings are sound because membership in I_R is monotone in Gam and in Del.
Everything else is computed from the definitions (see check_recovery.py)."""
import itertools, sys, time
import check_recovery as C

C.V = ('p', 'q'); C.INDIV = ('a', 'b'); C.SPARE = ('s',)
C.N = C.INDIV + C.V + C.SPARE
C.BN_G = ('_x',); C.BN_H = ('_y',)

def all_graphs(bn, maxsize=int(sys.argv[2]) if len(sys.argv) > 2 else 2):
    so = list(C.INDIV) + [bn]
    triples = [(s, p, o) for s in so for p in C.V for o in so]
    gs = [frozenset()]
    for k in range(1, maxsize + 1):
        gs += [frozenset(c) for c in itertools.combinations(triples, k)]
    return gs

GS = all_graphs('_x'); HS = all_graphs('_y')

def neg_minimal(H):
    """One triple per mapping mu: bnodes(H) -> N (minimal Lemma 3 negative pairs)."""
    insts = C.instances(H)
    if any(len(g) == 0 for g in insts):
        return [frozenset()] if not H else []
    return [frozenset(ch) for ch in itertools.product(*[sorted(g) for g in insts])]

def iss_entails(good, G, H, negs):
    if not H:
        return True
    for g in C.instances(G):
        for D in negs:
            if not good((g, D)):
                return False
    return True

def iss_incoherent(good, G):
    return all(good((g, frozenset())) for g in C.instances(G))

def check_regime(R, label):
    cl = C.make_closure(R); good = C.make_good(cl)
    negs = {H: neg_minimal(H) for H in HS}
    n = ent = inc = m2 = mp = 0
    t0 = time.time()
    for G in GS:
        a2 = iss_incoherent(good, G); b2 = C.r_inconsistent(cl, G); inc += b2
        if a2 != b2:
            mp += 1; print("PROP 2 MISMATCH", label, sorted(G), a2, b2, flush=True)
        for H in HS:
            n += 1
            a = iss_entails(good, G, H, negs[H]); b = C.r_entails(cl, G, H); ent += b
            if a != b:
                m2 += 1; print("THM 2 MISMATCH", label, sorted(G), sorted(H), a, b, flush=True)
    print(f"{label}: pairs {n}, entail {ent}, inconsistent G {inc}/{len(GS)}, "
          f"thm2 mismatches {m2}, prop2 mismatches {mp}, {time.time()-t0:.0f}s", flush=True)
    return m2, mp

def single_rule_regimes():
    prem = (('X', 'p', 'Y'),)
    concs = [C.BOT] + [c for c in itertools.product(('X', 'Y', 'p', 'q'), repeat=3)]
    return [((prem, c),) for c in concs]

MULTI = {
    'trans+bot': ((( ('X','p','Y'), ('Y','p','Z') ), ('X','p','Z')), ((( 'X','p','X'),), C.BOT)),
    'rdfs-like': ((( ('X','q','Y'), ('Y','p','Z') ), ('X','q','Z')), ((( 'X','p','Y'), ('Y','p','Z') ), ('X','p','Z'))),
    'sym+irrefl': ((( ('X','p','Y'),), ('Y','p','X')), ((( 'X','p','X'),), C.BOT)),
    'disjoint': ((( ('X','p','Y'),), ('X','q','Y')), ((( 'X','q','p'),), C.BOT)),
    'axiom+bot': (((), ('p','q','p')), ((( 'p','q','X'), ('X','p','Y')), C.BOT)),
}

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    total = [0, 0]
    if which in ('single', 'all'):
        for i, R in enumerate(single_rule_regimes()):
            m = check_regime(R, f"single[{i}] {R[0][1]}")
            total[0] += m[0]; total[1] += m[1]
    if which in ('multi', 'all'):
        for name, R in MULTI.items():
            m = check_regime(R, name)
            total[0] += m[0]; total[1] += m[1]
    print("TOTAL mismatches thm2/prop2:", total, flush=True)
