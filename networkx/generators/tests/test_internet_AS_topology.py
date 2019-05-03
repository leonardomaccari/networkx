#!/usr/bin/env python
"""
====================
Generators - internet_AS_topology
====================

Unit tests for internet_AS_topology.py
"""
import itertools

from nose.tools import *
import networkx as nx
from networkx import *
from networkx.testing import assert_edges_equal
from networkx.testing import assert_nodes_equal


def almost_eq_fractions(x, y, perc=5.0):
    if x == y:
        return True
    if abs(x - y) < perc/100:
        return True
    return False


class TestInternetASTopology():
    def test_number_of_nodes(self):
        g = internet_as_graph(1000)
        assert_equal(len(g), 1000)
        assert_equal(len([n for n in g.nodes(data=True) if n[1]["type"]
                         == "T"]), 6)
        assert_equal(len([n for n in g.nodes(data=True) if n[1]["type"]
                         == "M"]), 149)
        assert_equal(len([n for n in g.nodes(data=True) if n[1]["type"]
                         == "CP"]), 49)
        assert_equal(len([n for n in g.nodes(data=True) if n[1]["type"]
                         == "C"]), 796)

    def test_regions(self, numnodes=10000):
        g = internet_as_graph(numnodes)
        regions = ["REG"+str(i) for i in range(5)]
        r_labels = dict()
        label_numbers = dict()
        types = ["T", "M", "CP", "C"]
        nodes_number = dict()
        for t in types:
            nodes_number[t] = len([n for n in g.nodes(data=True)
                                   if n[1]["type"] == t])
        for r in regions:
            r_labels[r] = 0
            for t in types:
                label_numbers[t] = dict({(i, 0) for i in
                                        range(1, len(regions)+1)})

        for n in g.nodes(data=True):
            labels = n[1]['regions'].split("_")
            for l in r_labels:
                r_labels[l] += 1
            label_numbers[n[1]['type']][len(labels)] += 1

        assert_true(almost_eq_fractions(label_numbers["M"][1] /
                                        nodes_number["M"], 0.8))
        assert_true(almost_eq_fractions(label_numbers["M"][2] /
                                        nodes_number["M"], 0.2))
        assert_true(almost_eq_fractions(label_numbers["CP"][1] /
                                        nodes_number["CP"], 0.95))
        assert_true(almost_eq_fractions(label_numbers["CP"][2] /
                                        nodes_number["CP"], 0.05))
        assert_true(almost_eq_fractions(label_numbers["C"][1] /
                                        nodes_number["C"], 1))
        assert_true(almost_eq_fractions(label_numbers["T"][5] /
                                        nodes_number["T"], 1))

    def test_clique(self):
        g = nx.internet_as_graph(1000)
        t_nodes = [n[0] for n in g.nodes(data=True) if n[1]["type"] == "T"]
        sub_g = g.subgraph(t_nodes)
        assert_equal(nx.graph_clique_number(sub_g), len(t_nodes))

