# uCode1 BBC BASIC Examples

These example programs demonstrate BBC BASIC programming on uCode1.

## Example Index

| File | Description | Concepts |
|------|-------------|----------|
| `01_hello.bas` | Hello World | PRINT, MODE, COLOUR, TAB, GET$ |
| `02_maths.bas` | Maths Fun | INPUT, arithmetic, SQR, RND |
| `03_guess.bas` | Number Guessing | REPEAT/UNTIL, IF, RND, loops |
| `04_teletext.bas` | Teletext Page | MODE 7, COLOUR codes, TAB layout |
| `05_adventure.bas` | Mini Adventure | PROC, GOSUB, string handling, game logic |

## Running Examples

```bash
# Load and run an example
LOAD "examples/01_hello.bas"
RUN

# Or chain directly
CHAIN "examples/03_guess.bas"
```

## Creating Your Own

1. Type `BASIC` or `MODE 6` to enter BBC BASIC mode
2. Type `NEW` to clear any existing program
3. Type your program lines (e.g., `10 PRINT "Hello"`)
4. Type `RUN` to execute
5. Type `SAVE "myprog"` to save
