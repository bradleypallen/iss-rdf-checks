"""
Brute-force check of the recovery results in "Implication-Space Semantics for RDF".

What is computed literally from the definitions (no lemma is assumed):
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
"""
import itertools, random, sys
from functools import lru_cache

BOT = 'BOT'
V = ('p', 'q')            # vocabulary (fixed by the maps of Def 4(2))
INDIV = ('a', 'b')        # individual names available to G and H
SPARE = ('s',)            # spare IRI for Skolemization (admissibility, Def 12)
N = INDIV + V + SPARE     # the vocabulary fragment (Convention 1)
VARS = ('X', 'Y', 'Z')
BN_G = ('_x',)            # blank node available to G
BN_H = ('_y',)            # blank node available to H

def is_bnode(t): return t.startswith('_')
def is_var(t): return t in VARS
def terms(X): return {t for tr in X if tr != BOT for t in tr}
def bnodes(X): return {t for t in terms(X) if is_bnode(t)}
def inst(t, sub): return tuple(sub.get(u, u) for u in t)

# ---------------------------------------------------------------- regimes (Def 4)

def gen_regime(rng, nrules):
    """Random rule schemas: premises over variables and V, conclusion over
    premise variables and V (range restriction) or BOT. No side conditions,
    so uniformity is automatic (Remark 5)."""
    rules = []
    while len(rules) < nrules:
        k = rng.choice([1, 1, 2, 2, 0])
        prem = []
        for _ in range(k):
            prem.append(tuple(rng.choice(VARS + V) for _ in range(3)))
        pv = sorted({u for t in prem for u in t if is_var(u)})
        if k == 0:
            conc = tuple(rng.choice(V) for _ in range(3))        # axiomatic
        elif rng.random() < 0.25:
            conc = BOT                                          # false-concluding
        else:
            conc = tuple(rng.choice(tuple(pv) + V) for _ in range(3))
        if prem and conc != BOT and conc in prem:
            continue                                            # trivial rule
        rules.append((tuple(prem), conc))
    return tuple(rules)

def make_closure(R, universe=None, bnode_only=False):
    """cl_R(X). Instances over terms(X) ∪ V (all instances; range restriction
    means no other instance can ever fire). `universe` restricts instances to
    that set (the Corollary 3 slip); `bnode_only` fires rules only when X is
    a blank node (a non-uniform regime)."""
    @lru_cache(maxsize=None)
    def closure(X):
        X = set(X)
        U = (terms(X) | set(V)) if universe is None else set(universe)
        U = sorted(U)
        changed = True
        while changed:
            changed = False
            for prem, conc in R:
                pv = sorted({u for t in prem for u in t if is_var(u)})
                for img in itertools.product(U, repeat=len(pv)):
                    sub = dict(zip(pv, img))
                    if bnode_only and 'X' in sub and not is_bnode(sub['X']):
                        continue
                    if all(inst(t, sub) in X for t in prem):
                        c = BOT if conc == BOT else inst(conc, sub)
                        if c not in X:
                            X.add(c); changed = True
        return frozenset(X)
    return closure

# ------------------------------------------------- the practice's side (Def 3, 4)

def simply_entails(X, H):
    """Def 3: some instance mapping mu: bnodes(H) -> I ∪ B ∪ L with mu(H) ⊆ X."""
    X = set(X); H = set(H)
    bn = sorted(bnodes(H))
    if not bn:
        return H <= X
    T = sorted(terms(X))
    for img in itertools.product(T, repeat=len(bn)):
        mu = dict(zip(bn, img))
        if all(inst(t, mu) in X for t in H):
            return True
    return False

def r_inconsistent(closure, G): return BOT in closure(frozenset(G))

def r_entails(closure, G, H):
    cl = closure(frozenset(G))
    return BOT in cl or simply_entails(cl - {BOT}, H)

# ----------------------------------------- the semantics' side (Def 6, 7, 10, 11, 13, 14)

EMPTY = frozenset()
UNIT = frozenset({(EMPTY, EMPTY)})      # generating set of the unit for ⊔

def adj(F, K):                            # Def 6, adjunction on generating sets
    return frozenset((A | C, B | D) for (A, B) in F for (C, D) in K)

def adj_many(parts):                      # ⊔ over a family; empty family = unit
    acc = UNIT
    for F in parts:
        acc = adj(acc, F)
    return acc

def symj(parts):                          # Def 6, symjunction = union
    acc = frozenset()
    for F in parts:
        acc |= F
    return acc

def nabla(parts):                         # Hlobil 2026a: ∇X = ⊓{⊔x | ∅ ≠ x ⊆ X}
    parts = list(parts)
    subs = []
    for r in range(1, len(parts) + 1):
        for x in itertools.combinations(parts, r):
            subs.append(adj_many(x))
    return symj(subs)

def pos_role(t): return frozenset({(frozenset({t}), EMPTY)})   # R+(B(t))
def neg_role(t): return frozenset({(EMPTY, frozenset({t}))})   # R-(B(t))

def ground_content(G):                    # Def 10
    G = sorted(G)
    return adj_many(pos_role(t) for t in G), nabla(neg_role(t) for t in G)

def instances(G):
    bn = sorted(bnodes(G))
    maps = [dict(zip(bn, img)) for img in itertools.product(N, repeat=len(bn))]
    return [frozenset(inst(t, m) for t in G) for m in maps]

def content_pos(G):                       # Def 11, positive role (Def 10 when ground)
    return nabla(adj_many(pos_role(t) for t in sorted(g)) for g in instances(G))

def content_neg(G):                       # Def 11, negative role
    return adj_many(nabla(neg_role(t) for t in sorted(g)) for g in instances(G))

def content(G):
    return content_pos(G), content_neg(G)

def make_good(closure):                   # Def 13 + 14, Herbrand (B injective)
    def good(pair):
        Gam, Del = pair
        if Gam & Del:
            return True                   # I_C
        cl = closure(Gam)
        return BOT in cl or bool(Del & cl)
    return good

def adj_iter(F, K):                       # adjunction, streamed (same pairs as adj)
    for (A, B) in F:
        for (C, D) in K:
            yield (A | C, B | D)

def iss_entails(good, G, H):              # Def 7, via Lemma 2
    return all(good(pr) for pr in adj_iter(content_pos(G), content_neg(H)))

def iss_incoherent(good, G):              # Proposition 2's left-hand side
    return all(good(pr) for pr in adj_iter(content_pos(G), UNIT))

# --------------------------------------------------------- random graphs

def gen_graph(rng, size, bn_pool, p_bnode=0.4):
    G = set()
    while len(G) < size:
        tr = []
        for _ in range(3):
            if bn_pool and rng.random() < p_bnode:
                tr.append(rng.choice(bn_pool))
            else:
                tr.append(rng.choice(INDIV + V))
        G.add(tuple(tr))
    return frozenset(G)

# --------------------------------------------------------- Lemma 2 on tiny frames

def check_lemma2(rng, trials=200):
    bearers = ('t1', 't2', 't3')
    subsets = [frozenset(s) for r in range(4) for s in itertools.combinations(bearers, r)]
    S = [(A, B) for A in subsets for B in subsets]          # 64 candidate implications
    def rsr(I, F):
        return frozenset(p for p in S if all(((p[0] | x, p[1] | y) in I) for (x, y) in F))
    bad = 0
    for _ in range(trials):
        I = frozenset(p for p in S if (p[0] & p[1]) or rng.random() < 0.4)   # Containment + noise
        F = frozenset(rng.sample(S, rng.randint(0, 4)))
        closed = rsr(I, rsr(I, F))
        # ⋃R(F) is the union of all X with RSR(X) = RSR(F); check it equals RSR(RSR(F))
        # by verifying the latter is a member with the same RSR and contains F.
        assert F <= closed and rsr(I, closed) == rsr(I, F)
        if (closed <= I) != (F <= I):
            bad += 1
    return bad

# --------------------------------------------------------- main runs

def run(seed=1, n_regimes=40, n_pairs=25):
    rng = random.Random(seed)
    print(f"Lemma 2 on random 3-bearer frames: {check_lemma2(rng)} failures")

    stats = dict(cases=0, entail=0, inconsistent=0, bn_G=0, bn_H=0,
                 mismatch_thm2=0, mismatch_prop2=0,
                 overN_cases=0, overN_mismatch=0, nonunif_cases=0, nonunif_mismatch=0)
    examples = dict(overN=None, nonunif=None)

    for r in range(n_regimes):
        R = gen_regime(rng, rng.randint(2, 5))
        cl_all = make_closure(R)
        cl_N = make_closure(R, universe=N)
        cl_bn = make_closure(R, bnode_only=True)
        good = make_good(cl_all)
        for _ in range(n_pairs):
            G = gen_graph(rng, rng.randint(0, 3), BN_G)
            H = gen_graph(rng, rng.randint(0, 2 if rng.random() < 0.7 else 3), BN_H)
            if bnodes(H) and len(H) > 2:
                H = frozenset(sorted(H)[:2])
            stats['cases'] += 1
            stats['bn_G'] += bool(bnodes(G)); stats['bn_H'] += bool(bnodes(H))

            # Theorem 2 / Lemma 7
            a = iss_entails(good, G, H); b = r_entails(cl_all, G, H)
            stats['entail'] += b
            if a != b:
                stats['mismatch_thm2'] += 1
                print("THEOREM 2 MISMATCH", R, G, H, a, b)
            # Proposition 2
            a = iss_incoherent(good, G); b = r_inconsistent(cl_all, G)
            stats['inconsistent'] += b
            if a != b:
                stats['mismatch_prop2'] += 1
                print("PROPOSITION 2 MISMATCH", R, G, a, b)

            # control 1: instances over N only (the Corollary 3 slip)
            if bnodes(G):
                stats['overN_cases'] += 1
                a = iss_entails(good, G, H); b = r_entails(cl_N, G, H)
                if a != b:
                    stats['overN_mismatch'] += 1
                    examples['overN'] = examples['overN'] or (R, G, H, a, b)
            # control 2: non-uniform regime (rules fire only for blank-node X)
            if bnodes(G):
                stats['nonunif_cases'] += 1
                good_bn = make_good(cl_bn)
                a = iss_entails(good_bn, G, H); b = r_entails(cl_bn, G, H)
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
