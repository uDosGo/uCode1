10 REM ═══════════════════════════════════════════════════════════════
20 REM  uCode1 BASIC — Task Manager Integration
30 REM  Create and manage uDos tasks from uCode1 BASIC snippets
40 REM ═══════════════════════════════════════════════════════════════
50 REM
60 REM  This BASIC program provides a simple interface to the
70 REM  uDos task management system. It communicates with the
80 REM  MCP task server via HTTP POST requests.
90 REM
100 REM  Commands:
110 REM    RUN     — Show task menu
120 REM    GOTO 500 — List all tasks
130 REM    GOTO 800 — Create a new task
140 REM    GOTO 1100 — Show Kanban board summary
150 REM
160 REM ═══════════════════════════════════════════════════════════════
170 REM
180 REM  NOTE: This requires the MCP task server to be running on
190 REM  port 30001. Start it with:
200 REM    python3 ~/Code/DevStudio/Usync/binder/task_mcp_server.py
210 REM
220 REM ═══════════════════════════════════════════════════════════════

230 REM ─── Main Menu ───
240 PRINT CHR$(147): REM CLEAR SCREEN
250 PRINT "╔══════════════════════════════════╗"
260 PRINT "║     uDos Task Manager (BASIC)    ║"
270 PRINT "╚══════════════════════════════════╝"
280 PRINT
290 PRINT "1. List tasks"
300 PRINT "2. Create task"
310 PRINT "3. Show Kanban summary"
320 PRINT "4. Exit"
330 PRINT
340 INPUT "Choose (1-4): "; CH$
350 IF CH$ = "1" THEN GOTO 500
360 IF CH$ = "2" THEN GOTO 800
370 IF CH$ = "3" THEN GOTO 1100
380 IF CH$ = "4" THEN END
390 GOTO 240

400 REM ─── HTTP Helper (via curl) ───
410 REM Calls the MCP task server and returns JSON response
420 REM Input: T$ = tool name, A$ = JSON arguments
430 REM Output: R$ = JSON response string
440 SYS 65526: REM CALL CURL WRAPPER
450 RETURN

500 REM ─── List Tasks ───
510 PRINT CHR$(147)
520 PRINT "═══ Task List ═══"
530 PRINT
540 INPUT "Lane (dev/pub/user/all): "; L$
550 IF L$ = "" THEN L$ = "all"
560 IF L$ = "all" THEN L$ = ""
570 PRINT "Fetching tasks..."
580 OPEN 15,8,15: REM OPEN COMMAND CHANNEL
590 CMD$ = "curl -s -X POST http://localhost:30001/mcp"
600 CMD$ = CMD$ + " -H 'Content-Type: application/json'"
610 CMD$ = CMD$ + " -d '{\"method\":\"tools/call\",\"params\":{\"name\":\"task_list\",\"arguments\":{\"lane\":\"" + L$ + "\"}}}'"
620 REM Execute via shell (uCode1 extension)
630 SYS 65526, CMD$
640 REM Parse and display results
650 PRINT "Done. Check terminal for output."
660 PRINT
670 INPUT "Press ENTER for menu"; X$
680 GOTO 240

800 REM ─── Create Task ───
810 PRINT CHR$(147)
820 PRINT "═══ Create Task ═══"
830 PRINT
840 INPUT "Title: "; T$
850 IF T$ = "" THEN PRINT "Title required!": GOTO 840
860 INPUT "Lane (dev/pub/user): "; L$
870 IF L$ = "" THEN L$ = "user"
880 INPUT "Priority (low/med/high/urgent): "; P$
890 IF P$ = "" THEN P$ = "medium"
900 INPUT "Description: "; D$
910 PRINT
920 PRINT "Creating task..."
930 CMD$ = "curl -s -X POST http://localhost:30001/mcp"
940 CMD$ = CMD$ + " -H 'Content-Type: application/json'"
950 CMD$ = CMD$ + " -d '{\"method\":\"tools/call\",\"params\":{\"name\":\"task_create\",\"arguments\":{\"title\":\"" + T$ + "\",\"lane\":\"" + L$ + "\",\"priority\":\"" + P$ + "\",\"description\":\"" + D$ + "\"}}}'"
960 SYS 65526, CMD$
970 PRINT "Task created!"
980 PRINT
990 INPUT "Create another? (y/n): "; Y$
1000 IF Y$ = "y" OR Y$ = "Y" THEN GOTO 810
1010 GOTO 240

1100 REM ─── Kanban Summary ───
1110 PRINT CHR$(147)
1120 PRINT "═══ Kanban Board Summary ═══"
1130 PRINT
1140 INPUT "Lane (dev/pub/user): "; L$
1150 IF L$ = "" THEN L$ = "dev"
1160 PRINT "Fetching board for " + L$ + "..."
1170 CMD$ = "curl -s -X POST http://localhost:30001/mcp"
1180 CMD$ = CMD$ + " -H 'Content-Type: application/json'"
1190 CMD$ = CMD$ + " -d '{\"method\":\"tools/call\",\"params\":{\"name\":\"task_kanban_board\",\"arguments\":{\"lane\":\"" + L$ + "\"}}}'"
1200 SYS 65526, CMD$
1210 PRINT
1220 PRINT "Board data displayed in terminal."
1230 PRINT
1240 INPUT "Press ENTER for menu"; X$
1250 GOTO 240

2000 REM ─── Quick Task from BASIC Snippet ───
2010 REM Usage: GOTO 2000 to create a task from current context
2020 REM Edit the variables below before running
2030 T$ = "Review BASIC integration"
2040 L$ = "dev"
2050 P$ = "medium"
2060 D$ = "Test the uCode1 BASIC task manager integration"
2070 GOTO 920
