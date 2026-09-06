"""issrdf — the definitions of *Implication-Space Semantics for RDF*, as code.

Module ↔ paper:
  universe.py   Convention 1, Definition 12      the finite fragment N and admissibility
  regime.py     Definitions 1–4                  triples, graphs, simple entailment, regimes, cl_R
  roles.py      Definition 6 (Hlobil 2026 Def. 10) adjunction, symjunction, power-symjunction, roles
  content.py    Definitions 9–11                 contents of ground and blank-node graphs
  frame.py      Definitions 7, 8, 13–15          the base, the frame, Herbrand membership, entailment

Everything here is computed from the definitions; no lemma of the paper is
used (CLAUDE.md, "The one rule"). See DEFINITIONS.md for the table.
"""
from .universe import Universe
from .regime import (BOT, VARS, is_bnode, is_var, terms, bnodes, names, inst,
                     make_closure, simply_entails, r_inconsistent, r_entails)
from .roles import EMPTY, UNIT, adj, adj_iter, adj_many, symj, nabla, pos_role, neg_role
from .content import ground_content, instances, content_pos, content_neg, content
from .frame import make_good, iss_entails, iss_incoherent, rsr

__all__ = [n for n in dir() if not n.startswith('_')]
