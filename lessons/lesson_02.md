# Lesson 2: Your First Program

**Level:** 1 — Introduction to Programming
**Age Group:** 8-12
**Duration:** 30 minutes

## Learning Objectives

By the end of this lesson, students will be able to:
- Write a simple BBC BASIC program
- Use PRINT to display text
- Use RUN to execute a program
- Use LIST to view program code

## Explanation

A **program** is a list of instructions for the computer to follow.
In BBC BASIC, each instruction has a **line number** so the computer
knows the order to follow them.

### Your First Program

Type these lines exactly:

```basic
10 PRINT "Hello, World!"
20 PRINT "Welcome to uCode1"
30 PRINT "This is my first program"
```

### Running the Program

Type `RUN` and press Enter. The computer will execute each line
in order, from line 10 to line 30.

### Listing the Program

Type `LIST` to see your program again. Type `LIST 10-20` to see
only lines 10 to 20.

## Interactive Exercise

1. Type `NEW` to clear any existing program
2. Type the program above
3. Type `RUN` to run it
4. Type `LIST` to see the code
5. Add a line 40: `40 PRINT "I am learning BASIC!"`
6. Type `RUN` again

## BBC BASIC Code

```basic
10 REM My First Program
20 MODE 7
30 COLOUR 2
40 PRINT TAB(0,10);"Hello, World!"
50 PRINT TAB(0,12);"Welcome to uCode1"
60 END
```

Try this version too! It uses:
- `REM` — a remark/comment (ignored by the computer)
- `MODE 7` — teletext display mode
- `COLOUR 2` — green text
- `TAB(x,y)` — position the cursor
- `END` — end the program

## Quiz

1. What does `RUN` do?
   a) Shows the program
   b) Executes the program
   c) Clears the program
   **Answer: b) Executes the program**

2. What does `LIST` do?
   a) Shows the program code
   b) Runs the program
   c) Saves the program
   **Answer: a) Shows the program code**

3. What does `REM` mean?
   a) Remove
   b) Remark (a comment)
   c) Remember
   **Answer: b) Remark (a comment)**

## Summary

- Programs are lists of numbered instructions
- `PRINT` displays text on screen
- `RUN` executes your program
- `LIST` shows your program code
- `REM` adds comments that the computer ignores
