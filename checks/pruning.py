"""The two prunings used by the larger runs, and the only reasoning the
semantics side borrows beyond the definitions (CLAUDE.md, "Pruning").

Both rest on one fact from Definition 13: membership of ⟨Γ, Δ⟩ in I_R is
monotone in Γ and in Δ, because cl_R is monotone (Γ ⊆ Γ' gives
cl_R(Γ) ⊆ cl_R(Γ'), ⊥ included) and Γ ∩ Δ ≠ ∅ is monotone. Hence:

  1. Positive side. Every Lemma-3 pair ⟨⋃_{ν∈x} ν(G), ·⟩, x a non-empty set
     of instance mappings, contains the singleton pair ⟨ν(G), ·⟩ for any
     ν ∈ x; so "every x lies in I_R" iff "every singleton does".
  2. Negative side. Every pair ⟨·, ⋃_μ S_μ⟩ contains one with S_μ a single
     triple of μ(H); so "every choice" iff "every one-triple-per-μ choice".

Nothing else is borrowed. Lemma 7's "some μ with μ(H) ⊆ cl_R(G)" is NOT
a pruning and must not be added here (check_owlrl.py uses it, for the
reason its docstring gives).
"""
import itertools
from issrdf import adj_many, pos_role, instances


def pos_singletons(G, U):
    """Generating sets of the singleton positive pairs ⟨ν(G), ∅⟩, one per
    instance mapping ν."""
    return [adj_many(pos_role(t) for t in sorted(g)) for g in instances(G, U)]


def neg_minimal(H, U):
    """One triple per mapping μ : bnodes(H) → N — the minimal Lemma-3
    negative pairs' succedents. Empty H has no negative pairs."""
    insts = instances(H, U)
    if any(len(g) == 0 for g in insts):
        return [frozenset()] if not H else []
    return [frozenset(ch) for ch in itertools.product(*[sorted(g) for g in insts])]
