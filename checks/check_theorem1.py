"""Theorem 1 with non-injective bearer maps, exhaustive over bearer maps.

Setting: N = {a, p}, so 8 ground triples. A base B over N is Containment plus a
random set of pairs (no monotonicity, no Cut). Bearer set 𝔹 of size 2 or 3;
EVERY map 𝔅: triples → 𝔹 is tried (256 resp. 6561 maps, almost all
non-injective). For each 𝔅 the fit frames are exactly the supersets of
   I_min(𝔅) = I_C(𝔹) ∪ { <𝔅Γ, 𝔅Δ> : Γ |~_B Δ },
and content entailment is monotone in the frame, so checking at I_min(𝔅)
checks every fit model with that bearer map.

Theorem 1 claims: G |~ H in the Herbrand model  iff  G |~ H in every fit model.
  'only if' (Herbrand ⇒ every fit model): tested for every 𝔅.
  'if'      (every fit model ⇒ Herbrand): Herbrand is itself fit (identity 𝔅),
            so it is the identity map's row of the same test.
Contents by Defs 10/11 with the model's bearer map; blank nodes allowed."""
import itertools, random, sys
import check_recovery as C

C.V = ('p',); C.INDIV = ('a',); C.SPARE = (); C.N = ('a', 'p')
C.BN_G = ('_x',); C.BN_H = ('_y',)
TRIPLES = [t for t in itertools.product(C.N, repeat=3)]
E = frozenset()

def subsets(xs):
    xs = list(xs)
    return [frozenset(c) for r in range(len(xs) + 1) for c in itertools.combinations(xs, r)]

TSETS = subsets(TRIPLES)                       # 256 subsets of ground triples

def random_base(rng, density):
    """Only the non-Containment pairs; Containment is implicit (overlap test)."""
    return frozenset((G, D) for G in TSETS for D in TSETS if not (G & D) and rng.random() < density)

def content_pairs(G, H, bmap):
    """Generating pairs of [[G]]+ ⊔ [[H]]- in a model with bearer map bmap (Defs 10, 11)."""
    def pos(t): return frozenset({(frozenset({bmap[t]}), E)})
    def neg(t): return frozenset({(E, frozenset({bmap[t]}))})
    P = C.nabla(C.adj_many(pos(t) for t in sorted(g)) for g in C.instances(G))
    Nn = C.adj_many(C.nabla(neg(t) for t in sorted(h)) for h in C.instances(H))
    return C.adj(P, Nn)

def run(seed, nbearers, n_bases=3, n_graphs=10):
    rng = random.Random(seed)
    bearers = list(range(nbearers))
    IC = frozenset((A, B) for A in subsets(bearers) for B in subsets(bearers) if A & B)
    maps = [dict(zip(TRIPLES, img)) for img in itertools.product(bearers, repeat=len(TRIPLES))]
    ident = {t: t for t in TRIPLES}
    checked = viol = herb_yes = 0
    for _ in range(n_bases):
        B = random_base(rng, rng.choice([0.05, 0.2, 0.5]))
        I_herb = lambda p: bool(p[0] & p[1]) or p in B          # Def 14: I_C ∪ B
        graphs = [C.gen_graph(rng, rng.randint(0, 2), C.BN_G) for _ in range(n_graphs)]
        hs = [C.gen_graph(rng, rng.randint(0, 2), C.BN_H) for _ in range(n_graphs)]
        yes = [(G, H) for G in graphs for H in hs
               if all(I_herb(p) for p in content_pairs(G, H, ident))]
        herb_yes += len(yes)
        for bm in maps:                               # I_min once per bearer map
            Bimg = frozenset((frozenset(bm[t] for t in g), frozenset(bm[t] for t in d)) for (g, d) in B)
            Imin = lambda p: bool(p[0] & p[1]) or p in Bimg
            for G, H in yes:
                checked += 1
                if not all(Imin(p) for p in content_pairs(G, H, bm)):
                    viol += 1
                    print("THEOREM 1 VIOLATION", sorted(G), sorted(H), bm)
    print(f"seed {seed}, |B|={nbearers}: Herbrand-yes cases {herb_yes}, "
          f"(case, bearer map) checks {checked}, violations {viol}")

if __name__ == '__main__':
    run(int(sys.argv[1]), int(sys.argv[2]))
