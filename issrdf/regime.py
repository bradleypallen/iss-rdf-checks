"""Definitions 1–4 (Section 2 of the paper): triples and graphs, simple
entailment, entailment regimes and their closure.

Representation. A triple is a 3-tuple of strings; a graph is a frozenset of
triples. Blank nodes are strings starting with '_' (Definition 1's B); every
other string is a name (an IRI; literals do not occur in the checks). BOT is
the symbol ⊥ of Definition 4. Rules are pairs (premises, conclusion) whose
terms may include the metavariables VARS; a rule schema stands for the set of
its instances under uniform substitution (Remark 5), which makes uniformity
automatic since no schema carries a side condition.
"""
import itertools
from functools import lru_cache

BOT = 'BOT'                 # ⊥
VARS = ('X', 'Y', 'Z')      # metavariables of rule schemas (Remark 5)


def is_bnode(t):
    """Definition 1: t ∈ B."""
    return t.startswith('_')


def is_var(t):
    return t in VARS


def terms(X):
    """All terms occurring in the triples of X (⊥ carries none)."""
    return {t for tr in X if tr != BOT for t in tr}


def bnodes(X):
    """Definition 2: bnodes(G), the blank nodes occurring in G."""
    return {t for t in terms(X) if is_bnode(t)}


def names(X):
    """Definition 2: names(G), the names (elements of I ∪ L) occurring in G."""
    return {t for t in terms(X) if not is_bnode(t)}


def inst(t, sub):
    """Apply a map on terms pointwise to a triple (Definition 2: an instance
    mapping is "extended to triples and graphs pointwise and acting as the
    identity on names"; the same for the maps ρ of Definition 4(2))."""
    return tuple(sub.get(u, u) for u in t)


def make_closure(R, V, instances_over=None, bnode_only=False):
    """Definition 4 (Entailment regime), the closure.  "The closure cl_R(X) of
    a set X of triples is the least Y ⊆ L^RDF ∪ {⊥} with Y ⊇ X such that c ∈ Y
    whenever ⟨A, c⟩ ∈ R and A ⊆ Y."

    R is a tuple of rule schemas over V; the returned function computes
    cl_R(X) by iterating the schemas' instances to a fixed point. Instances
    are taken over terms(X) ∪ V: by range restriction (Definition 4(1)) no
    instance over any other term can fire, so this is the closure under the
    full, infinite regime R. Memoized per closure function.

    Two deliberate deviations exist as negative controls and must not be used
    for anything else:
      instances_over=N   take instances over N only, so instances at blank
                         nodes never fire — the slip of an earlier draft's
                         Corollary 3 (the "instances over N" control);
      bnode_only=True    fire a rule only when X is bound to a blank node —
                         a regime that violates uniformity (Definition 4(2)).
    """
    @lru_cache(maxsize=None)
    def closure(X):
        X = set(X)
        U = (terms(X) | set(V)) if instances_over is None else set(instances_over)
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


def simply_entails(X, H):
    """Definition 3 (Simple RDF entailment).  "G simply entails G' if and only
    if some subgraph of G is an instance of G'; i.e., iff there is an instance
    mapping μ with μ(G') ⊆ G."  μ : bnodes(H) → I ∪ B ∪ L; only images among
    terms(X) can make μ(H) ⊆ X, so those are the ones searched."""
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


def r_inconsistent(closure, G):
    """Definition 4: "X is R-inconsistent iff ⊥ ∈ cl_R(X)."."""
    return BOT in closure(frozenset(G))


def r_entails(closure, G, H):
    """Definition 4: "G R-entails H iff G is R-inconsistent or cl_R(G) ∖ {⊥}
    simply entails H."."""
    cl = closure(frozenset(G))
    return BOT in cl or simply_entails(cl - {BOT}, H)
