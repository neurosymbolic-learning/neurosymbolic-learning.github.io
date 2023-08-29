from dataclasses import dataclass
from typing import Callable, Dict

from neurosym.types.type_signature import ConcreteTypeSignature

from ..programs.hole import Hole
from ..programs.s_expression import InitializedSExpression, SExpression
from ..types.type import AtomicType, Type, ArrowType
from torch import nn

from .production import ConcreteProduction, Production, ParameterizedProduction
from .dsl import DSL


@dataclass
class NeuralDSL(DSL):
    """
    A neural DSL extends `DSL` to handle neural heuristics (ie: type-appropriate NN productions)
    These neural heuristics can be used to fill holes in partial programs.
    Required to run NEAR.
    """

    partial_programs: Dict[Type, SExpression]
    type_to_symbol: Dict[Type, str]

    @classmethod
    def from_dsl(
        cls, dsl: DSL, type_specific_modules: Dict[Type, Callable[[], nn.Module]]
    ):
        """
        Creates a NeuralDSL from a DSL and a set of type specific modules.

        The type specific modules are used to fill holes in partial programs.

        Args:
            dsl: The DSL to extend.
            type_specific_modules: A dictionary mapping types to functions that
                are used to initialize the modules for that type.

        Returns:
            A NeuralDSL.
        """
        partial_productions = []
        type_to_symbol = {}

        for fn_type, module_template in type_specific_modules.items():
            assert isinstance(
                fn_type, ArrowType
            ), f"Type of partial NN module must be an ArrowType, got {fn_type}"
            identifier = "__neural_dsl_internal_{t}".format(t=fn_type)
            type_to_symbol[fn_type] = identifier
            module_c_prod = ParameterizedProduction(
                identifier,
                ConcreteTypeSignature([], fn_type),
                lambda initialized_module: initialized_module,
                dict(initialized_module=module_template),
            )

            partial_productions.append(module_c_prod)

        productions = dsl.productions + partial_productions

        return cls(productions=productions, type_to_symbol=type_to_symbol)

    def get_partial_program(self, hole: Hole) -> Production:
        """
        Returns a production that can be used to fill the given hole.
        """
        return SExpression(
            self.type_to_symbol[hole.type],
            [],
        )

    def initialize(self, program: SExpression) -> InitializedSExpression:
        """
        Initializes all the productions in the given program.

        Returns a new program with the same structure, but with all the productions
        initialized.
        """
        if isinstance(program, Hole):
            prod = self.get_partial_program(program)
        else:
            prod = self.get_production(program.symbol)
        return super().initialize(self, prod)


def create_modules(types, module_factory):
    return {t: lambda: module_factory(*compute_io_shape(t)) for t in types}


def compute_io_shape(t):
    # TODO(AS) implement
    raise NotImplementedError