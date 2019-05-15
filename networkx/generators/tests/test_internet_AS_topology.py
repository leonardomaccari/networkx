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


# --no-skip is bugged. Does not work properly withouth this patch
if '--no-skip' in sys.argv or 'NOSE_WITHOUT_SKIP' in os.environ:
    no_skip = True


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

    def test_number_of_nodes(self):
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
        t_nodes = [n[0] for n in self.small_g.nodes(data=True)
                   if n[1]["type"] == "T"]
        sub_g = self.small_g.subgraph(t_nodes)
        assert_equal(nx.graph_clique_number(sub_g), len(t_nodes))



class TestInternetASTopologyStats():

    @classmethod
    def setup_class(cls):
        cls.medium_g = internet_as_graph(1000)

    def test_regions(self):
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
