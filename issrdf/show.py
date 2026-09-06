"""Display helpers for the notebooks. Nothing here computes a definition:
these functions format triples, graphs, generating sets and rules, and
explain a frame-membership verdict by restating the tests of make_good.

Notation: blank nodes print as _:x (stored as '_x'); ∅ for the empty set;
a candidate implication ⟨Γ, Δ⟩ prints as ⟨{…}, {…}⟩.
"""
import pathlib
from .regime import BOT, is_bnode, is_var


def term(u):
    return '_:' + u[1:] if is_bnode(u) else u


def triple(t):
    return '⊥' if t == BOT else '(' + ', '.join(term(u) for u in t) + ')'


def graph(G):
    """A set of triples, sorted; ⊥ (which cl_R may contain) printed last."""
    G = sorted(t for t in G if t != BOT) + ([BOT] if BOT in G else [])
    return '∅' if not G else '{' + ', '.join(triple(t) for t in G) + '}'


def pair(p):
    A, B = p
    return f"⟨{graph(A)}, {graph(B)}⟩"


def pair_key(p):
    A, B = p
    return (len(A), sorted(A), len(B), sorted(B))


def pairs(F):
    """The pairs of a generating set, one per line, in a fixed order."""
    return '\n'.join(pair(p) for p in sorted(F, key=pair_key))


def rule(r):
    prem, conc = r
    lhs = '{' + ', '.join(triple(t) for t in prem) + '}' if prem else '∅'
    return f"{lhs} → {triple(conc)}"


def regime(R):
    return '\n'.join(rule(r) for r in R)


def mapping(mu):
    return '{' + ', '.join(f"{term(b)} ↦ {v}" for b, v in sorted(mu.items())) + '}' if mu else '{} (ground)'


def why(closure, p):
    """Restate the tests of frame.make_good for one pair and say which one
    decided: returns (verdict, reason)."""
    Gam, Del = p
    if Gam & Del:
        t = sorted(Gam & Del)[0]
        return True, f"{triple(t)} ∈ Γ ∩ Δ  (I_C, Definition 8)"
    cl = closure(Gam)
    if BOT in cl:
        return True, "⊥ ∈ cl_R(Γ): Γ is R-inconsistent  (Definition 13)"
    hit = sorted(Del & cl)
    if hit:
        return True, f"{triple(hit[0])} ∈ Δ ∩ cl_R(Γ)  (Definition 13)"
    return False, (f"Γ ∩ Δ = ∅, ⊥ ∉ cl_R(Γ), and Δ ∩ cl_R(Γ) = ∅; "
                   f"cl_R(Γ) ∖ Γ = {graph(cl - Gam)}")


def report(closure, F, limit=None, only_failures=False):
    """Print each pair of F with its verdict and reason; return whether all
    pairs are in I_R. `limit` caps the number of lines printed."""
    ok = True; shown = 0; hidden = 0
    for p in sorted(F, key=pair_key):
        good, reason = why(closure, p)
        ok = ok and good
        if only_failures and good:
            continue
        if limit is not None and shown >= limit:
            hidden += 1; continue
        print(f"  {'✓' if good else '✗'} {pair(p)}\n      {reason}")
        shown += 1
    if hidden:
        print(f"  … {hidden} more pairs not shown")
    return ok


def union_labels(Gam, labelled):
    """Which of the labelled instances (label, graph) are contained in Γ —
    used to describe a Lemma-3 union ⋃_{ν∈x} ν(G) by its x."""
    return [lab for lab, g in labelled if g <= Gam]


def verdict_line(label, iss, def4):
    return f"{label:40s} semantics {str(iss):5s}  rules {str(def4):5s}  {'agree' if iss == def4 else 'DISAGREE'}"


def write_log(path, lines):
    """Append-free write of a plain-text log for results/ (one line per case)."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n')
    print(f"wrote {path} ({len(lines)} lines)")
