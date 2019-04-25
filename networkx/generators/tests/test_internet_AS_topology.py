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


class TestInternetASTopology():
    def test_number_of_nodes(self):
        # balanced_tree(r,h) is a tree with (r**(h+1)-1)/(r-1) edges
        g = internet_AS_graph(1000)
        assert_equal(len(g), 1000)
        assert_equal(len([n for n in g.nodes(data=True) if n[1]["type"]
                         == "T"]), 6)
        assert_equal(len([n for n in g.nodes(data=True) if n[1]["type"]
                         == "M"]), 149)
        assert_equal(len([n for n in g.nodes(data=True) if n[1]["type"]
                         == "CP"]), 49)
        assert_equal(len([n for n in g.nodes(data=True) if n[1]["type"]
                         == "C"]), 796)
