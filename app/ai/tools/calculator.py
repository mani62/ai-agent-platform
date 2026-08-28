import ast
import operator
from typing import Any

from app.ai.tools.base import BaseTool


class CalculatorTool(BaseTool):

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Performs basic mathematical calculations."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A mathematical expression such as 25 * 4 + 10",
                }
            },
            "required": ["expression"],
        }

    def execute(
        self,
        **kwargs: Any,
    ) -> str:
        expression = kwargs.get("expression")

        if not expression:
            raise ValueError("Expression is required")

        result = self._evaluate(expression)

        return str(result)

    def _evaluate(
        self,
        expression: str,
    ) -> int | float:

        tree = ast.parse(
            expression,
            mode="eval",
        )

        return self._evaluate_node(tree.body)

    def _evaluate_node(
        self,
        node: ast.AST,
    ) -> int | float:

        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
        }

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError(
                "Only numbers are allowed"
            )

        if isinstance(node, ast.BinOp):
            operation = operators.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError(
                    "Unsupported operation"
                )

            left = self._evaluate_node(
                node.left
            )

            right = self._evaluate_node(
                node.right
            )

            return operation(
                left,
                right,
            )

        if isinstance(node, ast.UnaryOp):
            value = self._evaluate_node(
                node.operand
            )

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return value

        raise ValueError(
            "Invalid mathematical expression"
        )