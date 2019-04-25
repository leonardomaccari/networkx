"""
Internet AS graph.
"""
#    Copyright (C) 2019 by
#    Leonardo Maccari <maccari@disi.unitn.it>
#    All rights reserved.
#    BSD license.
__author__ = """\n""".join(['Leonardo Maccari <maccari@disi.unitn.it>'])
__all__ = ['internet_AS_graph']

import networkx as nx
from networkx.utils import py_random_state


@py_random_state(16)
def internet_AS_graph(n, nt=6, nm=None, ncp=None, nc=None,
                      dm=None, dcp=None, dc=None, pm=None,
                      pcp_m=None, pcp_cp=None, tm=0.375,
                      tcp=0.375, tc=0.125, m_ratio=0.15,
                      cp_ratio=0.05, seed=None):
    """Returns a graph that reproduces the topology of the Internet ASs.

    Parameters
    ----------
    n: int
        The total number of nodes (should be in the range 1000-10000)

    nt: int
        The number of T nodes, defaults to 6

    nm: int
        The number of M nodes, defaults to m_ratio*n (0.15*n)

    ncp: int
        The number of CP nodes, defaults to cp_ratio*n (0.05*n)

    nc: int
        The number of C nodes, defaults to n - nt - nm - ncp, (approx 0.80n)

    dm: int
        Average MHD of the M nodes, defaults to 0.0001*(2+2.5*n)

    dcp: int
        Average MHD of CP noses, defaults to 0.0001*(2+1.5*n)

    dc: int
        Average MHD of C nodes, defaults to 0.00001*(1+5*n)

    pm: int
        Average M-M peering degree, defaults to 0.0001*(1+2*n)

    pcp_m: int
        Average CP-M peering degree, defaults to 0.0001*(0.2+2*n)

    pcp_cp: int
        Average CP-CP peering degree, defaults tp 0.00001*(0.05 + 5*n)

    tm: float
        Probability that M's provider is T, defaults to 0.375

    tcp: int
        Probability that CP's provider is T, defaults to 0.375

    tc: int
        Probability that C's provider is T, defaults to 0.125

    m_ratio: float
        The ratio of M nodes over the total

    cp_ratio: float
        The ratio of CP nodes over the total

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Notes
    -----

    The algorithm principles are described in the paper "On the scalability of
    BGP: the roles of topology growth", by Ahmed Elmokashfi, Amund Kvalbein,
    Constantine Dovrolis, JSAC 2010.
    """

    g = nx.Graph()
    if not nm:
        nm = int(m_ratio*(n-nt))
    if not ncp:
        ncp = int(cp_ratio*(n-nt))
    if not nc:
        nc = n - nt - ncp - nm
    g.add_nodes_from(range(nt), type="T")
    g.add_nodes_from(range(nt, nm + nt), type="M")
    g.add_nodes_from(range(nt + nm, nm + nt + ncp), type="CP")
    g.add_nodes_from(range(nt + nm + ncp, nt + nm + ncp + nc), type="C")

    return g
