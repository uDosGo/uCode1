10 REM Number Guessing Game
20 MODE 7
30 COLOUR 2
40 PRINT TAB(0,2);"GUESS THE NUMBER"
50 PRINT TAB(0,4);"I'm thinking of a number"
60 PRINT TAB(0,5);"between 1 and 100."
70 SECRET = RND(100)
80 GUESSES = 0
90 REPEAT
100   INPUT "Your guess: ";G
110   GUESSES = GUESSES + 1
120   IF G < SECRET THEN PRINT "Too low!"
130   IF G > SECRET THEN PRINT "Too high!"
140 UNTIL G = SECRET
150 PRINT "Correct! You got it in ";GUESSES;" guesses."
160 IF GUESSES < 5 THEN PRINT "Excellent!"
170 IF GUESSES < 10 THEN PRINT "Good job!"
180 PRINT "Play again? (Y/N)"
190 A$ = GET$
200 IF A$ = "Y" OR A$ = "y" THEN RUN
210 END
