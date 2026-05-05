"""
BBC BASIC Interpreter for uCode1

This module provides a Python-based BBC BASIC interpreter that is compatible
with the BBC Microcomputer's BASIC dialect. It supports BBC BASIC V as used
in the BBC Micro, Master 128, and other Acorn computers.

Features:
- Full BBC BASIC V syntax support
- VDU command processing
- Variable management (integer, float, string, arrays)
- Error handling with BBC-style error messages
- Line numbering and editing
- PROC/FN support
- Structured programming (IF-THEN-ELSE, REPEAT-UNTIL, etc.)

Integration:
This interpreter is designed to work with the VDU module for display output
and can be connected to ThinUI through the VDU bridge.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from enum import Enum, auto
import re
import math

try:
    from .evaluator import BBCEvaluator
except ImportError:
    BBCEvaluator = None


class BBCBasicError(Exception):
    """Base exception for BBC BASIC errors"""
    
    def __init__(self, error_number: int, message: str, line_number: Optional[int] = None):
        self.error_number = error_number
        self.message = message
        self.line_number = line_number
        super().__init__(f"Error {error_number}: {message}" + 
                        (f" at line {line_number}" if line_number else ""))
    
    @classmethod
    def from_ern(cls, ern: int, line_number: Optional[int] = None):
        """Create error from BBC error number"""
        messages = {
            0: "OK",
            1: "Escape",
            2: "Error",
            3: "Repeat",
            4: "Mistake",
            5: "Number too big",
            6: "Too many dimensions",
            7: "Subscript wrong",
            8: "No room",
            9: "Unknown command",
            10: "Bad programme",
            11: "Wrong number of parameters",
            12: "Type mismatch",
            13: "Division by zero",
            14: "Integer out of range",
            15: "No FOR for this NEXT",
            16: "No REPEAT for this UNTIL",
            17: "Syntax error",
            18: "Missing bracket",
            19: "String too long",
            20: "Bad string",
            21: "Number expected",
            22: "String expected",
            23: "Statement lost",
            24: "Bad variable",
            25: "Variable not found",
            26: "No room for line",
            27: "File not found",
            28: "Bad file number",
            29: "File not open",
            30: "End of file",
            31: "File full",
            32: "Input/Output error",
            33: "No such file",
            34: "File already exists",
            35: "File in use",
            36: "Bad file name",
            37: "Bad file mode",
            38: "Bad file number",
            39: "File handle in use",
            40: "Too many open files",
            255: "Break pressed",
        }
        message = messages.get(ern, f"Unknown error ({ern})")
        return cls(ern, message, line_number)


class BBCErrorCodes(Enum):
    """BBC BASIC Error Codes"""
    OK = 0
    ESCAPE = 1
    ERROR = 2
    REPEAT = 3
    MISTAKE = 4
    NUMBER_TOO_BIG = 5
    TOO_MANY_DIMENSIONS = 6
    SUBSCRIPT_WRONG = 7
    NO_ROOM = 8
    UNKNOWN_COMMAND = 9
    BAD_PROGRAMME = 10
    WRONG_NO_PARAMS = 11
    TYPE_MISMATCH = 12
    DIVISION_BY_ZERO = 13
    INTEGER_OUT_OF_RANGE = 14
    NO_FOR_FOR_NEXT = 15
    NO_REPEAT_FOR_UNTIL = 16
    SYNTAX_ERROR = 17
    MISSING_BRACKET = 18
    STRING_TOO_LONG = 19
    BAD_STRING = 20
    NUMBER_EXPECTED = 21
    STRING_EXPECTED = 22
    STATEMENT_LOST = 23
    BAD_VARIABLE = 24
    VARIABLE_NOT_FOUND = 25
    NO_ROOM_FOR_LINE = 26
    FILE_NOT_FOUND = 27


class TokenType(Enum):
    """BASIC Token Types"""
    END = auto()
    number = auto()
    string = auto()
    variable = auto()
    array_var = auto()
    fn_var = auto()
    command = auto()
    keyword = auto()
    operator = auto()
    lparen = auto()
    rparen = auto()
    comma = auto()
    colon = auto()
    semicolon = auto()
    rem = auto()
    data = auto()
    newline = auto()
    eof = auto()


class Token:
    """BASIC Token"""
    
    def __init__(self, type: TokenType, value: str, line: int, col: int):
        self.type = type
        self.value = value
        self.line = line
        self.col = col
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', line={self.line}, col={self.col})"


@dataclass
class BBCBasicState:
    """Current state of the BBC BASIC interpreter"""
    
    # Memory state
    variables: Dict[str, Any] = field(default_factory=dict)
    arrays: Dict[str, List[Any]] = field(default_factory=dict)
    functions: Dict[str, Any] = field(default_factory=dict)
    
    # Execution state
    program: List[str] = field(default_factory=list)
    line_numbers: List[int] = field(default_factory=list)
    program_counter: int = 0
    current_line: int = 0
    error: Optional[BBCBasicError] = None
    
    # VDU state
    vdu_handler: Optional[Any] = None
    screen_mode: int = 7
    fg_color: int = 7
    bg_color: int = 0
    
    # Stacks for control structures
    for_stack: List[Dict[str, Any]] = field(default_factory=list)
    repeat_stack: List[int] = field(default_factory=list)
    gosub_stack: List[int] = field(default_factory=list)
    while_stack: List[int] = field(default_factory=list)
    case_stack: List[Dict[str, Any]] = field(default_factory=list)
    proc_stack: List[Dict[str, Any]] = field(default_factory=list)
    
    # DATA/READ state
    data_values: List[Any] = field(default_factory=list)
    data_pointer: int = 0
    
    # ON ERROR state
    on_error_line: Optional[int] = None
    on_error_action: Optional[str] = None
    on_error_target: Optional[str] = None
    error_line: Optional[int] = None
    
    # I/O state
    input_buffer: str = ""
    input_prompt: str = "? "
    open_files: Dict[int, Any] = field(default_factory=dict)
    
    # Misc state
    trace: bool = False
    break_requested: bool = False
    random_seeded: bool = False
    
    @property
    def current_line_text(self) -> str:
        """Get current line text"""
        if 0 <= self.program_counter < len(self.program):
            return self.program[self.program_counter]
        return ""


class BBCBasicInterpreter:
    """
    BBC BASIC V Interpreter
    
    This class implements the BBC BASIC interpreter core functionality.
    """
    
    def __init__(self, vdu_handler=None):
        """Initialize interpreter with optional VDU handler"""
        self.state = BBCBasicState()
        self.state.vdu_handler = vdu_handler
        
        # Token patterns
        self._token_specs = [
            ('number', r'\d+\.?\d*'),
            ('string', r'"[^"]*"'),
            ('variable', r'[A-Za-z_][A-Za-z0-9_]*%?\$?'),
            ('array_var', r'[A-Za-z_][A-Za-z0-9_]*\([^)]*\)'),
            ('operator', r'\+|\-|\*|/|\\|MOD|AND|OR|NOT|XOR|<=|>=|<>|<|>'),
            ('lparen', r'\('),
            ('rparen', r'\)'),
            ('comma', r','),
            ('colon', r':'),
            ('semicolon', r';'),
            ('rem', r'REM\s+.*', re.IGNORECASE),
            ('whitespace', r'\s+'),
        ]
        
        # BBC BASIC keywords
        self._keywords = [
            'END', 'PRINT', 'INPUT', 'LET', 'DIM', 'FOR', 'TO', 'NEXT', 'STEP',
            'IF', 'THEN', 'ELSE', 'ENDIF', 'CASE', 'OF', 'OTHERWISE', 'ENDCASE',
            'REPEAT', 'UNTIL', 'WHILE', 'ENDWHILE', 'GOTO', 'GOSUB', 'RETURN',
            'PROC', 'ENDPROC', 'DEF', 'FN', 'LOCAL', 'ON', 'ERROR', 'RESUME',
            'MODE', 'VDU', 'CLS', 'CLG', 'PLOT', 'DRAW', 'COLOUR', 'GCOL',
            'MOVE', 'ORIGIN', 'WINDOW', 'SCROLL', 'SOUND', 'ENVELOPE',
            'BPUT', 'BGET', 'OPENIN', 'OPENOUT', 'OPENUP', 'CLOSE', 'PTR', 'EXT',
            'RUN', 'NEW', 'LIST', 'LOAD', 'SAVE', 'CHAIN', 'QUIT',
            'TRACE', 'UNTIL', 'STOP', 'READ', 'DATA', 'RESTORE', 'ON', 'CALL',
            'ABS', 'ACS', 'ADVAL', 'AND', 'ASC', 'ASN', 'ATN', 'BEAT', 'BGET',
            'COUNTER', 'CHR$', 'COS', 'DEG', 'DIV', 'EOR', 'ERROR', 'ERR', 'EVAL',
            'EXP', 'EXT', 'FALSE', 'FILE', 'GET$', 'GET', 'INKEY$', 'INKEY',
            'INSTR(', 'INT', 'LEFT$', 'LEN', 'LN', 'LOG', 'MID$', 'NOT', 'NUM',
            'OPENIN', 'OPENOUT', 'OPENUP', 'OR', 'PI', 'POINT(', 'POS', 'RAD',
            'RND', 'RIGHT$', 'SGN', 'SIN', 'SQR', 'STRING$', 'TAN', 'TIME', 'TRUE',
            'USR', 'VAL', 'VPOS', 'XOR', 'ADFS', 'BPUT', 'CALL', 'CHAIN', 'COUNT',
            'DELETE', 'EDIT', 'LINE', 'LOAD', 'OLD', 'RENUMBER', 'SAVE', 'VERIFY'
        ]
        
        # Built-in functions
        self._builtins = {
            'ABS': self._fn_abs,
            'ACS': self._fn_acs,
            'ADVAL': self._fn_adval,
            'ASC': self._fn_asc,
            'ASN': self._fn_asn,
            'ATN': self._fn_atn,
            'BGET': self._fn_bget,
            'CHR$': self._fn_chr,
            'COS': self._fn_cos,
            'DEG': self._fn_deg,
            'EXP': self._fn_exp,
            'EXT': self._fn_ext,
            'GET$': self._fn_get_string,
            'GET': self._fn_get,
            'INT': self._fn_int,
            'LEFT$': self._fn_left,
            'LEN': self._fn_len,
            'LN': self._fn_ln,
            'LOG': self._fn_log,
            'MID$': self._fn_mid_string,
            'PI': lambda: math.pi,
            'RAD': self._fn_rad,
            'RND': self._fn_rnd,
            'RIGHT$': self._fn_right,
            'SGN': self._fn_sgn,
            'SIN': self._fn_sin,
            'SQR': self._fn_sqr,
            'STRING$': self._fn_string,
            'TAN': self._fn_tan,
            'TIME': self._fn_time,
            'USR': self._fn_usr,
            'VAL': self._fn_val,
            'VPOS': self._fn_vpos,
        }
        
        # Statement handlers
        self._statement_handlers = {
            'REM': self._stmt_rem,
            'PRINT': self._stmt_print,
            'INPUT': self._stmt_input,
            'LET': self._stmt_let,
            'DIM': self._stmt_dim,
            'FOR': self._stmt_for,
            'NEXT': self._stmt_next,
            'IF': self._stmt_if,
            'ENDIF': self._stmt_endif,
            'ELSE': self._stmt_else,
            'REPEAT': self._stmt_repeat,
            'UNTIL': self._stmt_until,
            'WHILE': self._stmt_while,
            'ENDWHILE': self._stmt_endwhile,
            'GOTO': self._stmt_goto,
            'GOSUB': self._stmt_gosub,
            'RETURN': self._stmt_return,
            'PROC': self._stmt_proc,
            'ENDPROC': self._stmt_endproc,
            'DEF': self._stmt_def,
            'FN': self._stmt_fn,
            'MODE': self._stmt_mode,
            'VDU': self._stmt_vdu,
            'CLS': self._stmt_cls,
            'CLG': self._stmt_clg,
            'PLOT': self._stmt_plot,
            'DRAW': self._stmt_draw,
            'COLOUR': self._stmt_colour,
            'GCOL': self._stmt_gcol,
            'MOVE': self._stmt_move,
            'ORIGIN': self._stmt_origin,
            'RUN': self._stmt_run,
            'NEW': self._stmt_new,
            'LIST': self._stmt_list,
            'LOAD': self._stmt_load,
            'SAVE': self._stmt_save,
            'STOP': self._stmt_stop,
            'END': self._stmt_end,
            'DATA': self._stmt_data,
            'READ': self._stmt_read,
            'RESTORE': self._stmt_restore,
            'ON': self._stmt_on,
            'ERROR': self._stmt_error,
            'RESUME': self._stmt_resume,
            'TRACE': self._stmt_trace,
            'LOCAL': self._stmt_local,
            'CASE': self._stmt_case,
            'OF': self._stmt_of,
            'OTHERWISE': self._stmt_otherwise,
            'ENDCASE': self._stmt_endcase,
            'CHAIN': self._stmt_chain,
            'QUIT': self._stmt_quit,
            'OPENIN': self._stmt_openin,
            'OPENOUT': self._stmt_openout,
            'OPENUP': self._stmt_openup,
            'CLOSE': self._stmt_close,
            'PTR': self._stmt_ptr,
            'EXT': self._stmt_ext,
            'BPUT': self._stmt_bput,
            'BGET': self._stmt_bget,
            'SOUND': self._stmt_sound,
            'ENVELOPE': self._stmt_envelope,
            'SCROLL': self._stmt_scroll,
            'WINDOW': self._stmt_window,
            'CALL': self._stmt_call,
        }
    
    def reset(self):
        """Reset interpreter state"""
        self.state = BBCBasicState()
        self.state.vdu_handler = self.state.vdu_handler  # Preserve VDU handler
    
    def tokenize(self, code: str) -> List[Token]:
        """Tokenize BBC BASIC code"""
        tokens = []
        pos = 0
        line = 1
        col = 1
        
        while pos < len(code):
            # Whitespace
            if code[pos].isspace():
                if code[pos] == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
                pos += 1
                continue
            
            # Check for keywords (case insensitive)
            matched = False
            for keyword in self._keywords:
                if code[pos:pos+len(keyword)].upper() == keyword.upper():
                    # Check for keyword boundary
                    if pos+len(keyword) == len(code) or not code[pos+len(keyword)].isalnum():
                        tokens.append(Token(TokenType.keyword, keyword, line, col))
                        pos += len(keyword)
                        col += len(keyword)
                        matched = True
                        break
            
            if matched:
                continue
            
            # Check for line numbers
            line_num_match = re.match(r'^\d+', code[pos:])
            if line_num_match:
                tokens.append(Token(TokenType.number, line_num_match.group(), line, col))
                pos += len(line_num_match.group())
                col += len(line_num_match.group())
                continue
            
            # Check for strings
            if code[pos] == '"':
                end = pos + 1
                while end < len(code) and code[end] != '"':
                    if code[end] == '\n':
                        line += 1
                        col = 1
                    else:
                        col += 1
                    end += 1
                if end < len(code):
                    tokens.append(Token(TokenType.string, code[pos:end+1], line, col))
                    pos = end + 1
                    col += 1
                    continue
            
            # Check for variables
            var_match = re.match(r'^[A-Za-z_][A-Za-z0-9_]*%', code[pos:])
            if var_match:
                tokens.append(Token(TokenType.variable, var_match.group(), line, col))
                pos += len(var_match.group())
                col += len(var_match.group())
                continue
            
            var_match = re.match(r'^[A-Za-z_][A-Za-z0-9_]*\$', code[pos:])
            if var_match:
                tokens.append(Token(TokenType.variable, var_match.group(), line, col))
                pos += len(var_match.group())
                col += len(var_match.group())
                continue
            
            var_match = re.match(r'^[A-Za-z_][A-Za-z0-9_]*', code[pos:])
            if var_match:
                tokens.append(Token(TokenType.variable, var_match.group(), line, col))
                pos += len(var_match.group())
                col += len(var_match.group())
                continue
            
            # Check for numbers
            num_match = re.match(r'^\d+\.?\d*', code[pos:])
            if num_match:
                tokens.append(Token(TokenType.number, num_match.group(), line, col))
                pos += len(num_match.group())
                col += len(num_match.group())
                continue
            
            # Single character tokens
            if code[pos] == '(':
                tokens.append(Token(TokenType.lparen, '(', line, col))
                pos += 1
                col += 1
            elif code[pos] == ')':
                tokens.append(Token(TokenType.rparen, ')', line, col))
                pos += 1
                col += 1
            elif code[pos] == ',':
                tokens.append(Token(TokenType.comma, ',', line, col))
                pos += 1
                col += 1
            elif code[pos] == ':':
                tokens.append(Token(TokenType.colon, ':', line, col))
                pos += 1
                col += 1
            elif code[pos] == ';':
                tokens.append(Token(TokenType.semicolon, ';', line, col))
                pos += 1
                col += 1
            else:
                # Unknown token
                tokens.append(Token(TokenType.eof, code[pos], line, col))
                pos += 1
                col += 1
        
        return tokens
    
    def parse_line(self, line: str) -> Tuple[int, str]:
        """Parse a BASIC line into line number and statement"""
        line = line.strip()
        if not line:
            return 0, ""
        
        # Extract line number
        match = re.match(r'^(\d+)\s+(.*)', line)
        if match:
            return int(match.group(1)), match.group(2)
        
        return 0, line
    
    def parse_statement(self, statement: str) -> List[str]:
        """Parse a BASIC statement into tokens"""
        # Split by colon for multiple statements
        parts = [p.strip() for p in statement.split(':')]
        return [p for p in parts if p]
    
    def load_program(self, lines: List[str]):
        """Load a program from lines of text"""
        self.state.program = []
        self.state.line_numbers = []
        
        for line in lines:
            line = line.strip()
            if line:
                line_num, statement = self.parse_line(line)
                if line_num > 0:
                    self.state.program.append(statement)
                    self.state.line_numbers.append(line_num)
        
        self.state.program_counter = 0
        self.state.error = None
    
    def get_line_index(self, line_number: int) -> int:
        """Find index of a line number"""
        for i, num in enumerate(self.state.line_numbers):
            if num == line_number:
                return i
        return -1
    
    def find_line(self, line_number: int) -> int:
        """Find the next line >= line_number"""
        for i, num in enumerate(self.state.line_numbers):
            if num >= line_number:
                return i
        return len(self.state.line_numbers)
    
    def set_line(self, line_number: int, statement: str):
        """Set or replace a line in the program"""
        index = self.get_line_index(line_number)
        if index >= 0:
            self.state.program[index] = statement
        else:
            # Insert in sorted order
            insert_at = self.find_line(line_number)
            self.state.line_numbers.insert(insert_at, line_number)
            self.state.program.insert(insert_at, statement)
    
    def delete_line(self, line_number: int):
        """Delete a line from the program"""
        index = self.get_line_index(line_number)
        if index >= 0:
            del self.state.program[index]
            del self.state.line_numbers[index]
    
    def run(self, start_line: int = 0):
        """Run the program from a given line"""
        self.state.running = True
        self.state.break_requested = False
        self.state.error = None
        
        if start_line > 0:
            self.state.program_counter = self.find_line(start_line)
        else:
            self.state.program_counter = 0
        
        while self.state.running and not self.state.break_requested:
            if self.state.program_counter >= len(self.state.program):
                # End of program
                break
            
            line_text = self.state.program[self.state.program_counter]
            line_num = self.state.line_numbers[self.state.program_counter]
            
            # Execute all statements on this line
            statements = self.parse_statement(line_text)
            
            for statement in statements:
                try:
                    if not self._execute_statement(statement, line_num):
                        break  # Statement requested break (e.g., END, STOP)
                except BBCBasicError as e:
                    self.state.error = e
                    if not self.state.trace:
                        raise
                except KeyboardInterrupt:
                    self.state.break_requested = True
                    break
            
            self.state.program_counter += 1
        
        self.state.running = False
        
        if self.state.error:
            raise self.state.error
    
    def _execute_statement(self, statement: str, line_number: int) -> bool:
        """Execute a single BASIC statement, returns False to break"""
        statement = statement.strip()
        if not statement:
            return True
        
        # Handle LET without explicit LET keyword (BBC BASIC allows this)
        # Check if this is an assignment (contains = and not in a string)
        if '=' in statement:
            # Check for various patterns
            # Simple assignment: VAR = expr
            # Array assignment: VAR(idx) = expr
            # Function/procedure: PROC or FN
            
            # Check if this starts with a variable name followed by =
            # But not if it's a keyword like PRINT=something
            upper_statement = statement.upper()
            
            # Split by = for simple check
            eq_pos = statement.find('=')
            potential_var = statement[:eq_pos].strip()
            
            # In BBC BASIC, assignment can start with a variable name
            # and the LET keyword is optional
            if (potential_var and 
                (potential_var[0].isalpha() or potential_var[0] == '_') and
                potential_var.upper() not in self._keywords and
                '(' in potential_var):
                # This looks like an array or function assignment
                pass
            
            # Get the part before =
            left_side = statement[:eq_pos].strip()
            
            # If left side is just a variable name (possibly with type suffix),
            # and not in keywords, treat it as LET
            var_pattern = r'^[A-Za-z_][A-Za-z0-9_]*\$?%?$'
            if re.match(var_pattern, left_side) or ('(' in left_side and ')' in left_side):
                # This is an assignment statement - prepend LET
                return self._execute_statement(f"LET {statement}", line_number)
        
        # Convert to uppercase for keyword matching
        upper_statement = statement.upper()
        
        # Split into command and rest
        parts = re.split(r'\s+', upper_statement.strip(), 1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        
        # Handle line numbers in direct mode
        if command == statement and command.isdigit():
            # This is a line number without a command - treat as GOTO
            return self._execute_statement(f"GOTO {command}", line_number)
        
        # Handle VDU (case-sensitive rises an error check)
        if command == 'VDU':
            return self._stmt_vdu(args, line_number)
        
        # Handle uCode1 PROC_* extension commands (PROC_LENS_*, PROC_SKIN_*, PROC_MCP_*, PROC_SPOOL_*)
        if command.startswith('PROC_'):
            return self._handle_proc_extension(statement, line_number)
        
        # Check for statement handler
        handler_name = f'_stmt_{command.lower()}'
        if hasattr(self, handler_name):
            handler = getattr(self, handler_name)
            return handler(args, line_number)
        
        # Unknown command
        raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value, line_number)
    
    def _handle_proc_extension(self, statement: str, line_number: int) -> bool:
        """
        Handle uCode1 PROC_* extension commands.
        
        Dispatches to the appropriate engine (LENS, SKIN, MCP, Spool)
        based on the command prefix.
        """
        # Parse: PROC_XXX_CommandName(arg1, arg2, ...)
        # or: PROC_XXX_CommandName arg1 arg2
        proc_match = re.match(
            r'^PROC_([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\s*$',
            statement,
            re.IGNORECASE | re.DOTALL
        )
        if proc_match:
            full_name = proc_match.group(1).upper()
            args_str = proc_match.group(2)
        else:
            # Try space-separated args
            parts = statement.split(None, 1)
            if len(parts) > 1:
                full_name = parts[0].upper()
                args_str = parts[1]
            else:
                full_name = statement.upper()
                args_str = ""
        
        # Strip PROC_ prefix for dispatch
        # full_name is like "LENS_FLAGEVENT" or "SKIN_APPLY"
        # Split on first underscore to get engine name
        engine_end = full_name.find('_')
        if engine_end < 0:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value, line_number)
        
        engine_name = full_name[:engine_end]  # "LENS", "SKIN", "MCP", "SPOOL"
        command_name = full_name[engine_end + 1:]  # "FLAGEVENT", "APPLY", etc.
        
        # Parse arguments from the args string
        args_list = []
        if args_str.strip():
            depth = 0
            current = ""
            for ch in args_str:
                if ch == '(':
                    depth += 1
                    current += ch
                elif ch == ')':
                    depth -= 1
                    current += ch
                elif ch == ',' and depth == 0:
                    args_list.append(current.strip())
                    current = ""
                else:
                    current += ch
            if current.strip():
                args_list.append(current.strip())
        
        # Evaluate each argument
        evaluated_args = [self.evaluate(a) for a in args_list]
        
        # Dispatch to the appropriate engine
        if engine_name == 'LENS':
            return self._dispatch_lens(command_name, evaluated_args, line_number)
        elif engine_name == 'SKIN':
            return self._dispatch_skin(command_name, evaluated_args, line_number)
        elif engine_name == 'MCP':
            return self._dispatch_mcp(command_name, evaluated_args, line_number)
        elif engine_name == 'SPOOL':
            return self._dispatch_spool(command_name, evaluated_args, line_number)
        else:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value, line_number)
    
    def _dispatch_lens(self, command: str, args: list, line_number: int) -> bool:
        """Dispatch a LENS command to the LENS engine"""
        engine = getattr(self, '_lens_engine', None)
        if engine is None:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value, line_number)
        
        cmd_upper = command.upper()
        if cmd_upper == 'FLAGEVENT':
            if len(args) < 1:
                raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value, line_number)
            engine.flag_event(str(args[0]))
        elif cmd_upper == 'SNAPSHOT':
            if len(args) < 1:
                raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value, line_number)
            engine.snapshot(str(args[0]))
        else:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value, line_number)
        return True
    
    def _dispatch_skin(self, command: str, args: list, line_number: int) -> bool:
        """Dispatch a SKIN command to the SKIN engine"""
        engine = getattr(self, '_skin_engine', None)
        if engine is None:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value, line_number)
        
        cmd_upper = command.upper()
        if cmd_upper == 'APPLY':
            if len(args) < 1:
                raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value, line_number)
            engine.apply(str(args[0]))
        elif cmd_upper == 'MAPCHAR':
            if len(args) < 2:
                raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value, line_number)
            engine.map_char(int(args[0]), str(args[1]))
        elif cmd_upper == 'SETPALETTE':
            if len(args) < 2:
                raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value, line_number)
            engine.set_palette(int(args[0]), str(args[1]))
        else:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value, line_number)
        return True
    
    def _dispatch_mcp(self, command: str, args: list, line_number: int) -> bool:
        """Dispatch an MCP command to the MCP bridge"""
        engine = getattr(self, '_mcp_bridge', None)
        if engine is None:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value, line_number)
        
        cmd_upper = command.upper()
        if cmd_upper == 'RESPOND':
            if len(args) < 1:
                raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value, line_number)
            engine.respond(str(args[0]))
        else:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value, line_number)
        return True
    
    def _dispatch_spool(self, command: str, args: list, line_number: int) -> bool:
        """Dispatch a Spool command to the Spool bridge"""
        engine = getattr(self, '_spool_bridge', None)
        if engine is None:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value, line_number)
        
        cmd_upper = command.upper()
        if cmd_upper == 'SAVE':
            if len(args) < 1:
                raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value, line_number)
            engine.save(str(args[0]))
        else:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value, line_number)
        return True
    def step(self):
        """Execute one statement and pause"""
        if not self.state.running:
            self.state.running = True
            self.state.program_counter = 0
        
        if self.state.program_counter < len(self.state.program):
            line_text = self.state.program[self.state.program_counter]
            line_num = self.state.line_numbers[self.state.program_counter]
            
            statements = self.parse_statement(line_text)
            if statements:
                self._execute_statement(statements[0], line_num)
            
            self.state.program_counter += 1
    
    def stop(self):
        """Stop program execution"""
        self.state.running = False
        self.state.break_requested = True
    
    # ========== STATEMENT HANDLERS ==========
    
    def _stmt_rem(self, args: str, line_number: int) -> bool:
        """REM - Comment"""
        return True
    
    def _stmt_print(self, args: str, line_number: int) -> bool:
        """PRINT - Output text"""
        # Process print items
        items = []
        current = ""
        in_string = False
        
        for char in args:
            if char == '"':
                in_string = not in_string
                current += char
            elif char == ';' and not in_string:
                items.append(current)
                current = ""
            elif char == ',' and not in_string:
                items.append(current)
                current = ""
                items.append(',')  # Tab
            else:
                current += char
        
        if current:
            items.append(current)
        
        # Print items
        output = ""
        for item in items:
            if item == ',':
                # Tab
                output = self._format_tab(output)
            else:
                item = item.strip()
                if item:
                    # Evaluate expression
                    value = self.evaluate(item)
                    output += str(value) if value is not None else ""
        
        if self.state.vdu_handler:
            self.state.vdu_handler.write_bytes(output.encode())
        else:
            print(output, end='')
        
        return True
    
    def _format_tab(self, text: str) -> str:
        """Format tab stop"""
        # BBC BASIC tabs to next multiple of 16
        pos = len(text) % 16
        if pos == 0:
            pos = 16
        return text + " " * (16 - pos)
    
    def _stmt_input(self, args: str, line_number: int) -> bool:
        """INPUT - Get user input"""
        parts = args.split(',')
        prompt = parts[0].strip()
        
        if prompt:
            if prompt.startswith('"') and prompt.endswith('"'):
                # Use provided prompt
                pass
            else:
                # Evaluate prompt expression
                prompt = str(self.evaluate(prompt))
        
        # Request input
        if self.state.vdu_handler:
            # For now, just print prompt
            self.state.vdu_handler.write_bytes(prompt.encode())
            self.state.input_buffer = ""
            self.state.input_prompt = prompt
        
        return True
    
    def _stmt_let(self, args: str, line_number: int) -> bool:
        """LET - Variable assignment"""
        # Split on =
        if '=' not in args:
            raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value, line_number)
        
        var_part, expr_part = args.split('=', 1)
        var_name = var_part.strip()
        expr_value = self.evaluate(expr_part.strip())
        
        # Handle array assignment
        if '(' in var_name and ')' in var_name:
            # Array assignment
            base_name = var_name[:var_name.index('(')]
            indices = var_name[var_name.index('(')+1:var_name.index(')')]
            indices = [self.evaluate(idx.strip()) for idx in indices.split(',')]
            
            if base_name not in self.state.arrays:
                raise BBCBasicError.from_ern(BBCErrorCodes.VARIABLE_NOT_FOUND.value, line_number)
            
            self.state.arrays[base_name][tuple(indices)] = expr_value
        else:
            # Simple variable assignment
            self.state.variables[var_name] = expr_value
        
        return True
    
    def _stmt_dim(self, args: str, line_number: int) -> bool:
        """DIM - Dimension array"""
        parts = [p.strip() for p in args.split(',')]
        
        for part in parts:
            name_size = part.split('(', 1)
            if len(name_size) != 2 or not name_size[1].endswith(')'):
                raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value, line_number)
            
            name = name_size[0]
            sizes_str = name_size[1][:-1]
            sizes = [int(self.evaluate(s.strip())) for s in sizes_str.split(',')]
            
            # Create array with given dimensions
            self.state.arrays[name] = [None] * (sizes[0] if sizes else 10)
            if len(sizes) > 1:
                # Multi-dimensional (for now, just flatten)
                total_size = 1
                for s in sizes:
                    total_size *= s
                self.state.arrays[name] = [None] * total_size
        
        return True
    
    def _stmt_if(self, args: str, line_number: int) -> bool:
        """IF - Conditional statement"""
        # Find THEN
        then_pos = args.upper().find('THEN')
        if then_pos == -1:
            raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value, line_number)
        
        condition = args[:then_pos].strip()
        rest = args[then_pos+4:].strip()
        
        # Evaluate condition
        result = self.evaluate(condition)
        
        if result:
            # Execute the then part
            if rest.startswith('('):
                # Multi-line IF
                self._execute_statement(rest, line_number)
            else:
                # Single statement
                self._execute_statement(rest, line_number)
        
        return True
    
    def _stmt_for(self, args: str, line_number: int) -> bool:
        """FOR - Start of for loop"""
        parts = [p.strip() for p in args.split('=')]
        if len(parts) != 2:
            raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value, line_number)
        
        left, right = parts
        
        # Parse left side (variable, start, step)
        for_parts = [p.strip() for p in left.split(',')]
        if len(for_parts) < 2 or len(for_parts) > 3:
            raise BBCBasicError.from_ern(BBCErrorCodes.WRONG_NO_PARAMS.value, line_number)
        
        var_name = for_parts[0]
        start = self.evaluate(for_parts[1])
        step = self.evaluate(for_parts[2]) if len(for_parts) == 3 else 1
        end = self.evaluate(right)
        
        # Push loop context
        self.state.for_stack.append({
            'variable': var_name,
            'start': start,
            'end': end,
            'step': step,
            'current': start,
            'line': line_number
        })
        
        # Set initial variable value
        self.state.variables[var_name] = start
        
        return True
    
    def _stmt_next(self, args: str, line_number: int) -> bool:
        """NEXT - End of for loop"""
        if not self.state.for_stack:
            raise BBCBasicError.from_ern(BBCErrorCodes.NO_FOR_FOR_NEXT.value, line_number)
        
        # If specific variable, find matching FOR
        next_var = args.strip().upper()
        
        loop = self.state.for_stack[-1]
        if next_var and next_var != loop['variable'].upper():
            # Find the matching FOR with next_var
            for loop in reversed(self.state.for_stack):
                if loop['variable'].upper() == next_var:
                    break
            else:
                raise BBCBasicError.from_ern(BBCErrorCodes.NO_FOR_FOR_NEXT.value, line_number)
        
        # Increment variable
        loop['current'] += loop['step']
        loop['variable'] = loop['variable']  # Reference
        
        # Update variable
        self.state.variables[loop['variable']] = loop['current']
        
        # Check if loop continues
        if loop['step'] > 0:
            should_continue = loop['current'] <= loop['end']
        else:
            should_continue = loop['current'] >= loop['end']
        
        if should_continue:
            # Jump back to FOR line
            for_line = loop['line']
            self.state.program_counter = self.find_line(for_line)
        else:
            # Pop loop
            self.state.for_stack.pop()
        
        return True
    
    def _stmt_goto(self, args: str, line_number: int) -> bool:
        """GOTO - Jump to line"""
        target = self.evaluate(args.strip())
        if not isinstance(target, int):
            raise BBCBasicError.from_ern(BBCErrorCodes.NUMBER_EXPECTED.value, line_number)
        
        self.state.program_counter = self.find_line(target)
        return True
    
    def _stmt_gosub(self, args: str, line_number: int) -> bool:
        """GOSUB - Subroutine call"""
        target = self.evaluate(args.strip())
        if not isinstance(target, int):
            raise BBCBasicError.from_ern(BBCErrorCodes.NUMBER_EXPECTED.value, line_number)
        
        # Push return address
        self.state.gosub_stack.append(self.state.program_counter + 1)
        self.state.program_counter = self.find_line(target)
        return True
    
    def _stmt_return(self, args: str, line_number: int) -> bool:
        """RETURN - Return from subroutine"""
        if not self.state.gosub_stack:
            raise BBCBasicError.from_ern(BBCErrorCodes.ERROR.value, line_number)
        
        self.state.program_counter = self.state.gosub_stack.pop()
        return True
    
    def _stmt_mode(self, args: str, line_number: int) -> bool:
        """MODE - Set screen mode"""
        mode = self.evaluate(args.strip())
        if not isinstance(mode, int):
            raise BBCBasicError.from_ern(BBCErrorCodes.NUMBER_EXPECTED.value, line_number)
        
        self.state.screen_mode = mode
        if self.state.vdu_handler:
            self.state.vdu_handler.vdu(22, mode)
        
        return True
    
    def _stmt_vdu(self, args: str, line_number: int) -> bool:
        """VDU - Visual Display Unit command"""
        parts = [p.strip() for p in args.split(',')]
        if not parts:
            return True
        
        # First parameter is VDU command
        try:
            cmd = int(parts[0])
        except ValueError:
            raise BBCBasicError.from_ern(BBCErrorCodes.NUMBER_EXPECTED.value, line_number)
        
        # Convert remaining parameters
        vdu_args = []
        for arg in parts[1:]:
            try:
                # Try to evaluate as expression
                val = self.evaluate(arg)
                if isinstance(val, (bool, str)):
                    vdu_args.append(ord(val) if isinstance(val, str) and len(val) == 1 else (1 if val else 0))
                else:
                    vdu_args.append(int(val) if val is not None else 0)
            except:
                vdu_args.append(0)
        
        # Send to VDU handler
        if self.state.vdu_handler:
            if cmd >= 128:
                # Extended commands
                self.state.vdu_handler.vdu(cmd, *vdu_args)
            else:
                # Text characters
                for c in range(32, 127):
                    if cmd == c:
                        self.state.vdu_handler.write(c)
                        break
                else:
                    # Control codes
                    self.state.vdu_handler.vdu(cmd, *vdu_args)
        
        return True
    
    def _stmt_cls(self, args: str, line_number: int) -> bool:
        """CLS - Clear screen"""
        if self.state.vdu_handler:
            self.state.vdu_handler.vdu(127)  # VDU 127 = clear screen
        return True
    
    def _stmt_clg(self, args: str, line_number: int) -> bool:
        """CLG - Clear graphics"""
        if self.state.vdu_handler:
            self.state.vdu_handler.vdu(16)  # VDU 16 = clear graphics
        return True
    
    def _stmt_run(self, args: str, line_number: int) -> bool:
        """RUN - Run program"""
        self.run(0 if not args.strip() else int(self.evaluate(args.strip())))
        return False  # Break
    
    def _stmt_new(self, args: str, line_number: int) -> bool:
        """NEW - Clear program"""
        self.reset()
        if self.state.vdu_handler:
            self.state.vdu_handler.clear()
        print("\nNew")
        return False  # Break
    
    def _stmt_list(self, args: str, line_number: int) -> bool:
        """LIST - List program"""
        start_line = 0
        end_line = 999999
        
        if args.strip():
            parts = args.split('-')
            start_line = int(self.evaluate(parts[0].strip()))
            if len(parts) > 1:
                end_line = int(self.evaluate(parts[1].strip()))
        
        for i, line_num in enumerate(self.state.line_numbers):
            if start_line <= line_num <= end_line:
                if self.state.vdu_handler:
                    self.state.vdu_handler.write_bytes(f"{line_num} {self.state.program[i]}\n".encode())
                else:
                    print(f"{line_num} {self.state.program[i]}")
        
        return True
    
    def _stmt_stop(self, args: str, line_number: int) -> bool:
        """STOP - Stop execution"""
        self.stop()
        return False
    
    def _stmt_end(self, args: str, line_number: int) -> bool:
        """END - End program"""
        self.state.program_counter = len(self.state.program)
        return False
    
    def _stmt_data(self, args: str, line_number: int) -> bool:
        """DATA - Data for READ (collects values during execution)"""
        # Parse DATA values and add to the data_values list
        data_str = args.strip()
        if data_str:
            for item in data_str.split(','):
                item = item.strip()
                if item:
                    if item.startswith('"') and item.endswith('"'):
                        self.state.data_values.append(item[1:-1])
                    else:
                        try:
                            self.state.data_values.append(int(item))
                        except ValueError:
                            try:
                                self.state.data_values.append(float(item))
                            except ValueError:
                                self.state.data_values.append(item)
        return True
    
    def _stmt_read(self, args: str, line_number: int) -> bool:
        """READ - Read next DATA value into variable(s)"""
        var_names = [v.strip() for v in args.split(',')]
        for var_name in var_names:
            if not var_name:
                continue
            if self.state.data_pointer >= len(self.state.data_values):
                raise BBCBasicError.from_ern(BBCErrorCodes.END_OF_FILE.value, line_number)
            
            value = self.state.data_values[self.state.data_pointer]
            self.state.data_pointer += 1
            
            # Handle array element assignment
            if '(' in var_name and ')' in var_name:
                base_name = var_name[:var_name.index('(')]
                indices_str = var_name[var_name.index('(')+1:var_name.index(')')]
                indices = [int(self.evaluate(idx.strip())) for idx in indices_str.split(',')]
                
                if base_name not in self.state.arrays:
                    raise BBCBasicError.from_ern(BBCErrorCodes.VARIABLE_NOT_FOUND.value, line_number)
                
                # Flatten multi-dimensional index
                if len(indices) == 1:
                    self.state.arrays[base_name][indices[0]] = value
                else:
                    # For multi-dimensional, compute flat index
                    flat_idx = 0
                    stride = 1
                    for i in range(len(indices) - 1, -1, -1):
                        flat_idx += indices[i] * stride
                        stride *= 10  # Approximate dimension size
                    self.state.arrays[base_name][flat_idx] = value
            else:
                self.state.variables[var_name] = value
        
        return True

    
    def _stmt_trace(self, args: str, line_number: int) -> bool:
        """TRACE - Enable/disable trace"""
        self.state.trace = args.strip().upper() in ['ON', 'YES', 'TRUE']
        return True
    
    # Default handlers for unimplemented statements
    def _stmt_else(self, args: str, line_number: int) -> bool:
        return True
    
    def _stmt_endif(self, args: str, line_number: int) -> bool:
        return True
    
    def _stmt_repeat(self, args: str, line_number: int) -> bool:
        self.state.repeat_stack.append(self.state.program_counter)
        return True
    
    def _stmt_until(self, args: str, line_number: int) -> bool:
        if not self.state.repeat_stack:
            raise BBCBasicError.from_ern(BBCErrorCodes.ERROR.value, line_number)
        
        condition = self.evaluate(args.strip())
        if not condition:
            self.state.program_counter = self.state.repeat_stack[-1]
        else:
            self.state.repeat_stack.pop()
        return True
    
    # ========== EXPRESSION EVALUATION ==========
    
    def evaluate(self, expression: str) -> Any:
        """Evaluate a BBC BASIC expression"""
        expression = expression.strip()
        if not expression:
            return None
        
        # Check for string literal
        if expression.startswith('"') and expression.endswith('"'):
            return expression[1:-1]
        
        # Check for numeric literal (integer or float)
        try:
            if '.' in expression:
                return float(expression)
            return int(expression)
        except (ValueError, TypeError):
            pass
        
        # Check for function call (with parentheses)
        func_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\((.*)\)$', expression, re.IGNORECASE)
        if func_match:
            func_name = func_match.group(1).upper()
            args_str = func_match.group(2)
            
            # Built-in function
            if func_name in self._builtins:
                args = [self.evaluate(a.strip()) for a in args_str.split(',')]
                return self._builtins[func_name](*args)
            
            # User-defined function
            if func_name in self.state.functions:
                return self.state.functions[func_name](args_str)
            
            # Handle uCode1 FN_* extension functions (FN_LENS_*, FN_MCP_*, FN_SPOOL_*)
            if func_name.startswith('FN_'):
                return self._handle_fn_extension(func_name, args_str)
            
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value)
        
        # Check for FN_* extension function without parentheses (e.g. FN_LENS_GetJSON)
        fn_match = re.match(r'^FN_[A-Za-z_][A-Za-z0-9_]*$', expression, re.IGNORECASE)
        if fn_match:
            func_name = expression.upper()
            return self._handle_fn_extension(func_name, "")
        
        # Check for variable (must come after numeric and function checks)
        if re.match(r'^[A-Za-z_][A-Za-z0-9_]*\$?%?$', expression):
            var_name = expression
            
            # Handle array access
            if '(' in var_name and ')' in var_name:
                base_name = var_name[:var_name.index('(')]
                indices = var_name[var_name.index('(')+1:var_name.index(')')]
                indices = [self.evaluate(idx.strip()) for idx in indices.split(',')]
                
                if base_name in self.state.arrays:
                    return self.state.arrays[base_name][tuple(indices)]
                return 0
            
            # Simple variable
            if var_name in self.state.variables:
                return self.state.variables[var_name]
            
            # Not initialized
            return 0 if not var_name.endswith('$') else ""
        
        # Unknown expression
        raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value)
    
    def _handle_fn_extension(self, func_name: str, args_str: str) -> Any:
        """
        Handle uCode1 FN_* extension function calls.
        
        Dispatches to the appropriate engine (LENS, MCP, Spool)
        based on the function name prefix.
        """
        # Strip FN_ prefix
        # func_name is like "FN_LENS_GETJSON" -> "LENS_GETJSON"
        inner = func_name[3:]  # Remove "FN_"
        
        # Split on first underscore to get engine name
        engine_end = inner.find('_')
        if engine_end < 0:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value)
        
        engine_name = inner[:engine_end]  # "LENS", "MCP", "SPOOL"
        command_name = inner[engine_end + 1:]  # "GETJSON", "POLL", "LOAD"
        
        # Parse arguments
        args_list = []
        if args_str.strip():
            depth = 0
            current = ""
            for ch in args_str:
                if ch == '(':
                    depth += 1
                    current += ch
                elif ch == ')':
                    depth -= 1
                    current += ch
                elif ch == ',' and depth == 0:
                    args_list.append(current.strip())
                    current = ""
                else:
                    current += ch
            if current.strip():
                args_list.append(current.strip())
        
        evaluated_args = [self.evaluate(a) for a in args_list]
        
        # Dispatch to the appropriate engine
        if engine_name == 'LENS':
            return self._fn_dispatch_lens(command_name, evaluated_args)
        elif engine_name == 'MCP':
            return self._fn_dispatch_mcp(command_name, evaluated_args)
        elif engine_name == 'SPOOL':
            return self._fn_dispatch_spool(command_name, evaluated_args)
        else:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value)
    
    def _fn_dispatch_lens(self, command: str, args: list) -> Any:
        """Dispatch a LENS FN_* function call"""
        engine = getattr(self, '_lens_engine', None)
        if engine is None:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value)
        
        cmd_upper = command.upper()
        if cmd_upper == 'GETJSON':
            return engine.get_json()
        else:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value)
    
    def _fn_dispatch_mcp(self, command: str, args: list) -> Any:
        """Dispatch an MCP FN_* function call"""
        engine = getattr(self, '_mcp_bridge', None)
        if engine is None:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value)
        
        cmd_upper = command.upper()
        if cmd_upper == 'POLL':
            return engine.poll()
        else:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value)
    
    def _fn_dispatch_spool(self, command: str, args: list) -> Any:
        """Dispatch a Spool FN_* function call"""
        engine = getattr(self, '_spool_bridge', None)
        if engine is None:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value)
        
        cmd_upper = command.upper()
        if cmd_upper == 'LOAD':
            if len(args) < 1:
                raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value)
            return engine.load(str(args[0]))
        else:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value)
    
    def _evaluate_numeric(self, expression: str) -> float:
        """Evaluate a numeric expression"""
        # Strip whitespace
        expression = expression.strip()
        
        # Handle unwary operators
        expression = self._handle_unary(expression)
        
        # Handle parentheses
        while '(' in expression:
            start = expression.rfind('(')
            end = expression.find(')', start)
            if end == -1:
                raise BBCBasicError.from_ern(BBCErrorCodes.MISSING_BRACKET.value)
            
            inner = expression[start+1:end]
            inner_value = self._evaluate_numeric(inner)
            expression = expression[:start] + str(inner_value) + expression[end+1:]
        
        # Handle multiplication and division
        expression = self._evaluate_mul_div(expression)
        
        # Handle addition and subtraction
        expression = self._evaluate_add_sub(expression)
        
        # Handle AND, OR
        expression = self._evaluate_logical(expression)
        
        try:
            return float(expression)
        except ValueError:
            raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value)
    
    def _handle_unary(self, expression: str) -> str:
        """Handle unary operators"""
        # Replace unary minus
        expression = re.sub(r'(\s|^)(\-|\+)(?=\d)', r'\1u\2', expression)
        return expression
    
    def _evaluate_mul_div(self, expression: str) -> str:
        """Evaluate multiplication and division"""
        tokens = re.split(r'(\*|/|MOD)', expression)
        result = []
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token in ('*', '/', 'MOD'):
                left = float(result[-1])
                right = float(self._evaluate_numeric(tokens[i+1]))
                
                if token == '*':
                    result[-1] = str(left * right)
                elif token == '/':
                    if right == 0:
                        raise BBCBasicError.from_ern(BBCErrorCodes.DIVISION_BY_ZERO.value)
                    result[-1] = str(left / right)
                elif token == 'MOD':
                    result[-1] = str(int(left) % int(right))
                i += 2
            else:
                if token.strip():
                    result.append(token)
                i += 1
        
        return ''.join(result)
    
    def _evaluate_add_sub(self, expression: str) -> str:
        """Evaluate addition and subtraction"""
        tokens = re.split(r'(\+|\-|u\-|u\+)', expression)
        result = []
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token in ('+', '-', 'u-', 'u+'):
                if token == 'u-':
                    # Unary minus
                    operand = self._eval_token_numeric(tokens[i+1].strip())
                    result[-1] = str(-operand)
                    i += 2
                elif token == 'u+':
                    # Unary plus
                    operand = self._eval_token_numeric(tokens[i+1].strip())
                    result[-1] = str(+operand)
                    i += 2
                else:
                    # Evaluate left operand
                    left_val = self._eval_token_numeric(result[-1]) if result else 0
                    right_val = self._eval_token_numeric(tokens[i+1].strip())
                    
                    if token == '+':
                        result[-1] = str(left_val + right_val)
                    else:
                        result[-1] = str(left_val - right_val)
                    i += 2
            else:
                if token.strip():
                    result.append(token.strip())
                i += 1
        
        return ''.join(result)
    
    def _eval_token_numeric(self, token: str) -> float:
        """Evaluate a token as a numeric value (variable or literal)"""
        token = token.strip()
        # Try as variable first
        if re.match(r'^[A-Za-z_][A-Za-z0-9_]*\$?%?$', token):
            val = self.evaluate(token)
            if isinstance(val, (int, float)):
                return float(val)
        # Try as numeric
        try:
            return float(token)
        except ValueError:
            pass
        return 0.0
    
    def _evaluate_logical(self, expression: str) -> str:
        """Evaluate logical operators"""
        # AND
        while ' AND ' in expression or 'AND ' in expression or ' and ' in expression:
            pattern = r'([\d\.]+|true|false|yes|no)\s*AND\s*([\d\.]+|true|false|yes|no)'
            match = re.search(pattern, expression, re.IGNORECASE)
            if not match:
                break
            left = self._bool_value(match.group(1))
            right = self._bool_value(match.group(2))
            result = 'true' if (left and right) else 'false'
            expression = expression[:match.start()] + result + expression[match.end():]
        
        # OR
        while ' OR ' in expression or 'OR ' in expression or ' or ' in expression:
            pattern = r'([\d\.]+|true|false|yes|no)\s*OR\s*([\d\.]+|true|false|yes|no)'
            match = re.search(pattern, expression, re.IGNORECASE)
            if not match:
                break
            left = self._bool_value(match.group(1))
            right = self._bool_value(match.group(2))
            result = 'true' if (left or right) else 'false'
            expression = expression[:match.start()] + result + expression[match.end():]
        
        return expression
    
    def _bool_value(self, value: str) -> bool:
        """Convert value to boolean"""
        value = value.lower().strip()
        if value in ('true', 'yes', '1'):
            return True
        if value in ('false', 'no', '0'):
            return False
        return float(value) != 0
    
    # ========== BUILT-IN FUNCTIONS ==========
    
    def _fn_abs(self, x: float) -> float:
        return abs(x)
    
    def _fn_acs(self, x: float) -> float:
        return math.acos(x)
    
    def _fn_adval(self, x: float) -> float:
        # ADVAL - Read ADC value (not implemented)
        return 0
    
    def _fn_asc(self, s: str) -> int:
        return ord(s[0]) if s else 0
    
    def _fn_asn(self, x: float) -> float:
        return math.asin(x)
    
    def _fn_atn(self, x: float) -> float:
        return math.atan(x)
    
    def _fn_bget(self, x: float) -> int:
        # BGET - Read byte (not implemented)
        return 0
    
    def _fn_chr(self, x: float) -> str:
        return chr(int(x))
    
    def _fn_cos(self, x: float) -> float:
        return math.cos(x)
    
    def _fn_deg(self, x: float) -> float:
        self.state.vdu_handler._setup_mode()
        return math.degrees(x)
    
    def _fn_exp(self, x: float) -> float:
        return math.exp(x)
    
    def _fn_ext(self, x: float) -> int:
        # EXT - Get external value (not implemented)
        return 0
    
    def _fn_get(self, x: float) -> int:
        # GET - Read key (not implemented)
        return 0
    
    def _fn_get_string(self, x: float) -> str:
        # GET$ - Read key as string (not implemented)
        return ""
    
    def _fn_int(self, x: float) -> float:
        return math.floor(x)
    
    def _fn_left(self, s: str, n: float) -> str:
        n = int(n)
        return s[:n] if s else ""
    
    def _fn_len(self, s: str) -> int:
        return len(s) if s else 0
    
    def _fn_ln(self, x: float) -> float:
        return math.log(x)
    
    def _fn_log(self, x: float) -> float:
        return math.log10(x)
    
    def _fn_mid_string(self, s: str, start: float, length: Optional[float] = None) -> str:
        start = int(start) - 1  # BBC BASIC is 1-indexed
        if length is not None:
            length = int(length)
            return s[start:start+length] if s else ""
        return s[start:] if s else ""
    
    def _fn_rad(self, x: float) -> float:
        return math.radians(x)
    
    def _fn_rnd(self, x: float) -> float:
        import random
        if not self.state.random_seeded:
            random.seed()
            self.state.random_seeded = True
        if x == 0:
            return random.random()
        elif x < 0:
            # RND(-n) - seed the random number generator
            random.seed(int(abs(x)))
            self.state.random_seeded = True
            return random.random()
        else:
            # RND(n) - return random integer in range 1..n
            return random.randint(1, int(x))
    
    def _fn_right(self, s: str, n: float) -> str:
        n = int(n)
        return s[-n:] if s and n > 0 else ""
    
    def _fn_sgn(self, x: float) -> int:
        if x > 0:
            return 1
        elif x < 0:
            return -1
        return 0
    
    def _fn_sin(self, x: float) -> float:
        return math.sin(x)
    
    def _fn_sqr(self, x: float) -> float:
        return math.sqrt(x)
    
    def _fn_string(self, n: float, c: str) -> str:
        return c * int(n)
    
    def _fn_tan(self, x: float) -> float:
        return math.tan(x)
    
    def _fn_time(self) -> float:
        import time
        return time.time() * 100  # Centiseconds since midnight
    
    def _fn_usr(self, x: float) -> float:
        # USR - Call machine code (not implemented)
        return x
    
    def _fn_val(self, s: str) -> float:
        try:
            return float(s)
        except ValueError:
            return 0
    
    def _fn_vpos(self) -> float:
        # VPOS - Vertical position (not implemented)
        return 0

    # ========== SPRINT 1: PROPER STATEMENT HANDLERS ==========
    
    def _stmt_while(self, args: str, line_number: int) -> bool:
        """WHILE - While loop start with proper loop stack"""
        condition = self.evaluate(args.strip())
        if condition:
            self.state.while_stack.append(line_number)
        else:
            # Skip to matching ENDWHILE
            depth = 1
            pc = self.state.program_counter + 1
            while pc < len(self.state.program):
                line_text = self.state.program[pc].strip().upper()
                if line_text.startswith('WHILE'):
                    depth += 1
                elif line_text.startswith('ENDWHILE'):
                    depth -= 1
                    if depth == 0:
                        self.state.program_counter = pc
                        break
                pc += 1
        return True
    
    def _stmt_endwhile(self, args: str, line_number: int) -> bool:
        """ENDWHILE - Jump back to matching WHILE"""
        if self.state.while_stack:
            while_line = self.state.while_stack.pop()
            self.state.program_counter = self.find_line(while_line) - 1
        return True
    
    def _stmt_case(self, args: str, line_number: int) -> bool:
        """CASE - Case statement with proper stack"""
        selector = self.evaluate(args.strip())
        self.state.case_stack.append({
            'selector': selector,
            'matched': False,
            'line': line_number
        })
        return True
    
    def _stmt_of(self, args: str, line_number: int) -> bool:
        """OF - Of clause in CASE"""
        if not self.state.case_stack:
            return True
        
        case = self.state.case_stack[-1]
        if case['matched']:
            # Already matched, skip to next OF, OTHERWISE, or ENDCASE
            depth = 1
            pc = self.state.program_counter + 1
            while pc < len(self.state.program):
                line_text = self.state.program[pc].strip().upper()
                if line_text.startswith('OF'):
                    depth += 1
                elif line_text.startswith('OTHERWISE') or line_text.startswith('ENDCASE'):
                    depth -= 1
                    if depth == 0:
                        self.state.program_counter = pc - 1
                        break
                pc += 1
            return True
        
        # Check if this OF value matches the selector
        of_value = self.evaluate(args.strip())
        if of_value == case['selector']:
            case['matched'] = True
        else:
            # Skip to next OF, OTHERWISE, or ENDCASE
            depth = 1
            pc = self.state.program_counter + 1
            while pc < len(self.state.program):
                line_text = self.state.program[pc].strip().upper()
                if line_text.startswith('OF'):
                    depth += 1
                elif line_text.startswith('OTHERWISE') or line_text.startswith('ENDCASE'):
                    depth -= 1
                    if depth == 0:
                        self.state.program_counter = pc - 1
                        break
                pc += 1
        return True
    
    def _stmt_otherwise(self, args: str, line_number: int) -> bool:
        """OTHERWISE - Otherwise clause (default case)"""
        if not self.state.case_stack:
            return True
        
        case = self.state.case_stack[-1]
        if case['matched']:
            # Already matched, skip to ENDCASE
            pc = self.state.program_counter + 1
            while pc < len(self.state.program):
                line_text = self.state.program[pc].strip().upper()
                if line_text.startswith('ENDCASE'):
                    self.state.program_counter = pc - 1
                    break
                pc += 1
        else:
            case['matched'] = True
        return True
    
    def _stmt_endcase(self, args: str, line_number: int) -> bool:
        """ENDCASE - End case, pop case stack"""
        if self.state.case_stack:
            self.state.case_stack.pop()
        return True
    
    def _stmt_chain(self, args: str, line_number: int) -> bool:
        """CHAIN - Chain to another program"""
        filename = args.strip()
        if filename.startswith('"') and filename.endswith('"'):
            filename = filename[1:-1]
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            self.load_program(lines)
            self.run()
        except FileNotFoundError:
            raise BBCBasicError.from_ern(BBCErrorCodes.FILE_NOT_FOUND.value, line_number)
        return False
    
    def _stmt_quit(self, args: str, line_number: int) -> bool:
        """QUIT - Quit interpreter"""
        return False
    
    def _stmt_openin(self, args: str, line_number: int) -> bool:
        """OPENIN - Open file for input"""
        parts = [p.strip() for p in args.split(',')]
        if len(parts) >= 2:
            channel_part = parts[0].replace('#', '').strip()
            filename = parts[1]
            if filename.startswith('"') and filename.endswith('"'):
                filename = filename[1:-1]
            try:
                channel = int(self.evaluate(channel_part))
                self.state.open_files[channel] = open(filename, 'r')
            except (ValueError, FileNotFoundError):
                raise BBCBasicError.from_ern(BBCErrorCodes.FILE_NOT_FOUND.value, line_number)
        return True
    
    def _stmt_openout(self, args: str, line_number: int) -> bool:
        """OPENOUT - Open file for output"""
        parts = [p.strip() for p in args.split(',')]
        if len(parts) >= 2:
            channel_part = parts[0].replace('#', '').strip()
            filename = parts[1]
            if filename.startswith('"') and filename.endswith('"'):
                filename = filename[1:-1]
            try:
                channel = int(self.evaluate(channel_part))
                self.state.open_files[channel] = open(filename, 'w')
            except (ValueError, FileNotFoundError):
                raise BBCBasicError.from_ern(BBCErrorCodes.FILE_NOT_FOUND.value, line_number)
        return True
    
    def _stmt_openup(self, args: str, line_number: int) -> bool:
        """OPENUP - Open file for update"""
        parts = [p.strip() for p in args.split(',')]
        if len(parts) >= 2:
            channel_part = parts[0].replace('#', '').strip()
            filename = parts[1]
            if filename.startswith('"') and filename.endswith('"'):
                filename = filename[1:-1]
            try:
                channel = int(self.evaluate(channel_part))
                self.state.open_files[channel] = open(filename, 'r+')
            except (ValueError, FileNotFoundError):
                raise BBCBasicError.from_ern(BBCErrorCodes.FILE_NOT_FOUND.value, line_number)
        return True
    
    def _stmt_close(self, args: str, line_number: int) -> bool:
        """CLOSE - Close file"""
        channel_part = args.replace('#', '').strip()
        if channel_part:
            try:
                channel = int(self.evaluate(channel_part))
                if channel in self.state.open_files:
                    self.state.open_files[channel].close()
                    del self.state.open_files[channel]
            except (ValueError, KeyError):
                pass
        return True
    
    def _stmt_ptr(self, args: str, line_number: int) -> bool:
        """PTR - Set file pointer position"""
        parts = [p.strip() for p in args.split('#')]
        if len(parts) >= 2:
            try:
                channel = int(self.evaluate(parts[0].strip()))
                position = int(self.evaluate(parts[1].strip()))
                if channel in self.state.open_files:
                    self.state.open_files[channel].seek(position)
            except (ValueError, KeyError):
                pass
        return True
    
    def _stmt_ext(self, args: str, line_number: int) -> bool:
        """EXT - Extension command"""
        return True
    
    def _stmt_bput(self, args: str, line_number: int) -> bool:
        """BPUT - Write byte to file"""
        parts = [p.strip() for p in args.split('#')]
        if len(parts) >= 2:
            try:
                channel = int(self.evaluate(parts[0].strip()))
                byte_val = int(self.evaluate(parts[1].strip()))
                if channel in self.state.open_files:
                    self.state.open_files[channel].write(bytes([byte_val]))
            except (ValueError, KeyError):
                pass
        return True
    
    def _stmt_bget(self, args: str, line_number: int) -> bool:
        """BGET - Read byte from file"""
        channel_part = args.replace('#', '').strip()
        if channel_part:
            try:
                channel = int(self.evaluate(channel_part))
                if channel in self.state.open_files:
                    byte_val = self.state.open_files[channel].read(1)
                    return ord(byte_val) if byte_val else -1
            except (ValueError, KeyError):
                pass
        return True
    
    def _stmt_sound(self, args: str, line_number: int) -> bool:
        """SOUND - Make sound (stub)"""
        return True
    
    def _stmt_envelope(self, args: str, line_number: int) -> bool:
        """ENVELOPE - Define sound envelope (stub)"""
        return True
    
    def _stmt_scroll(self, args: str, line_number: int) -> bool:
        """SCROLL - Scroll screen"""
        if self.state.vdu_handler:
            self.state.vdu_handler.vdu(14)
        return True
    
    def _stmt_window(self, args: str, line_number: int) -> bool:
        """WINDOW - Set graphics window"""
        return True
    
    def _stmt_call(self, args: str, line_number: int) -> bool:
        """CALL - Call OS routine (stub)"""
        return True
    
    def _stmt_proc(self, args: str, line_number: int) -> bool:
        """PROC - Call a user-defined procedure"""
        proc_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\((.*)\)$', args, re.DOTALL)
        if proc_match:
            proc_name = proc_match.group(1).upper()
            proc_args_str = proc_match.group(2)
        else:
            parts = args.split(None, 1)
            proc_name = parts[0].upper() if parts else args.upper()
            proc_args_str = parts[1] if len(parts) > 1 else ""
        
        if proc_name in self.state.functions:
            proc_def = self.state.functions[proc_name]
            actual_args = []
            if proc_args_str.strip():
                depth = 0
                current = ""
                for ch in proc_args_str:
                    if ch == '(':
                        depth += 1
                        current += ch
                    elif ch == ')':
                        depth -= 1
                        current += ch
                    elif ch == ',' and depth == 0:
                        actual_args.append(current.strip())
                        current = ""
                    else:
                        current += ch
                if current.strip():
                    actual_args.append(current.strip())
            
            evaluated_args = [self.evaluate(a) for a in actual_args]
            
            self.state.proc_stack.append({
                'return_pc': self.state.program_counter + 1,
                'local_vars': {}
            })
            
            if 'params' in proc_def:
                for i, param_name in enumerate(proc_def['params']):
                    if i < len(evaluated_args):
                        self.state.variables[param_name] = evaluated_args[i]
            
            self.state.program_counter = self.find_line(proc_def['line'])
        else:
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value, line_number)
        return True
    
    def _stmt_endproc(self, args: str, line_number: int) -> bool:
        """ENDPROC - Return from procedure"""
        if self.state.proc_stack:
            frame = self.state.proc_stack.pop()
            if 'local_vars' in frame:
                for var_name in frame['local_vars']:
                    if var_name in self.state.variables:
                        del self.state.variables[var_name]
            self.state.program_counter = frame['return_pc']
        return True
    
    def _stmt_def(self, args: str, line_number: int) -> bool:
        """DEF - Define procedure or function"""
        args = args.strip()
        
        proc_match = re.match(r'^PROC_?([A-Za-z_][A-Za-z0-9_]*)\((.*)\)', args, re.IGNORECASE)
        if proc_match:
            proc_name = proc_match.group(1).upper()
            params_str = proc_match.group(2)
            params = [p.strip() for p in params_str.split(',')] if params_str.strip() else []
            self.state.functions[proc_name] = {
                'type': 'proc',
                'params': params,
                'line': line_number,
                'end_line': None
            }
            return True
        
        fn_match = re.match(r'^FN_?([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\s*=\s*(.*)', args, re.IGNORECASE)
        if fn_match:
            fn_name = fn_match.group(1).upper()
            params_str = fn_match.group(2)
            expression = fn_match.group(3)
            params = [p.strip() for p in params_str.split(',')] if params_str.strip() else []
            self.state.functions[fn_name] = {
                'type': 'fn',
                'params': params,
                'expression': expression,
                'line': line_number
            }
            return True
        
        raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value, line_number)
    
    def _stmt_fn(self, args: str, line_number: int) -> bool:
        """FN - Call a user-defined function (as statement)"""
        fn_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\((.*)\)$', args, re.DOTALL)
        if fn_match:
            fn_name = fn_match.group(1).upper()
            fn_args_str = fn_match.group(2)
            
            if fn_name in self.state.functions:
                fn_def = self.state.functions[fn_name]
                if fn_def['type'] == 'fn':
                    actual_args = []
                    if fn_args_str.strip():
                        depth = 0
                        current = ""
                        for ch in fn_args_str:
                            if ch == '(':
                                depth += 1
                                current += ch
                            elif ch == ')':
                                depth -= 1
                                current += ch
                            elif ch == ',' and depth == 0:
                                actual_args.append(current.strip())
                                current = ""
                            else:
                                current += ch
                        if current.strip():
                            actual_args.append(current.strip())
                    
                    evaluated_args = [self.evaluate(a) for a in actual_args]
                    
                    saved_vars = {}
                    for i, param_name in enumerate(fn_def['params']):
                        if i < len(evaluated_args):
                            saved_vars[param_name] = self.state.variables.get(param_name)
                            self.state.variables[param_name] = evaluated_args[i]
                    
                    result = self.evaluate(fn_def['expression'])
                    
                    for param_name in fn_def['params']:
                        if param_name in saved_vars:
                            if saved_vars[param_name] is not None:
                                self.state.variables[param_name] = saved_vars[param_name]
                            elif param_name in self.state.variables:
                                del self.state.variables[param_name]
                    
                    return True
            raise BBCBasicError.from_ern(BBCErrorCodes.UNKNOWN_COMMAND.value, line_number)
        return True
    
    def _stmt_on(self, args: str, line_number: int) -> bool:
        """ON - ON ERROR GOTO/GOSUB or multi-way branch"""
        args = args.strip()
        
        error_match = re.match(r'^ERROR\s+(GOTO|GOSUB|PROC)\s+(.+)$', args, re.IGNORECASE)
        if error_match:
            action = error_match.group(1).upper()
            target = error_match.group(2).strip()
            self.state.on_error_line = line_number
            self.state.on_error_action = action
            self.state.on_error_target = target
            return True
        
        branch_match = re.match(r'^(.+?)\s+(GOTO|GOSUB)\s+(.+)$', args, re.IGNORECASE)
        if branch_match:
            expr = self.evaluate(branch_match.group(1).strip())
            action = branch_match.group(2).upper()
            targets_str = branch_match.group(3)
            targets = [t.strip() for t in targets_str.split(',')]
            
            idx = int(expr) - 1
            if 0 <= idx < len(targets):
                target_line = int(self.evaluate(targets[idx]))
                if action == 'GOTO':
                    self.state.program_counter = self.find_line(target_line)
                else:
                    self.state.gosub_stack.append(self.state.program_counter + 1)
                    self.state.program_counter = self.find_line(target_line)
            return True
        
        raise BBCBasicError.from_ern(BBCErrorCodes.SYNTAX_ERROR.value, line_number)
    
    def _stmt_error(self, args: str, line_number: int) -> bool:
        """ERROR - Generate error with message"""
        error_msg = args.strip()
        if error_msg.startswith('"') and error_msg.endswith('"'):
            error_msg = error_msg[1:-1]
        raise BBCBasicError(2, error_msg, line_number)
    
    def _stmt_resume(self, args: str, line_number: int) -> bool:
        """RESUME - Resume after error"""
        if self.state.error_line is not None:
            if args.strip().upper() == 'NEXT':
                self.state.program_counter = self.find_line(self.state.error_line + 1)
            else:
                self.state.program_counter = self.find_line(self.state.error_line)
            self.state.error = None
            self.state.error_line = None
        return True
    
    def _stmt_local(self, args: str, line_number: int) -> bool:
        """LOCAL - Declare local variables"""
        if not self.state.proc_stack:
            return True
        
        frame = self.state.proc_stack[-1]
        var_names = [v.strip() for v in args.split(',')]
        
        for var_name in var_names:
            if var_name in self.state.variables:
                frame['local_vars'][var_name] = self.state.variables[var_name]
            self.state.variables[var_name] = 0 if not var_name.endswith('$') else ""
        
        return True
    
    def _stmt_plot(self, args: str, line_number: int) -> bool:
        """PLOT - Plot point"""
        if self.state.vdu_handler:
            parts = [p.strip() for p in args.split(',')]
            if len(parts) >= 2:
                self.state.vdu_handler.vdu(128, *args)
        return True
    
    def _stmt_draw(self, args: str, line_number: int) -> bool:
        """DRAW - Draw line"""
        if self.state.vdu_handler:
            parts = [p.strip() for p in args.split(',')]
            if len(parts) >= 2:
                self.state.vdu_handler.vdu(129, *parts)
        return True
    
    def _stmt_colour(self, args: str, line_number: int) -> bool:
        """COLOUR - Set colour"""
        if args.strip():
            colour = int(args.strip())
            self.state.fg_color = colour & 15
        return True
    
    def _stmt_gcol(self, args: str, line_number: int) -> bool:
        """GCOL - Set graphics colour"""
        if args.strip():
            colour = int(args.strip())
            self.state.fg_color = colour & 15
        return True
    
    def _stmt_move(self, args: str, line_number: int) -> bool:
        """MOVE - Move graphics cursor"""
        if self.state.vdu_handler:
            parts = [p.strip() for p in args.split(',')]
            if len(parts) >= 2:
                self.state.vdu_handler.vdu(132, *parts)
        return True
    
    def _stmt_origin(self, args: str, line_number: int) -> bool:
        """ORIGIN - Set graphics origin"""
        return True
    
    def _stmt_load(self, args: str, line_number: int) -> bool:
        """LOAD - Load program"""
        filename = args.strip()
        if filename.startswith('"') and filename.endswith('"'):
            filename = filename[1:-1]
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            self.load_program(lines)
        except FileNotFoundError:
            raise BBCBasicError.from_ern(BBCErrorCodes.FILE_NOT_FOUND.value, line_number)
        return False
    
    def _stmt_save(self, args: str, line_number: int) -> bool:
        """SAVE - Save program"""
        filename = args.strip()
        if filename.startswith('"') and filename.endswith('"'):
            filename = filename[1:-1]
        try:
            with open(filename, 'w') as f:
                for i, line_num in enumerate(self.state.line_numbers):
                    f.write(f"{line_num} {self.state.program[i]}\n")
        except IOError:
            raise BBCBasicError.from_ern(BBCErrorCodes.FILE_NOT_FOUND.value, line_number)
        return True
    
    def _stmt_restore(self, args: str, line_number: int) -> bool:
        """RESTORE - Restore DATA pointer"""
        if args.strip():
            target_line = int(self.evaluate(args.strip()))
            # Find the DATA line and reset pointer
            self.state.data_pointer = 0
            self.state.data_values = []
            for i, line_num in enumerate(self.state.line_numbers):
                if line_num >= target_line:
                    stmt = self.state.program[i].strip().upper()
                    if stmt.startswith('DATA'):
                        data_str = stmt[4:].strip()
                        for item in data_str.split(','):
                            item = item.strip()
                            if item:
                                if item.startswith('"') and item.endswith('"'):
                                    self.state.data_values.append(item[1:-1])
                                else:
                                    try:
                                        self.state.data_values.append(int(item))
                                    except ValueError:
                                        try:
                                            self.state.data_values.append(float(item))
                                        except ValueError:
                                            self.state.data_values.append(item)
                    break
        else:
            self.state.data_pointer = 0
        return True
