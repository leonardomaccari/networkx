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


@py_random_state(19)
def internet_AS_graph(n, nt=6, nm=None, ncp=None, nc=None,
                      dm=None, dcp=None, dc=None, pm=None,
                      pcp_m=None, pcp_cp=None, tm=0.375,
                      tcp=0.375, tc=0.125, m_ratio=0.15,
                      cp_ratio=0.05, regions=5,
                      m_tworeg=0.2, cp_tworeg=0.05,
                      seed=None):
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

    regions: int
        The number of Regions in the graph (defaults to 5)

    m_tworeg: float
        The fraction of M nodes in two regions (defaults to 0.2)

    cp_tworeg: float
        The fraction of CP nodes in two regions (defaults to 0.05)

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
    r_labels = ["REG"+str(i) for i in range(regions)]
    r_set = dict()
    for l in r_labels:
        r_set[l] = set()
    all_regions = "_".join(sorted(r_labels))
    g.add_nodes_from(range(nt), type="T", regions="_".join(r_labels))
    for i in range(nt, nm + nt):
        label = r_labels[i % len(r_labels)]
        if seed.random() < m_tworeg:  # 20% of M nodes are in 2 regions
            label += "_" + r_labels[seed.randint(0, len(r_labels) - 1)]
        g.add_node(i, type="M", regions=label)
    for i in range(nt + nm, nt + nm + ncp):
        label = r_labels[i % len(r_labels)]
        if seed.random() < cp_tworeg:  # 5% of CP nodes are in 2 regions
            label += "_" + r_labels[seed.randint(0, len(r_labels) - 1)]
        g.add_node(i, type="CP", regions=label)
    for i in range(nt + nm + ncp, nt + nm + ncp + nc):
        label = r_labels[i % len(r_labels)]
        g.add_node(i, type="C", regions=label)

    #for node g.nodes(data=True):
    #    r_set[node[1]['']]
    #for l in t_labels:
    #    r_set[l].add()

    return g
