from dataclasses import dataclass
from typing import List

from ..programs.hole import Hole
from ..programs.s_expression import InitializedSExpression, SExpression
from ..types.type import Type

from .production import Production


@dataclass
class DSL:
    productions: List[Production]
    # variable_system: VariableSystem TODO(KG) add this

    def expansions_for_type(self, type: Type) -> List[SExpression]:
        """
        Possible expansions for the given type.

        An expansion is an SExpression with holes in it. The holes can be filled in with
        other SExpressions to produce a complete SExpression.
        """
        return [
            SExpression(production.symbol(), tuple(Hole.of(t) for t in types))
            for production in self.productions
            for types in production.type_signature().unify_return(type)
        ]

    def get_production(self, symbol: str) -> Production:
        """
        Return the production with the given symbol.
        """
        for production in self.productions:
            if production.symbol() == symbol:
                return production
        raise ValueError(f"Production with symbol {symbol} not found")

    def initialize(self, program: SExpression) -> InitializedSExpression:
        """
        Initializes all the productions in the given program.

        Returns a new program with the same structure, but with all the productions
        initialized.
        """
        prod = self.get_production(program.symbol)
        return InitializedSExpression(
            program.symbol,
            tuple(self.initialize(child) for child in program.children),
            prod.initialize(),
        )

    def compute_on_pytorch(self, program: InitializedSExpression):
        prod = self.get_production(program.symbol)
        return prod.compute_on_pytorch(
            program.state,
            *[self.compute_on_pytorch(child) for child in program.children],
        )
