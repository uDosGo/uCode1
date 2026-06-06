10 REM Mini Adventure Game
20 MODE 7
30 COLOUR 2
40 PRINT TAB(0,2);"THE HAUNTED CASTLE"
50 PRINT TAB(0,4);"A Mini Adventure"
60 PRINT TAB(0,6);"Press any key to start..."
70 A$ = GET$
80 CLS
90 REM Location descriptions
100 LOC$ = "entrance"
110 INVENTORY$ = ""
120 GOLD = 0
130 HP = 10
140 REPEAT
150   CLS
160   COLOUR 3
170   IF LOC$ = "entrance" THEN PROC_entrance
180   IF LOC$ = "hall" THEN PROC_hall
190   IF LOC$ = "kitchen" THEN PROC_kitchen
200   IF LOC$ = "treasury" THEN PROC_treasury
210   IF LOC$ = "dungeon" THEN PROC_dungeon
220   IF HP <= 0 THEN PRINT "You have died!" : END
230 UNTIL LOC$ = "win"
240 PRINT "Congratulations! You win!"
250 END
260 :
270 DEF PROC_entrance
280   PRINT "You stand at the castle entrance."
290   PRINT "A dark hallway lies ahead."
300   PRINT "A kitchen is to the left."
310   PRINT ""
320   PRINT "Where to? (hall/kitchen)"
330   INPUT A$
340   IF A$ = "hall" THEN LOC$ = "hall"
350   IF A$ = "kitchen" THEN LOC$ = "kitchen"
360 ENDPROC
370 :
380 DEF PROC_hall
390   PRINT "A grand hall with suits of armor."
400   PRINT "Stairs lead up to the treasury."
410   PRINT "A trapdoor opens to the dungeon."
420   PRINT ""
430   IF INSTR(INVENTORY$,"key") = 0 THEN
440     PRINT "You see a rusty key on the floor."
450     PRINT "Take it? (Y/N)"
460     A$ = GET$
470     IF A$ = "Y" OR A$ = "y" THEN
480       INVENTORY$ = INVENTORY$ + "key "
490       PRINT "You take the key."
500     ENDIF
510   ENDIF
520   PRINT "Where to? (entrance/treasury/dungeon)"
530   INPUT A$
540   IF A$ = "entrance" THEN LOC$ = "entrance"
550   IF A$ = "treasury" THEN LOC$ = "treasury"
560   IF A$ = "dungeon" THEN LOC$ = "dungeon"
570 ENDPROC
580 :
590 DEF PROC_kitchen
600   PRINT "A dusty kitchen. A rat scurries away."
610   PRINT "You find 5 gold coins!"
620   GOLD = GOLD + 5
630   PRINT "Gold: ";GOLD
640   PRINT ""
650   PRINT "Return to entrance? (Y/N)"
660   A$ = GET$
670   IF A$ = "Y" OR A$ = "y" THEN LOC$ = "entrance"
680 ENDPROC
690 :
700 DEF PROC_treasury
710   IF INSTR(INVENTORY$,"key") > 0 THEN
720     PRINT "You unlock the treasury door!"
730     PRINT "Inside, you find the treasure!"
740     PRINT "Gold: ";GOLD + 100
750     LOC$ = "win"
760   ELSE
770     PRINT "The door is locked. You need a key."
780     PRINT "Return to hall? (Y/N)"
790     A$ = GET$
800     IF A$ = "Y" OR A$ = "y" THEN LOC$ = "hall"
810   ENDIF
820 ENDPROC
830 :
840 DEF PROC_dungeon
850   PRINT "A dark dungeon. You hear growling."
860   PRINT "A goblin attacks!"
870   HP = HP - 3
880   PRINT "You take 3 damage! HP: ";HP
890   PRINT ""
900   PRINT "Flee to hall? (Y/N)"
910   A$ = GET$
920   IF A$ = "Y" OR A$ = "y" THEN LOC$ = "hall"
930 ENDPROC
