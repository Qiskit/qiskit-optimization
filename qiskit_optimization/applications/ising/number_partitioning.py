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

"""An application class for the number partitioning."""

import copy
from typing import List

from docplex.mp.model import Model

from qiskit_optimization.algorithms import OptimizationResult
from qiskit_optimization.problems.quadratic_program import QuadraticProgram
from .base_optimization_application import BaseOptimizationApplication


class NumberPartitioning(BaseOptimizationApplication):
    """Convert a number partitioning problem [1] instance
    into a :class:`~qiskit_optimization.problems.QuadraticProgram`

    References:
        [1]: "Partition problem",
        https://en.wikipedia.org/wiki/Partition_problem
    """

    def __init__(self, number_set: List[int]) -> None:
        """
        Args:
            number_set: A list of intergers
        """
        self._number_set = number_set

    def to_quadratic_program(self) -> QuadraticProgram:
        """Convert a number partitioning problem instance into a
        :class:`~qiskit_optimization.problems.QuadraticProgram`

        Returns:
            The :class:`~qiskit_optimization.problems.QuadraticProgram` created
            from the number partitioning problem instance.
        """
        mdl = Model(name='Number partitioning')
        x = {i: mdl.binary_var(name='x_{0}'.format(i)) for i in range(len(self._number_set))}
        mdl.add_constraint(mdl.sum(num * (-2 * x[i] + 1)
                                   for i, num in enumerate(self._number_set)) == 0)
        op = QuadraticProgram()
        op.from_docplex(mdl)
        return op

    def interpret(self, result: OptimizationResult) -> List[List[int]]:
        """Interpret a result as a list of subsets

        Args:
            result: The calculated result of the problem

        Returns:
            A list of subsets whose sum is the half of the total.
        """
        num_subsets = [[], []]
        for i, value in enumerate(result.x):
            if value == 0:
                num_subsets[0].append(self._number_set[i])
            else:
                num_subsets[1].append(self._number_set[i])
        return num_subsets