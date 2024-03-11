from abc import abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Tuple

import numpy as np

from neurosym.program_dist.distribution import (
    ProgramDistribution,
    ProgramDistributionFamily,
)
from neurosym.program_dist.enumeration_chunk_size import DEFAULT_CHUNK_SIZE
from neurosym.programs.s_expression import SExpression


@dataclass
class TreeDistribution:
    """
    Distribution over SExpressions as trees.

    Internally, we represent the productions in the language as integers, which we
        call indices.
    """

    limit: int
    # input: tuple of ancestor production indices followed by
    #   the position of the node in its parent's children
    # output: list of (production index, likelihood) pairs
    distribution: Dict[Tuple[int, ...], List[Tuple[int, float]]]
    # production index -> (symbol, arity). at 0 should be the root.
    symbols: List[Tuple[str, int]]

    @cached_property
    def symbol_to_index(self) -> Dict[str, int]:
        return {symbol: i for i, (symbol, _) in enumerate(self.symbols)}

    @cached_property
    def distribution_dict(self) -> Dict[Tuple[int, ...], Dict[int, float]]:
        return {k: dict(v) for k, v in self.distribution.items()}

    @cached_property
    def sampling_dict_arrays(
        self,
    ) -> Dict[Tuple[int, ...], Tuple[np.ndarray, np.ndarray]]:
        return {
            k: (
                np.array([x[0] for x in v]),
                np.exp([x[1] for x in v]),
            )
            for k, v in self.distribution.items()
        }

    def compute_likelihood(
        self,
        program: SExpression,
        start_index: Tuple[int] = (0,),
        start_position: int = 0,
    ) -> float:
        """
        Compute the likelihood of the program.
        """
        key = start_index + (start_position,)
        top_symbol = self.symbol_to_index[program.symbol]
        likelihood = self.distribution_dict[key].get(top_symbol, -float("inf"))
        if likelihood == -float("inf"):
            return -float("inf")
        for i, child in enumerate(program.children):
            likelihood += self.compute_likelihood(
                child, (start_index + (top_symbol,))[-self.limit :], start_position=i
            )
        return likelihood


class TreeProgramDistributionFamily(ProgramDistributionFamily):
    """
    See `tree_dist_enumerator.py` for more information.
    """

    @abstractmethod
    def compute_tree_distribution(
        self, distribution: ProgramDistribution
    ) -> TreeDistribution:
        """
        Returns a tree distribution representing the given program distribution.
        """

    def tree_distribution(self, distribution: ProgramDistribution) -> TreeDistribution:
        """
        Cached version of `compute_tree_distribution`.
        """
        # This is a bit of a hack, but it reduces the need to pass around
        # the tree distribution everywhere, or to compute it multiple times.
        # pylint: disable=protected-access
        if not hasattr(distribution, "_tree_distribution"):
            distribution._tree_distribution = self.compute_tree_distribution(
                distribution
            )
        return distribution._tree_distribution

    def enumerate(
        self,
        dist: ProgramDistribution,
        *,
        min_likelihood: float = float("-inf"),
        chunk_size: float = DEFAULT_CHUNK_SIZE,
    ):
        # pylint: disable=cyclic-import
        from neurosym.program_dist.tree_distribution.tree_dist_enumerator import (
            enumerate_tree_dist,
        )

        tree_dist = self.tree_distribution(dist)

        return enumerate_tree_dist(
            tree_dist, min_likelihood=min_likelihood, chunk_size=chunk_size
        )

    def compute_likelihood(
        self, dist: ProgramDistribution, program: SExpression
    ) -> float:
        """
        Compute the likelihood of a program under a distribution.
        """
        return self.tree_distribution(dist).compute_likelihood(program)

    def sample(
        self,
        dist: ProgramDistribution,
        rng: np.random.RandomState,
        *,
        depth_limit=float("inf"),
    ) -> SExpression:
        # pylint: disable=cyclic-import

        from neurosym.program_dist.tree_distribution.tree_dist_sampler import (
            sample_tree_dist,
        )

        tree_dist = self.tree_distribution(dist)
        element = sample_tree_dist(tree_dist, rng, depth_limit=depth_limit)
        assert element.symbol == "<root>"
        [element] = element.children
        return element
