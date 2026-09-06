"""Random regimes and graphs for the randomized checks. Not definitions of
the paper: this is the case generator, kept outside issrdf/ so that the
package contains only what the paper defines.

The order of random-number calls is part of the record: the seeds quoted in
README.md reproduce the logs in results/ only if it is preserved."""
from issrdf import BOT, VARS, is_var


def gen_regime(rng, nrules, U):
    """Random rule schemas over U.V: premises over variables and V, conclusion
    over premise variables and V (range restriction, Def. 4(1)) or ⊥. No side
    conditions, so uniformity is automatic (Remark 5)."""
    V = U.V
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


def gen_graph(rng, size, bn_pool, U, p_bnode=0.4):
    """Random graph of `size` distinct triples over U.INDIV ∪ U.V, each
    position a blank node from bn_pool with probability p_bnode."""
    G = set()
    while len(G) < size:
        tr = []
        for _ in range(3):
            if bn_pool and rng.random() < p_bnode:
                tr.append(rng.choice(bn_pool))
            else:
                tr.append(rng.choice(U.INDIV + U.V))
        G.add(tuple(tr))
    return frozenset(G)
