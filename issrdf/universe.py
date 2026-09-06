"""Convention 1 and Definition 12: the finite vocabulary fragment N over which
the frame is built, and admissibility of N for a pair of graphs and a regime.

Conventions of the code base: blank nodes are strings starting with '_';
every other term is an IRI (literals never occur in the universes used by the
checks, so "IRIs of N" below is all of N).
"""
from dataclasses import dataclass
from .regime import bnodes, names


@dataclass(frozen=True)
class Universe:
    """Convention 1 (Finite vocabulary fragment).  "Fix a finite N ⊆ I ∪ L,
    the vocabulary fragment over which the frame is built. ... N constrains
    only what the frame, its lexicon, and its models range over."

    V      the regime's vocabulary (Definition 4), V ⊆ N (Definition 13)
    INDIV  individual names available to G and H
    SPARE  IRIs reserved for the injection of Definition 12 (Skolem names)
    BN_G   blank nodes a random G may use;  BN_H  likewise for H
    N      the fragment itself: INDIV + V + SPARE, in that order (the order
           fixes the enumeration order of instance mappings, nothing else)

    Only these functions read a Universe: make_closure (V), instances and
    the content functions (N), the two entailment tests (N), and the random
    generators in checks/generate.py (INDIV, V). The algebra of roles and the
    frame test are universe-free.
    """
    V: tuple
    INDIV: tuple
    SPARE: tuple = ()
    BN_G: tuple = ('_x',)
    BN_H: tuple = ('_y',)

    @property
    def N(self):
        return self.INDIV + self.V + self.SPARE

    def admissible(self, G, H=frozenset()):
        """Definition 12 (Admissible fragment).  "A finite N ⊆ I ∪ L is
        admissible for G, H and R iff names(G) ∪ names(H) ∪ V ⊆ N and there is
        an injection from bnodes(G) into the IRIs in N ∖ (names(G) ∪ names(H)
        ∪ V)."  Admissible for G alone means admissible for G and ∅.

        Not asserted by the constructor: Theorem 1 does not assume it, and
        check_theorem1.py runs with SPARE = (). The closure-regime checks
        assert it for every case."""
        used = names(G) | names(H) | set(self.V)
        if not used <= set(self.N):
            return False
        free = set(self.N) - used
        return len(bnodes(G)) <= len(free)

    def __repr__(self):
        return (f"Universe(V={self.V}, INDIV={self.INDIV}, SPARE={self.SPARE}, "
                f"BN_G={self.BN_G}, BN_H={self.BN_H})  # N = {self.N}")
