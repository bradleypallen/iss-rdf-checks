"""End-to-end: the semantics' verdict vs. materialize-and-query with a deployed
reasoner (owlrl 7.6: RDFS_Semantics = RDF/RDFS entailment patterns,
OWLRL_Semantics = OWL 2 RL/RDF rules incl. the false-concluding ones, which
owlrl records as error triples). Axiomatic triples are switched off on both
sides, so the regime tested is the rule part.

Def 4 side (the practice):  materialize G with owlrl, blank nodes left as they
  are; inconsistent  or  SPARQL ASK H over the result (Def 3, mu into I∪B∪L).

Semantics side (Defs 11, 13, 14, pruned by monotonicity as in
  check_recovery_2bn_fast.py, and on the negative side by the observation
  that "every choice of one triple per mu hits cl(Γ)" iff "some mu has
  mu(H) ⊆ cl(Γ)"):  for every ground instance Γ = ν(G) over N,
  Γ inconsistent  or  some mu: bnodes(H) → N has mu(H) ⊆ cl(Γ).
  N = names(G) ∪ names(H) ∪ V ∪ {spare}; owlrl is the closure oracle here too.

What this tests that the small-universe check could not: the deployed rule
set's behaviour on blank nodes and inconsistency (uniformity of the real
regime, the Skolem step of Lemma 7 against a real materializer)."""
import random, sys, time, itertools, signal
class CaseTimeout(Exception): pass
def _alarm(*a): raise CaseTimeout()
signal.signal(signal.SIGALRM, _alarm)
from rdflib import Graph, URIRef, BNode, Namespace, RDF, RDFS
from owlrl import DeductiveClosure, RDFS_Semantics, OWLRL_Semantics

EX = Namespace("http://ex.org/"); OWL = Namespace("http://www.w3.org/2002/07/owl#")
ERR = URIRef("http://www.daml.org/2002/03/agents/agent-ont#error")

V_RDFS = [RDF.type, RDF.Property, RDF.first, RDF.rest, RDF.nil, RDF.List, RDF.Statement,
          RDF.subject, RDF.predicate, RDF.object, RDF.value, RDF.Seq, RDF.Bag, RDF.Alt,
          RDFS.Resource, RDFS.Class, RDFS.subClassOf, RDFS.subPropertyOf, RDFS.domain,
          RDFS.range, RDFS.Literal, RDFS.Datatype, RDFS.Container,
          RDFS.ContainerMembershipProperty, RDFS.member, RDFS.seeAlso, RDFS.isDefinedBy,
          RDFS.comment, RDFS.label]
V_OWL = V_RDFS + [OWL.sameAs, OWL.differentFrom, OWL.disjointWith, OWL.equivalentClass,
                  OWL.equivalentProperty, OWL.inverseOf, OWL.Nothing, OWL.Thing, OWL.Class,
                  OWL.FunctionalProperty, OWL.InverseFunctionalProperty, OWL.SymmetricProperty,
                  OWL.AsymmetricProperty, OWL.TransitiveProperty, OWL.IrreflexiveProperty,
                  OWL.propertyDisjointWith, OWL.AllDisjointClasses, OWL.members,
                  OWL.NegativePropertyAssertion, OWL.sourceIndividual, OWL.assertionProperty,
                  OWL.targetIndividual, OWL.hasValue, OWL.someValuesFrom, OWL.allValuesFrom,
                  OWL.onProperty, OWL.intersectionOf, OWL.unionOf, OWL.complementOf,
                  OWL.oneOf, OWL.hasKey, OWL.maxCardinality, OWL.propertyChainAxiom]

IND = [EX.a, EX.b, EX.C, EX.D, EX.p, EX.q]
PRED_RDFS = [RDF.type, RDFS.subClassOf, RDFS.subPropertyOf, RDFS.domain, RDFS.range, EX.p, EX.q]
PRED_OWL = PRED_RDFS + [OWL.sameAs, OWL.differentFrom, OWL.disjointWith, OWL.equivalentClass,
                        OWL.inverseOf, OWL.propertyDisjointWith]
OBJ_OWL = [OWL.Nothing, OWL.FunctionalProperty, OWL.SymmetricProperty, OWL.TransitiveProperty,
           OWL.IrreflexiveProperty, OWL.AsymmetricProperty]
SPARE = EX.s
BX, BY = BNode('x'), BNode('y')

def gen(rng, size, bn, owl):
    G = set()
    preds = PRED_OWL if owl else PRED_RDFS
    objs = IND + (OBJ_OWL if owl else [])
    while len(G) < size:
        s = bn if (bn is not None and rng.random() < 0.5) else rng.choice(IND)
        o = bn if (bn is not None and rng.random() < 0.3) else rng.choice(objs)
        G.add((s, rng.choice(preds), o))
    return frozenset(G)

def close(G, sem):
    g = Graph()
    for t in G: g.add(t)
    DeductiveClosure(sem, axiomatic_triples=False, datatype_axioms=False).expand(g)
    inconsistent = any(True for _ in g.triples((None, ERR, None)))
    g.remove((None, ERR, None))
    return g, inconsistent

def ask(g, H, values=None):
    if not H: return True
    def s(t):
        return '?' + str(t) if isinstance(t, BNode) else f'<{t}>'
    pat = ' . '.join(f'{s(a)} {s(b)} {s(c)}' for (a, b, c) in sorted(H, key=str))
    vals = ''
    if values is not None:
        vs = sorted({str(t) for tr in H for t in tr if isinstance(t, BNode)})
        vals = ' '.join(f'VALUES ?{v} {{ {" ".join(f"<{n}>" for n in values)} }}' for v in vs)
    return bool(g.query(f'ASK {{ {vals} {pat} }}').askAnswer)

def def4_side(G, H, sem):
    g, inc = close(G, sem)
    return inc or ask(g, H)

def iss_side(G, H, sem, N):
    bn = sorted({t for tr in G for t in tr if isinstance(t, BNode)}, key=str)
    for img in itertools.product(N, repeat=len(bn)):
        nu = dict(zip(bn, img))
        Gam = frozenset(tuple(nu.get(t, t) for t in tr) for tr in G)
        g, inc = close(Gam, sem)
        if inc: continue
        if not ask(g, H, values=N): return False
    return True

def run(seed, owl, n_cases):
    rng = random.Random(seed)
    sem = OWLRL_Semantics if owl else RDFS_Semantics
    V = set(V_OWL if owl else V_RDFS)
    g0, _ = close(frozenset(), sem)                  # V must contain every IRI the regime's
    V |= {x for tr in g0 for x in tr if isinstance(x, URIRef)}   # axiomatic rules introduce
    stats = dict(cases=0, entail=0, inconsistent=0, bnG=0, bnH=0, mismatch=0)
    t0 = time.time()
    for i in range(n_cases):
        G = gen(rng, rng.randint(1, 4), BX if rng.random() < 0.7 else None, owl)
        if owl and rng.random() < 0.5:               # seed a candidate clash (false-concluding rules)
            x = BX if rng.random() < 0.6 else rng.choice(IND[:2])
            clash = rng.choice([
                {(x, OWL.sameAs, EX.b), (x, OWL.differentFrom, EX.b)},
                {(EX.C, OWL.disjointWith, EX.D), (x, RDF.type, EX.C), (x, RDF.type, EX.D)},
                {(x, RDF.type, OWL.Nothing)},
                {(EX.p, RDF.type, OWL.IrreflexiveProperty), (x, EX.p, x)},
                {(EX.p, RDF.type, OWL.AsymmetricProperty), (x, EX.p, EX.b), (EX.b, EX.p, x)},
                {(EX.p, OWL.propertyDisjointWith, EX.q), (x, EX.p, EX.b), (x, EX.q, EX.b)},
            ])
            G = frozenset(set(G) | set(rng.sample(sorted(clash, key=str), rng.randint(max(1, len(clash) - 1), len(clash)))))
        if rng.random() < 0.5:                       # H drawn from the closure of G, so entailments occur
            g, _ = close(G, sem)
            pool = [t for t in g if not isinstance(t[2], BNode) or t[2] in {BX}]
            pool = [t for t in pool if t[1] in (PRED_OWL if owl else PRED_RDFS)] or list(g)
            pool = sorted(pool, key=str)             # rdflib's iteration order is hash-seed dependent
            H = set(rng.sample(pool, min(len(pool), rng.randint(1, 2))))
            if rng.random() < 0.6 and H:               # blank out one term
                (a_, b_, c_) = rng.choice(sorted(H, key=str)); H.discard((a_, b_, c_))
                H.add((BY, b_, c_) if rng.random() < 0.5 else (a_, b_, BY))
            H = frozenset(tuple(BY if u == BX else u for u in tr) for tr in H)   # H's blank node is its own
        else:
            H = gen(rng, rng.randint(0, 2), BY if rng.random() < 0.6 else None, owl)
        names = {t for tr in G | H for t in tr if not isinstance(t, BNode)}
        N = sorted(names | set(V) | {SPARE}, key=str)
        try:
            signal.alarm(30)
            a = iss_side(G, H, sem, N); b = def4_side(G, H, sem)
            signal.alarm(0)
        except AttributeError as e:                  # owlrl bug on generalized input (x.value on an IRI)
            signal.alarm(0); stats['owlrl_crash'] = stats.get('owlrl_crash', 0) + 1
            continue
        except CaseTimeout:                          # owlrl blow-up; recorded, not judged
            stats['timeout'] = stats.get('timeout', 0) + 1
            print("TIMEOUT", sorted(G, key=str), sorted(H, key=str), flush=True)
            continue
        _, inc = close(G, sem)
        stats['cases'] += 1; stats['entail'] += b; stats['inconsistent'] += inc
        stats['bnG'] += any(isinstance(t, BNode) for tr in G for t in tr)
        stats['bnH'] += any(isinstance(t, BNode) for tr in H for t in tr)
        if a != b:
            stats['mismatch'] += 1
            print("MISMATCH", 'OWL' if owl else 'RDFS', sorted(G, key=str), sorted(H, key=str), a, b, flush=True)
        if (i + 1) % 10 == 0:
            print(f"[{'OWL' if owl else 'RDFS'} seed {seed}] {stats} {time.time()-t0:.0f}s", flush=True)
    print("DONE", stats, flush=True)
    return stats

if __name__ == '__main__':
    run(int(sys.argv[1]), sys.argv[2] == 'owl', int(sys.argv[3]))
