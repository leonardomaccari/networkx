"""
Internet AS graph.
"""
#    Copyright (C) 2019 by
#    Leonardo Maccari <maccari@disi.unitn.it>
#    All rights reserved.
#    BSD license.
__author__ = """\n""".join(['Leonardo Maccari <maccari@disi.unitn.it>'])
__all__ = ['internet_as_graph']

import networkx as nx
from networkx.utils import py_random_state
from networkx.generators.random_graphs import _random_subset


@py_random_state(5)
def pref_attach(g, source, num_targets, node_region_lists, region_list, seed,
                peerless_g, label="transit", pa_with_edge_type=True):
    """ Attach a new node to the network with preferential attachment

    g: nx Graph
    source: node
    num_targets: int
        How many link to add to the new node
    node_region_lists:
        dictionary or lists of valid nodes, keyed by region
    seed:
        random seed
    peerless_g:
        graph without peer links
    region_list:
        list of regions that we can attach to
    label:
        add edges with this label
    ba_with_edge_type:
        when computing the degree, restrict to the edges of type "label" """

    if not num_targets:
        return
    nodes = set()
    # take all nodes in the valid regions, without copies
    for region in region_list:
        nodes.update(node_region_lists[region])

    # create an array with nodes repeated by their degree
    nodes_w_copies = []
    num_candidates = 0

    subtree_nodes = find_subtree_nodes(peerless_g, source)
    for n in nodes:
        if n in subtree_nodes:
            continue
        if not pa_with_edge_type:
            deg = g.in_degree(n)
        else:
            deg = len(list(filter(lambda x: x[2]['type'] == label,
                      g.in_edges(n, data=True))))
        # at the initial stage, T nodes have no customers, and thus,
        # the chances they are chosen in pref. attachment are 0
        # we initialize them with probability larger than zero so
        # they start being populated with customers
        if not deg and g.nodes[n]['type'] == 'T':
            deg = 1
        if deg:
            nodes_w_copies.extend([n]*deg)
            num_candidates += 1
    # choose randomly on the set of nodes with repetition
    if not nodes_w_copies:
        return
    targets = _random_subset(nodes_w_copies, min(num_targets,
                                                 num_candidates),
                             seed)
    g.add_edges_from(zip([source]*num_targets, targets), type=label)
    if label != "peer":
        peerless_g.add_edges_from(zip([source]*num_targets, targets),
                                  type=label)


def find_subtree_nodes(g, target):
    """ This check is needed because we have to avoid loops. Node x can not
    be a customer of (or peer with) some other node that is in its customer
    tree. It is very expensive, though, so something smarter may be done """
    subtree_nodes = [n for n in g.nodes() if nx.has_path(g, n, target)]
    return set(subtree_nodes)


@py_random_state(19)
def internet_as_graph(n, nt=6, nm=None, ncp=None, nc=None,
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

    g = nx.DiGraph()
    if not nm:
        nm = int(m_ratio*(n-nt))
    if not ncp:
        ncp = int(cp_ratio*(n-nt))
    if not nc:
        nc = n - nt - ncp - nm
    r_labels = ["REG"+str(i) for i in range(regions)]
    node_lists = dict()
    for k in ["T", "M", "CP", "C"]:
        node_lists[k] = dict([(l, []) for l in r_labels])

    r_set = dict()
    for l in r_labels:
        r_set[l] = set()
    all_regions = "_".join(sorted(r_labels))
    g.add_nodes_from(range(nt), type="T", regions="_".join(r_labels))
    node_lists["T"] = dict((l, [i for i in range(nt)]) for l in r_set)

    for i in range(nt, nm + nt):
        first_region = i % len(r_labels)
        label = r_labels[first_region]
        node_lists["M"][label].append(i)
        if seed.random() < m_tworeg:  # 20% of M nodes are in 2 regions
            second_label = seed.choice(
                r_labels[:first_region] + r_labels[first_region+1:])
            label += "_" + second_label
            node_lists["M"][second_label].append(i)
        g.add_node(i, type="M", regions=label)

    for i in range(nt + nm, nt + nm + ncp):
        first_region = i % len(r_labels)
        label = r_labels[first_region]
        node_lists["CP"][label].append(i)
        if seed.random() < cp_tworeg:  # 5% of CP nodes are in 2 regions
            second_label = seed.choice(
                r_labels[:first_region] + r_labels[first_region+1:])
            label += "_" + second_label
            node_lists["CP"][second_label].append(i)
        g.add_node(i, type="CP", regions=label)

    for i in range(nt + nm + ncp, nt + nm + ncp + nc):
        first_region = i % len(r_labels)
        label = r_labels[first_region]
        g.add_node(i, type="C", regions=label)
        node_lists["C"][label].append(i)

    peerless_g = g.copy()
    # a clique of T nodes
    for i in range(nt):
        for j in range(i + 1, nt):
            g.add_edge(i, j, type="peer")
            g.add_edge(j, i, type="peer")

    # Add transit links

    d_m = 2 + n*2.5/10000
    t_m = 0.375
    d_cp = 2 + n*1.5/10000
    t_cp = 0.375
    d_c = 1 + n*5.0/100000
    t_c = 0.125

    for i in range(nt, n):
        regions = g.nodes(data=True)[i]["regions"].split("_")
        node_type = g.nodes(data=True)[i]["type"]
        if node_type == "M":
            deg = max(1, round(seed.random()*d_m*2))
            prop_t = round(deg*t_m)
        elif node_type == "CP":
            deg = max(1, round(seed.random()*d_cp*2))
            prop_t = round(deg*t_cp)
        else:
            deg = max(1, round(seed.random()*d_c*2))
            prop_t = round(deg*t_c)
        deg_t = 0
        deg_m = 0
        for j in range(deg):
            if seed.random() < prop_t:
                deg_t += 1
            else:
                deg_m += 1
        pref_attach(g, i, deg_m, node_lists["M"], regions, seed, peerless_g)
        # early M nodes do not have other M nodes to attach to, we compensate
        # with T nodes
        if g.out_degree(i) < deg_m:
            deg_t += deg_m - g.out_degree(i)
        pref_attach(g, i, deg_t, node_lists["T"], regions, seed, peerless_g)

        # two unclear things from the paper:
        # -  we assume CP nodes can have transit with both T and M
        # -  we assume the degree is uniformely distributed for C
        #    as in the M and CP nodes

    # we now add peering links
    p_m = 1 + n*2.0/10000
    p_cp_m = 0.2 + n*2.0/10000
    p_cp_cp = 0.05 + n*5.0/100000

    for i in range(nt, nt + nm + ncp):
        node_type = g.nodes(data=True)[i]["type"]
        regions = g.nodes(data=True)[i]["regions"].split("_")
        if node_type == "M":
            deg_m = max(0, round(seed.random()*p_m*2))
            if deg_m:
                pref_attach(g, i, deg, node_lists["M"], regions, seed,
                            peerless_g, label="peer")
        elif node_type == "CP":
            deg_m = max(0, round(seed.random()*p_cp_m*2))
            deg_cp = max(0, round(seed.random()*p_cp_cp*2))
            # CP nodes are attached with a uniform probability
            potential_targets_m = []
            potential_targets_cp = []
            if deg_m:
                for r in regions:
                    potential_targets_m += node_lists['M'][r]
            if deg_cp:
                for r in regions:
                    potential_targets_cp += node_lists['CP'][r]
            subtree_nodes = find_subtree_nodes(peerless_g, i)
            ss = len(subtree_nodes)
            for n in potential_targets_cp:
                if n in subtree_nodes:
                    potential_targets_cp.remove(n)
                    ss -= 1
                    if not ss:
                        break
            ss = len(subtree_nodes)
            for n in potential_targets_m:
                if n in subtree_nodes:
                    potential_targets_m.remove(n)
                    ss -= 1
                    if not ss:
                        break

            targets = _random_subset(potential_targets_m, deg_m, seed)
            g.add_edges_from(zip([i]*len(targets), targets), type="peer")
            targets = _random_subset(potential_targets_cp, deg_cp, seed)
            g.add_edges_from(zip([i]*len(targets), targets), type="peer")

    return g
