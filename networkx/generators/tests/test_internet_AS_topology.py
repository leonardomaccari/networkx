#!/usr/bin/env python
"""
====================
Generators - internet_AS_topology
====================

Unit tests for internet_AS_topology.py
"""
import itertools

from nose.tools import *
import sys
import os

from nose import SkipTest
import networkx as nx
from networkx import *
from networkx.testing import assert_edges_equal
from networkx.testing import assert_nodes_equal
from collections import defaultdict


# --no-skip is bugged. Does not work properly withouth this patch
if '--no-skip' in sys.argv or 'NOSE_WITHOUT_SKIP' in os.environ:
    no_skip = True
else:
    no_skip = False


def almost_eq_fractions(x, y, perc=5.0):
    if x == y:
        return True
    if abs(x - y) < perc/100:
        return True
    return False


skip_message = "Statistical tests take too much time, use --no-skip to enable"


class TestInternetASTopology():

    @classmethod
    def setup_class(cls):
        cls.small_g = internet_as_graph(1000)
        cls.peerless_g = nx.DiGraph()
        for e in cls.small_g.edges(data=True):
            if e[2]['type'] != "peer":
                cls.peerless_g.add_edge(e[0], e[1])

    def test_number_of_nodes(self):
        """ test the number of nodes """
        assert_equal(len(self.small_g), 1000)
        assert_equal(len([n for n in self.small_g.nodes(data=True)
                          if n[1]["type"] == "T"]), 6)
        assert_equal(len([n for n in self.small_g.nodes(data=True)
                          if n[1]["type"] == "M"]), 149)
        assert_equal(len([n for n in self.small_g.nodes(data=True)
                          if n[1]["type"] == "CP"]), 49)
        assert_equal(len([n for n in self.small_g.nodes(data=True)
                          if n[1]["type"] == "C"]), 796)

    def test_clique(self):
        """ test T nodes from a clique """
        t_nodes = set([n[0] for n in self.small_g.nodes(data=True)
                      if n[1]["type"] == "T"])
        sub_g = self.small_g.subgraph(t_nodes)
        # all T nodes must peer with each other
        for n in sub_g:
            neighs = set([e[1] for e in sub_g.out_edges(n)])
            assert_equal(neighs, t_nodes - set([n]))

    def test_edges_T(self):
        """ test correct T relationships """
        for n in self.small_g.nodes(data=True):
            if n[1]["type"] == "T":
                for e in self.small_g.out_edges(n[0], data=True):
                    # T nodes have outgoing links only with T nodes
                    assert_true(self.small_g.nodes[e[1]]['type'] == "T")
                    assert_true(e[2]['type'] == "peer")
                    # T nodes have only peering outgoing links
                for e in self.small_g.in_edges(n[0], data=True):
                    if self.small_g.nodes[e[0]]['type'] != "T":
                        # T nodes have only transit ingoing links
                        assert_true(e[2]['type'] == "transit")
                        assert_true(self.small_g.nodes[e[0]]['type'] != "T")

    def test_edges_M(self):
        """ test correct M relationships """
        for n in self.small_g.nodes(data=True):
            if n[1]["type"] == "M":
                for e in self.small_g.out_edges(n[0], data=True):
                    # M nodes do not buy transit from C or CP
                    if e[2]['type'] == "transit":
                        assert_true(self.small_g.nodes[e[1]]['type'] != "CP")
                        assert_true(self.small_g.nodes[e[1]]['type'] != "C")
                    # M nodes do not peer with T and C
                    if e[2]['type'] == "peer":
                        assert_true(self.small_g.nodes[e[1]]['type'] != "T")
                        assert_true(self.small_g.nodes[e[1]]['type'] != "C")
                for e in self.small_g.in_edges(n[0], data=True):
                    # M sell transit to all but T
                    if e[2]['type'] == "transit":
                        assert_true(self.small_g.nodes[e[1]]['type'] != "T")
                    # M peer only with T and M
                    if e[2]['type'] == "peer":
                        assert_in(self.small_g.nodes[e[1]]['type'],
                                  ['CP', 'M'])

    def test_edges_CP(self):
        """ test correct CP relationships """
        for n in self.small_g.nodes(data=True):
            if n[1]["type"] == 'CP':
                # CP nodes do not peer with T and C, and sell no transit
                for e in self.small_g.in_edges(n[0], data=True):
                    assert_true(e[2]['type'], 'peer')
                    assert_in(self.small_g.nodes[e[1]]['type'], ['CP', 'M'])
                for e in self.small_g.out_edges(n[0], data=True):
                    if e[2]['type'] == "peer":
                        assert_in(self.small_g.nodes[e[1]]['type'],
                                  ['CP', 'M'])
                    if e[2]['type'] == "transit":
                        assert_in(self.small_g.nodes[e[1]]['type'], ['T', 'M'])

    def test_edges(self):
        """ test all edges are labeled """
        for e in self.small_g.edges(data=True):
            assert_in(e[2]['type'], ['transit', 'peer'])

    def test_connectedness(self):
        """ test if graph is connected """
        counter = 0
        assert_true(nx.is_weakly_connected(self.small_g))
        g = self.small_g.to_undirected()
        assert_true(nx.is_connected(g))

    def test_loopfree(self):
        """ test that without peering links the graph is loop free """
        assert_true(nx.is_directed_acyclic_graph(self.peerless_g))

    def test_consistentcy(self):
        """ test that no node peers with someone in its customer tree """
        peering_relations = defaultdict(set)
        for e in self.small_g.edges(data=True):
            if e[2]["type"] == "peer":
                peering_relations[e[0]].add(e[1])
                peering_relations[e[1]].add(e[0])
        for n in peering_relations:
            sn = internet_AS_graph.find_subtree_nodes(self.peerless_g, n)
            assert_true(sn.isdisjoint(peering_relations[n]))


class TestInternetASTopologyStats():
    """ use nosetests --no-skip test_internet_AS_topology.py
        to run these tests, but they will take time """

    @classmethod
    def setup_class(cls):
        if not no_skip:
            raise SkipTest(skip_message)
        cls.medium_g = internet_as_graph(10000)

    def test_regions(self):
        """ test region distribution is close to target """
        if not no_skip:
            raise SkipTest(skip_message)
        regions = ["REG"+str(i) for i in range(5)]
        r_labels = dict()
        label_numbers = dict()
        types = ["T", "M", "CP", "C"]
        nodes_number = dict()
        for t in types:
            nodes_number[t] = len([n for n in self.medium_g.nodes(data=True)
                                   if n[1]["type"] == t])
        for r in regions:
            r_labels[r] = 0
            for t in types:
                label_numbers[t] = dict({(i, 0) for i in
                                        range(1, len(regions)+1)})

        for n in self.medium_g.nodes(data=True):
            labels = n[1]['regions'].split("_")
            for l in r_labels:
                r_labels[l] += 1
            # check no node is assigned twice to same region
            assert_equal(len(labels), len(set(labels)))
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

    # TODO add test to reasonably test the Power-law distribution of the degree
    def test_statistics(self):
        if not no_skip:
            raise SkipTest(skip_message)
        return
