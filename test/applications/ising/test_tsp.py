# This code is part of Qiskit.
#
# (C) Copyright IBM 2018, 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

""" Test Tsp class"""

import random
import numpy as np
import networkx as nx

from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import (OptimizationResult,
                                            OptimizationResultStatus)
from qiskit_optimization.applications.ising.tsp import Tsp
from qiskit_optimization.problems import (Constraint, QuadraticObjective, VarType)
from test.optimization_test_case import QiskitOptimizationTestCase


class TestTsp(QiskitOptimizationTestCase):
    """ Test Tsp class"""

    def setUp(self):
        super().setUp()
        random.seed(123)
        low = 0
        high = 100
        pos = {i: (random.randint(low, high), random.randint(low, high)) for i in range(4)}
        self.graph = nx.random_geometric_graph(4, np.hypot(high-low, high-low)+1, pos=pos)
        for u, v in self.graph.edges:
            delta = [self.graph.nodes[u]['pos'][i] - self.graph.nodes[v]['pos'][i]
                     for i in range(2)]
            self.graph.edges[u, v]['weight'] = np.rint(np.hypot(delta[0], delta[1]))

        qp = QuadraticProgram()
        for i in range(16):
            qp.binary_var()
        self.result = OptimizationResult(
            x=[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1], fval=272, variables=qp.variables,
            status=OptimizationResultStatus.SUCCESS)

    def test_to_quadratic_program(self):
        """Test to_quadratic_program"""
        tsp = Tsp(self.graph)
        qp = tsp.to_quadratic_program()
        # Test name
        self.assertEqual(qp.name, 'TSP')
        # Test variables
        self.assertEqual(qp.get_num_vars(), 16)
        for var in qp.variables:
            self.assertEqual(var.vartype, VarType.BINARY)
        # Test objective
        obj = qp.objective
        self.assertEqual(obj.sense, QuadraticObjective.Sense.MINIMIZE)
        self.assertEqual(obj.constant, 0)
        self.assertDictEqual(obj.linear.to_dict(), {})
        for edge, val in obj.quadratic.to_dict().items():
            self.assertEqual(val, self.graph.edges[edge[0]//4, edge[1]//4]['weight'])

        # Test constraint
        lin = qp.linear_constraints
        self.assertEqual(len(lin), 8)
        for i in range(4):
            self.assertEqual(lin[i].sense, Constraint.Sense.EQ)
            self.assertEqual(lin[i].rhs, 1)
            self.assertEqual(lin[i].linear.to_dict(), {4*i: 1, 4*i+1: 1, 4*i+2: 1, 4*i+3: 1})
        for i in range(4):
            self.assertEqual(lin[4+i].sense, Constraint.Sense.EQ)
            self.assertEqual(lin[4+i].rhs, 1)
            self.assertEqual(lin[4+i].linear.to_dict(), {i: 1, 4+i: 1, 8+i: 1, 12+i: 1})

    def test_interpret(self):
        """Test interpret"""
        tsp = Tsp(self.graph)
        self.assertEqual(tsp.interpret(self.result), [0, 1, 2, 3])

    def test_edgelist(self):
        tsp = Tsp(self.graph)
        self.assertEqual(tsp._edgelist(self.result), [(0, 1), (1, 2), (2, 3), (3, 0)])

    def test_random_graph(self):
        tsp = Tsp.random_graph(n=4, seed=123)
        graph = tsp.graph()
        for node in graph.nodes:
            self.assertEqual(graph.nodes[node]['pos'], self.graph.nodes[node]['pos'])
        for edge in graph.edges:
            self.assertEqual(graph.edges[edge]['weight'], self.graph.edges[edge]['weight'])
