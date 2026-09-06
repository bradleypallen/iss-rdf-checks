"""Lemma 1 / Definition 3 against an implementation we did not write.

For STANDARD graphs, simple entailment in the sense of Hayes & Patel-Schneider
2014 is exactly basic-graph-pattern matching in SPARQL (SPARQL 1.1 Query
§18.3, simple entailment regime): G simply entails H iff the ASK query whose
pattern is H with each blank node replaced by a variable succeeds over G.
rdflib's SPARQL engine is the reference here; our `simply_entails` (Def 3,
instance-mapping search) is what is being tested."""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.dirname(_HERE), _HERE]
import random
from rdflib import Graph, URIRef, BNode, Literal
from issrdf import simply_entails

EX = "http://ex.org/"
IRIS = ['a', 'b', 'p', 'q']
LITS = ['"1"', '"2"']

def term(t):
    if t.startswith('_'): return BNode(t[1:])
    if t.startswith('"'): return Literal(t.strip('"'))
    return URIRef(EX + t)

def gen_standard(rng, size, bn_pool):
    """Standard-syntax triples: subject IRI/bnode, predicate IRI, object anything."""
    G = set()
    while len(G) < size:
        s = rng.choice(IRIS + bn_pool)
        p = rng.choice(['p', 'q'])
        o = rng.choice(IRIS + bn_pool + LITS)
        G.add((s, p, o))
    return frozenset(G)

def to_rdflib(G):
    g = Graph()
    for (s, p, o) in G:
        g.add((term(s), term(p), term(o)))
    return g

def sparql_entails(G, H):
    if not H:
        return True
    g = to_rdflib(G)
    def var(t):
        if t.startswith('_'): return '?' + t[1:]
        if t.startswith('"'): return t
        return f'<{EX}{t}>'
    pattern = ' . '.join(f'{var(s)} {var(p)} {var(o)}' for (s, p, o) in sorted(H))
    return bool(g.query(f'ASK {{ {pattern} }}').askAnswer)

def run(seed, n=3000):
    rng = random.Random(seed)
    agree = ent = 0
    for i in range(n):
        G = gen_standard(rng, rng.randint(0, 4), ['_x', '_y'])
        H = gen_standard(rng, rng.randint(0, 3), ['_u', '_v'])
        a = simply_entails(G, H); b = sparql_entails(G, H)
        ent += b
        if a != b:
            print("LEMMA 1 / DEF 3 MISMATCH", sorted(G), sorted(H), a, b)
        else:
            agree += 1
    print(f"seed {seed}: {n} standard-graph pairs, {ent} entailments, {agree} agreements, {n-agree} mismatches")

if __name__ == '__main__':
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
