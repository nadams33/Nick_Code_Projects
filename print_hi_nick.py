import ast
import math
import operator
from pathlib import Path
from typing import Dict, Union

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


STATIC_DIR = Path(__file__).parent / "static"
MAX_EXPRESSION_LENGTH = 256
MAX_AST_NODES = 64
MAX_INTEGER_BITS = 4096

_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

app = FastAPI(title="Nova Calculator", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class CalculationRequest(BaseModel):
    expression: str = Field(..., min_length=1, max_length=MAX_EXPRESSION_LENGTH)


def _checked_number(value: Union[int, float]) -> Union[int, float]:
    if type(value) not in (int, float):
        raise ValueError("Only numeric expressions are supported.")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("The result is too large.")
    if isinstance(value, int) and value.bit_length() > MAX_INTEGER_BITS:
        raise ValueError("The result is too large.")
    return value


def _evaluate(node: ast.AST) -> Union[int, float]:
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)

    if isinstance(node, ast.Constant):
        return _checked_number(node.value)

    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("Exponents must be between -1000 and 1000.")
        result = _BINARY_OPERATORS[type(node.op)](left, right)
        return _checked_number(result)

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        result = _UNARY_OPERATORS[type(node.op)](_evaluate(node.operand))
        return _checked_number(result)

    raise ValueError("Use numbers and the +, -, *, /, //, %, and ** operators.")


def calculate(expression: str) -> Union[int, float]:
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as error:
        raise ValueError("Enter a valid arithmetic expression.") from error

    if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
        raise ValueError("The expression is too complex.")

    return _evaluate(tree)


@app.get("/", include_in_schema=False)
def calculator() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/calc")
def calc(payload: CalculationRequest) -> Dict[str, Union[str, int, float]]:
    try:
        result = calculate(payload.expression)
    except ZeroDivisionError as error:
        raise HTTPException(status_code=400, detail="Cannot divide by zero.") from error
    except (ValueError, OverflowError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {"expression": payload.expression, "result": result}
