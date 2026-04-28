"""
BASIC Expression Evaluator for uCode1

This module provides advanced expression evaluation capabilities
for the BBC BASIC interpreter, including:
- Expression parsing and evaluation
- Operator precedence handling
- Function call resolution
- Type coercion between numeric and string types

This is a separate module to keep the interpreter clean and
allow for potential swapping of evaluation engines.
"""

from typing import Any, Optional, Dict, List, Tuple
import re
import math

try:
    from .interpreter import BBCBasicInterpreter, BBCBasicState, BBCBasicError
except ImportError:
    BBCBasicInterpreter = None
    BBCBasicState = None
    BBCBasicError = Exception


class BBCEvaluator:
    """
    Expression evaluator for BBC BASIC.
    
    This class handles the parsing and evaluation of BBC BASIC expressions
    with proper operator precedence and type handling.
    """
    
    def __init__(self, interpreter: Optional['BBCBasicInterpreter'] = None):
        """
        Initialize evaluator.
        
        Args:
            interpreter: Reference to the interpreter for state access
        """
        self.interpreter = interpreter
        self.state = interpreter.state if interpreter else None
        
        # Operator precedence (higher number = higher precedence)
        self._precedence = {
            '^': 5,
            'MOD': 4,
            '*': 4,
            '/': 4,
            '+': 3,
            '-': 3,
            '=': 2,
            '<>': 2,
            '<': 2,
            '>': 2,
            '<=': 2,
            '>=': 2,
            'AND': 1,
            'OR': 1,
            'NOT': 6,  # Unary
        }
        
        # Left associative operators
        self._left_associative = {'+', '-', '*', '/', 'MOD', '=', '<>', '<', '>', '<=', '>=', 'AND', 'OR'}
        
        # Right associative operators
        self._right_associative = {'^', 'NOT'}
    
    def evaluate(self, expression: str) -> Any:
        """
        Evaluate a BBC BASIC expression.
        
        Args:
            expression: The expression to evaluate
            
        Returns:
            The result of the evaluation
        """
        # Remove whitespace for parsing
        # But keep it within strings
        cleaned = self._clean_expression(expression)
        
        # Parse into tokens
        tokens = self._tokenize_expression(cleaned)
        
        # Convert to RPN (Reverse Polish Notation)
        rpn = self._infix_to_rpn(tokens)
        
        # Evaluate RPN
        return self._evaluate_rpn(rpn)
    
    def _clean_expression(self, expression: str) -> str:
        """Clean expression for parsing"""
        # Add spaces around operators
        for op in ['+', '-', '*', '/', '^', '=', '<>', '<', '>', '<=', '>=', 'AND', 'OR', 'NOT', 'MOD']:
            if op in expression:
                # Don't add spaces within strings
                pass
        
        return expression
    
    def _tokenize_expression(self, expression: str) -> List[Tuple[str, str]]:
        """
        Tokenize expression into (type, value) pairs.
        
        Returns list of (token_type, token_value) tuples.
        """
        tokens = []
        pos = 0
        in_string = False
        string_char = None
        
        while pos < len(expression):
            char = expression[pos]
            
            # Handle strings
            if char in ('"', "'"):
                if in_string:
                    if char == string_char:
                        # End of string
                        tokens.append(('string', expression[start_pos:pos+1]))
                        in_string = False
                        string_char = None
                    pos += 1
                    continue
                else:
                    # Start of string
                    in_string = True
                    string_char = char
                    start_pos = pos
                    pos += 1
                    continue
            
            if in_string:
                pos += 1
                continue
            
            # Handle whitespace
            if char.isspace():
                pos += 1
                continue
            
            # Handle numbers
            if char.isdigit() or (char == '.' and pos+1 < len(expression) and expression[pos+1].isdigit()):
                start = pos
                while pos < len(expression) and (expression[pos].isdigit() or expression[pos] == '.'):
                    pos += 1
                tokens.append(('number', expression[start:pos]))
                continue
            
            # Handle variables and functions
            if char.isalpha() or char == '_':
                start = pos
                while pos < len(expression) and (expression[pos].isalnum() or expression[pos] in ('_', '$', '%')):
                    pos += 1
                tokens.append(('identifier', expression[start:pos]))
                continue
            
            # Handle operators
            # Check for multi-character operators first
            two_char_ops = ['<=', '>=', '<>', 'AND', 'OR', 'NOT', 'MOD']
            for op in two_char_ops:
                if expression.startswith(op, pos):
                    tokens.append(('operator', op))
                    pos += len(op)
                    break
            else:
                # Single character operators
                if char in ['+', '-', '*', '/', '^', '=', '<', '>', '(', ')', ',', ':']:
                    tokens.append(('operator' if char in '+-*/^=<>\\' else 'punctuation', char))
                    pos += 1
                    continue
            
            # Unknown
            pos += 1
        
        return tokens
    
    def _infix_to_rpn(self, tokens: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        Convert infix tokens to Reverse Polish Notation (RPN).
        
        Uses the Shunting-yard algorithm.
        """
        output = []
        stack = []
        
        for token_type, token_value in tokens:
            token = token_value
            
            if token_type == 'number':
                output.append((token_type, token))
            elif token_type == 'string':
                output.append((token_type, token))
            elif token_type == 'identifier':
                output.append((token_type, token))
            elif token == '(':
                stack.append((token_type, token))
            elif token == ')':
                # Pop until (
                while stack and stack[-1][1] != '(':
                    output.append(stack.pop())
                if stack and stack[-1][1] == '(':
                    stack.pop()  # Remove (
                else:
                    raise BBCBasicError(18, "Missing bracket", 0)  # Missing bracket error
            elif token in self._precedence:
                # Operator
                while stack:
                    top_token = stack[-1][1]
                    if top_token == '(':
                        break
                    if (self._precedence.get(top_token, 0) > self._precedence.get(token, 0)) or \
                       (self._precedence.get(top_token, 0) == self._precedence.get(token, 0) and
                        token in self._left_associative):
                        output.append(stack.pop())
                    else:
                        break
                stack.append((token_type, token))
        
        # Pop remaining operators
        while stack:
            token = stack.pop()
            if token[1] == '(' or token[1] == ')':
                raise BBCBasicError(18, "Missing bracket", 0)  # Missing bracket error
            output.append(token)
        
        return output
    
    def _evaluate_rpn(self, rpn: List[Tuple[str, str]]) -> Any:
        """Evaluate RPN expression"""
        stack = []
        
        for token_type, token in rpn:
            if token_type in ('number', 'string'):
                # Push value
                if token_type == 'number':
                    # Try int first
                    try:
                        stack.append(int(token))
                    except ValueError:
                        try:
                            stack.append(float(token))
                        except:
                            stack.append(0)
                else:
                    # String literal
                    stack.append(token)
            elif token_type == 'identifier':
                # Variable or function
                if self.interpreter:
                    stack.append(self.interpreter.evaluate(token))
                else:
                    stack.append(0)
            elif token_type in ('operator', 'punctuation'):
                # Apply operator
                if token in ['+', '-', '*', '/', '^', 'MOD', '=', '<>', '<', '>', '<=', '>=', 'AND', 'OR']:
                    if token in ['+', '-'] and len(stack) < 1:
                        # Unary
                        a = stack.pop()
                        if token == '-':
                            stack.append(-a)
                        else:
                            stack.append(a)
                    else:
                        # Binary
                        if len(stack) < 2:
                            raise BBCBasicError(17, "Syntax error", 0)
                        b = stack.pop()
                        a = stack.pop()
                        
                        if token == '+':
                            stack.append(a + b)
                        elif token == '-':
                            stack.append(a - b)
                        elif token == '*':
                            stack.append(a * b)
                        elif token == '/':
                            if b == 0:
                                raise BBCBasicError(13, "Division by zero", 0)
                            stack.append(a / b)
                        elif token == '^':
                            stack.append(a ** b)
                        elif token == 'MOD':
                            stack.append(int(a) % int(b))
                        elif token == '=':
                            stack.append(1 if a == b else 0)
                        elif token == '<>':
                            stack.append(1 if a != b else 0)
                        elif token == '<':
                            stack.append(1 if a < b else 0)
                        elif token == '>':
                            stack.append(1 if a > b else 0)
                        elif token == '<=':
                            stack.append(1 if a <= b else 0)
                        elif token == '>=':
                            stack.append(1 if a >= b else 0)
                        elif token == 'AND':
                            stack.append(1 if (a != 0 and b != 0) else 0)
                        elif token == 'OR':
                            stack.append(1 if (a != 0 or b != 0) else 0)
            elif token == 'NOT':
                a = stack.pop()
                stack.append(1 if a == 0 else 0)
        
        if len(stack) != 1:
            raise BBCBasicError(17, "Syntax error", 0)
        
        return stack[0]
    
    def test(self, expression: str) -> Any:
        """Test the evaluator with an expression"""
        return self.evaluate(expression)


def test_evaluator():
    """Test the evaluator standalone"""
    eval = BBCEvaluator()
    
    # Simple tests
    assert eval.test("1 + 2") == 3
    assert eval.test("2 * 3 + 4") == 10
    assert eval.test("(1 + 2) * 3") == 9
    assert eval.test("2 ^ 3 + 1") == 9
    
    print("Evaluator tests passed!")


if __name__ == '__main__':
    test_evaluator()
