import pytest

from app.ai.tools.calculator import CalculatorTool


@pytest.fixture
def calculator():
    return CalculatorTool()


def test_addition(calculator):
    result = calculator.execute(
        expression="2 + 3"
    )

    assert result == "5"


def test_multiplication(calculator):
    result = calculator.execute(
        expression="10 * 5"
    )

    assert result == "50"


def test_operator_precedence(calculator):
    result = calculator.execute(
        expression="2 + 3 * 4"
    )

    assert result == "14"


def test_parentheses(calculator):
    result = calculator.execute(
        expression="(2 + 3) * 4"
    )

    assert result == "20"


def test_negative_number(calculator):
    result = calculator.execute(
        expression="-5 + 2"
    )

    assert result == "-3"


def test_missing_expression(calculator):
    with pytest.raises(
        ValueError,
        match="Expression is required",
    ):
        calculator.execute()


def test_invalid_expression(calculator):
    with pytest.raises(ValueError):
        calculator.execute(
            expression="hello"
        )