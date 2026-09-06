"""Definition 6 (Implicational roles and their operations; Hlobil and Brandom
2025, Ch. 5) and the power-symjunction of Hlobil 2026, Definition 10.

Roles are handled by generating sets: a role is represented by a set of
candidate implications ⟨Γ, Δ⟩ that generates it (Definition 6: "We say that
a set H ⊆ S generates the role R(H); the operations are defined on
generating sets"). A pair is a 2-tuple of frozensets of bearers; in the
Herbrand model (Definition 15) bearers are the ground triples themselves.
"""
import itertools

EMPTY = frozenset()
UNIT = frozenset({(EMPTY, EMPTY)})      # generates the unit of ⊔ (Proposition 2: "the
                                        # adjunction over the empty family")


def adj(F, K):
    """Definition 6, adjunction on generating sets:
    "R(H) ⊔ R(J) = R({⟨A ∪ C, B ∪ D⟩ | ⟨A, B⟩ ∈ H, ⟨C, D⟩ ∈ J})"."""
    return frozenset((A | C, B | D) for (A, B) in F for (C, D) in K)


def adj_iter(F, K):
    """The pairs of adj(F, K), streamed in a fixed order (same set)."""
    for (A, B) in F:
        for (C, D) in K:
            yield (A | C, B | D)


def adj_many(parts):
    """⊔ over a finite family of generating sets; the empty family gives the
    unit {⟨∅, ∅⟩}. "Adjunction distributes over symjunction", so folding
    pairwise is the operation on the whole family."""
    acc = UNIT
    for F in parts:
        acc = adj(acc, F)
    return acc


def symj(parts):
    """Definition 6, symjunction on generating sets:
    "R(H) ⊓ R(J) = R(H ∪ J)"."""
    acc = frozenset()
    for F in parts:
        acc |= F
    return acc


def nabla(parts):
    """Definition 6, power-symjunction (Hlobil 2026, Def. 10):
    "∇X = ⊓{⊔x | x ⊆ X, x ≠ ∅} for a set of roles X"."""
    parts = list(parts)
    subs = []
    for r in range(1, len(parts) + 1):
        for x in itertools.combinations(parts, r):
            subs.append(adj_many(x))
    return symj(subs)


def pos_role(t):
    """Definition 6: for a bearer a, R⁺(a) = R⟨{a}, ∅⟩. With Definition 9's
    bearer map in the Herbrand model, the bearer of a ground triple t is t."""
    return frozenset({(frozenset({t}), EMPTY)})


def neg_role(t):
    """Definition 6: R⁻(a) = R⟨∅, {a}⟩."""
    return frozenset({(EMPTY, frozenset({t}))})
