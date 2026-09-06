"""Definitions 9–11: contents of ground graphs and of graphs with blank nodes,
over the fragment N of a Universe.

Definition 9 (RDF triples as bearers) is the bearer map 𝔅; in the Herbrand
model of Definition 15 it is the identity on ground triples, which is what
pos_role/neg_role assume. check_theorem1.py supplies other bearer maps.
"""
import itertools
from .regime import bnodes, inst
from .roles import adj_many, nabla, pos_role, neg_role


def ground_content(G):
    """Definition 10 (Content of a ground RDF graph):
    "⟦G⟧ = ⟨⊔{R⁺(𝔅(t)) | t ∈ G}, ∇{R⁻(𝔅(t)) | t ∈ G}⟩, its positive role the
    adjunction of its triples' positive roles, its negative role the power
    symjunction of theirs." Triples are taken in sorted order (the sets are
    order-independent)."""
    G = sorted(G)
    return adj_many(pos_role(t) for t in G), nabla(neg_role(t) for t in G)


def instances(G, U):
    """Definition 11: the ground instances μ(G) "where μ ranges over the
    mappings bnodes(H) → N (Convention 1), a blank node in any position being
    mapped alike." For ground G the family is the single instance G."""
    bn = sorted(bnodes(G))
    maps = [dict(zip(bn, img)) for img in itertools.product(U.N, repeat=len(bn))]
    return [frozenset(inst(t, m) for t in G) for m in maps]


def content_pos(G, U):
    """Definition 11, positive role: ∇{⟦μ(H)⟧⁺ | μ}, each ⟦μ(H)⟧⁺ by
    Definition 10. Reduces to Definition 10 when G is ground."""
    return nabla(adj_many(pos_role(t) for t in sorted(g)) for g in instances(G, U))


def content_neg(G, U):
    """Definition 11, negative role: ⊔{⟦μ(H)⟧⁻ | μ}."""
    return adj_many(nabla(neg_role(t) for t in sorted(g)) for g in instances(G, U))


def content(G, U):
    """Definition 11: ⟦H⟧ = ⟨∇{⟦μ(H)⟧⁺ | μ}, ⊔{⟦μ(H)⟧⁻ | μ}⟩."""
    return content_pos(G, U), content_neg(G, U)
