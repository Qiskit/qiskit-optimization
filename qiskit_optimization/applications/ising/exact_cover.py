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

"""An application class for the exact cover."""
from typing import List

import numpy as np
from docplex.mp.model import Model

from qiskit_optimization.algorithms import OptimizationResult
from qiskit_optimization.problems.quadratic_program import QuadraticProgram
from .base_optimization_application import BaseOptimizationApplication


class ExactCover(BaseOptimizationApplication):
    """Convert an exact cover problem [1] instance
    into a :class:`~qiskit_optimization.problems.QuadraticProgram`

    References:
        [1]: "Exact cover",
        https://en.wikipedia.org/wiki/Exact_cover
    """

    def __init__(self, subsets: List[List[int]]) -> None:
        """
        Args:
            subsets: A list of subsets
        """
        self._subsets = subsets
        self._set = []
        for sub in self._subsets:
            self._set.extend(sub)
        self._set = np.unique(self._set)

    def to_quadratic_program(self) -> QuadraticProgram:
        """Convert an exact cover instance into a
        :class:`~qiskit_optimization.problems.QuadraticProgram`

        Returns:
            The :class:`~qiskit_optimization.problems.QuadraticProgram` created
            from the exact cover instance.
        """
        mdl = Model(name='Exact cover')
        x = {i: mdl.binary_var(name='x_{0}'.format(i)) for i in range(len(self._subsets))}
        mdl.minimize(mdl.sum(x[i] for i in x))
        for element in self._set:
            mdl.add_constraint(mdl.sum(x[i] for i, sub in enumerate(self._subsets)
                                       if element in sub) == 1)
        op = QuadraticProgram()
        op.from_docplex(mdl)
        return op

    def interpret(self, result: OptimizationResult) -> List[List[int]]:
        """Interpret a result as a list of subsets

        Args:
            result: The calculated result of the problem

        Returns:
            A list of subsets whose corresponding variable is 1
        """
        sub = []
        for i, value in enumerate(result.x):
            if value:
                sub.append(self._subsets[i])
        return sub
