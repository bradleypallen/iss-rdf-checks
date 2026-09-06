"""Hand-built examples against the definitions in issrdf (no random input)."""
import itertools
import pytest
from issrdf import (Universe, BOT, EMPTY, make_closure, r_entails, r_inconsistent, make_good,
                    iss_entails, iss_incoherent, nabla, pos_role, neg_role, ground_content, rsr,
                    content_pos, content_neg, adj)

# The walkthrough's universe and regime (rdfs9 + cax-dw).
U = Universe(V=('type', 'subClassOf', 'disjointWith'), INDIV=('tweety', 'Bird', 'Flier'), SPARE=('s',))
R = (((('X', 'type', 'Y'), ('Y', 'subClassOf', 'Z')), ('X', 'type', 'Z')),
     ((('X', 'type', 'Y'), ('X', 'type', 'Z'), ('Y', 'disjointWith', 'Z')), BOT))
G = frozenset({('tweety', 'type', 'Bird'), ('Bird', 'subClassOf', 'Flier')})
H = frozenset({('tweety', 'type', 'Flier')})


def both(R, U, G, H):
    """(semantics, rules) verdicts for G |~ H."""
    cl = make_closure(R, U.V)
    return iss_entails(make_good(cl), G, H, U), r_entails(cl, G, H)


def test_tweety_entails(log):
    assert U.admissible(G, H)
    assert both(R, U, G, H) == (True, True)
    assert both(R, U, G, frozenset({('_y', 'type', 'Flier')})) == (True, True)
    log("tweety entails Flier, ground and blank-node H: both sides True")


def test_clash_is_incoherent(log):
    Gd = G | {('Bird', 'disjointWith', 'Flier')}
    cl = make_closure(R, U.V)
    assert r_inconsistent(cl, Gd) and iss_incoherent(make_good(cl), Gd, U)
    assert not r_inconsistent(cl, G) and not iss_incoherent(make_good(cl), G, U)
    assert both(R, U, Gd, frozenset({('Flier', 'type', 'tweety')})) == (True, True)   # explosion
    log("disjointWith clash: incoherent on both sides; consistent G is not; explosion")


def test_corollary3_counterexample(log):
    U1 = Universe(V=('type', 'subClassOf'), INDIV=('C', 'D'), SPARE=('s',))
    R1 = (((('X', 'type', 'Y'), ('Y', 'subClassOf', 'Z')), ('X', 'type', 'Z')),)
    G1 = frozenset({('_x', 'type', 'C'), ('C', 'subClassOf', 'D')})
    H1 = frozenset({('_y', 'type', 'D')})
    cl_all = make_closure(R1, U1.V); cl_N = make_closure(R1, U1.V, instances_over=U1.N)
    good = make_good(cl_all)
    assert (iss_entails(good, G1, H1, U1), r_entails(cl_all, G1, H1)) == (True, True)
    assert (iss_entails(good, G1, H1, U1), r_entails(cl_N, G1, H1)) == (True, False)
    assert iss_entails(make_good(cl_N), G1, H1, U1)                 # the frame is unaffected
    log("Cor. 3 example: agrees under all instances, semantics True / rules False over N only")


def test_nonuniform_regime(log):
    U2 = Universe(V=('type', 'Bird', 'Flier'), INDIV=('tweety',), SPARE=('s',))
    R2 = (((('X', 'type', 'Bird'),), ('X', 'type', 'Flier')),)
    G2 = frozenset({('_x', 'type', 'Bird')}); H2 = frozenset({('_y', 'type', 'Flier')})
    cl = make_closure(R2, U2.V, bnode_only=True)
    assert (iss_entails(make_good(cl), G2, H2, U2), r_entails(cl, G2, H2)) == (False, True)
    assert both(R2, U2, G2, H2) == (True, True)
    log("non-uniform regime: rules True / semantics False; uniform version agrees")


def test_nabla_of_two_singleton_roles(log):
    a, b = ('a', 'p', 'a'), ('b', 'p', 'b')
    assert nabla([pos_role(a), pos_role(b)]) == frozenset({
        (frozenset({a}), EMPTY), (frozenset({b}), EMPTY), (frozenset({a, b}), EMPTY)})
    assert nabla([neg_role(a), neg_role(b)]) == frozenset({
        (EMPTY, frozenset({a})), (EMPTY, frozenset({b})), (EMPTY, frozenset({a, b}))})
    pos, neg = ground_content(frozenset({a, b}))
    assert pos == frozenset({(frozenset({a, b}), EMPTY)})              # Def. 10: one pair
    assert neg == nabla([neg_role(a), neg_role(b)])                     # Def. 10: the three
    log("nabla of two singleton roles is the three-pair set; Def. 10 shapes")


def test_lemma2_on_hand_built_frame(log):
    """Lemma 2 (Reduction): union R(F) = RSR(RSR(F)) ⊆ I iff F ⊆ I, exhaustively over
    every F of at most two candidate implications of a two-bearer frame whose
    good implications are Containment plus 'a implies b'."""
    bearers = ('a', 'b')
    subsets = [frozenset(c) for r in range(3) for c in itertools.combinations(bearers, r)]
    S = [(A, B) for A in subsets for B in subsets]                       # 16 candidates
    I = frozenset(p for p in S if p[0] & p[1]) | {(frozenset({'a'}), frozenset({'b'}))}
    checked = 0
    for r in range(0, 3):
        for F in itertools.combinations(S, r):
            F = frozenset(F)
            closed = rsr(S, I, rsr(S, I, F))
            assert F <= closed and rsr(S, I, closed) == rsr(S, I, F)
            assert (closed <= I) == (F <= I)
            checked += 1
    log(f"Lemma 2 exhaustive on a 2-bearer frame, {checked} generating sets")


def test_N_independence(log):
    """Paragraph after Theorem 2: the verdict is the same for every admissible N."""
    U2 = Universe(V=U.V, INDIV=U.INDIV, SPARE=('s', 's2'))
    cases = [(G, H), (G, frozenset({('_y', 'type', 'Flier')})),
             (frozenset({('_x', 'type', 'Bird'), ('Bird', 'subClassOf', 'Flier')}), H),
             (frozenset({('_x', 'type', 'Bird'), ('Bird', 'subClassOf', 'Flier')}), frozenset({('_y', 'type', 'Flier')})),
             (frozenset({('_x', 'type', 'Bird'), ('_x', 'type', 'Flier'), ('Bird', 'disjointWith', 'Flier')}), frozenset())]
    for g, h in cases:
        assert U.admissible(g, h) and U2.admissible(g, h)
        assert both(R, U, g, h) == both(R, U2, g, h)
        assert both(R, U, g, h)[0] == both(R, U, g, h)[1]
    log(f"N-independence: {len(cases)} cases agree with one and two spare IRIs")


def test_admissibility():
    assert U.admissible(frozenset({('_x', 'type', 'Bird')}), H)
    assert not Universe(V=U.V, INDIV=U.INDIV, SPARE=()).admissible(
        frozenset({('_x', 'type', 'Bird'), ('_x', 'type', 'tweety'), ('_x', 'type', 'Flier')}), H)   # no free IRI
    assert not U.admissible(frozenset({('elsewhere', 'type', 'Bird')}), H)                        # name outside N
