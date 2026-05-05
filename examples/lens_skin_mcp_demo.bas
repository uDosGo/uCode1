REM ============================================================
REM uCode1 LENS/SKIN/MCP/Spool Demo
REM
REM This BBC BASIC program demonstrates all four uCode1
REM extension systems working together:
REM   - LENS: Data extraction (events, snapshots, JSON)
REM   - SKIN: Visual reskinning (themes, char mapping, palette)
REM   - MCP: External command control (poll, respond)
REM   - Spool: Save/load game state
REM
REM Run with: udos snack run lens_skin_mcp_demo
REM ============================================================

REM --- Initialise ---
MODE 7
PRINT "uCode1 LENS/SKIN/MCP/Spool Demo"
PRINT "========================================"
PRINT ""

REM --- Set up game state ---
HP% = 100
GOLD% = 50
ROOM% = 1
PLAYER$ = "Adventurer"
LEVEL% = 1

REM --- LENS: Flag events ---
PRINT "1. LENS: Flagging events..."
PROC_LENS_FlagEvent("game_start")
PROC_LENS_FlagEvent("entered_dungeon")
PRINT "   Events flagged: game_start, entered_dungeon"
PRINT ""

REM --- LENS: Take snapshot ---
PRINT "2. LENS: Taking snapshot..."
PROC_LENS_Snapshot("beginning")
PRINT "   Snapshot 'beginning' saved"
PRINT ""

REM --- SKIN: Apply a skin ---
PRINT "3. SKIN: Applying paper_retro skin..."
PROC_SKIN_Apply("paper_retro")
PRINT "   Skin changed to: paper_retro"
PRINT ""

REM --- SKIN: Map a character ---
PRINT "4. SKIN: Mapping character..."
PROC_SKIN_MapChar(65, "@")  REM Map 'A' to '@'
PRINT "   Char 65 mapped to '@'"
PRINT ""

REM --- SKIN: Set palette ---
PRINT "5. SKIN: Setting palette..."
PROC_SKIN_SetPalette(1, "#FFD700")  REM Gold colour
PRINT "   Palette entry 1 set to gold"
PRINT ""

REM --- Simulate gameplay ---
PRINT "6. Simulating gameplay..."
HP% = HP% - 10  REM Took damage
GOLD% = GOLD% + 25  REM Found gold
ROOM% = 2  REM Moved to next room
PROC_LENS_FlagEvent("room_changed")
PRINT "   HP: 100 -> 90, GOLD: 50 -> 75, ROOM: 1 -> 2"
PRINT ""

REM --- LENS: Get JSON state ---
PRINT "7. LENS: Exporting state as JSON..."
state$ = FN_LENS_GetJSON
PRINT "   JSON length: "; LEN(state$); " chars"
PRINT ""

REM --- MCP: Poll for external commands ---
PRINT "8. MCP: Polling for commands..."
cmd$ = FN_MCP_Poll
IF cmd$ = "" THEN
    PRINT "   No pending commands"
ELSE
    PRINT "   Command received: "; cmd$
    PROC_MCP_Respond("OK: " + cmd$ + " processed")
ENDIF
PRINT ""

REM --- Spool: Save state ---
PRINT "9. Spool: Saving game state..."
PROC_SPOOL_Save("demo_save")
PRINT "   State saved to spool"
PRINT ""

REM --- Change state and restore ---
PRINT "10. Spool: Loading saved state..."
HP% = 0  REM Simulate death
GOLD% = 0
PRINT "    HP: 0, GOLD: 0 (after 'death')"
loaded% = FN_SPOOL_Load("demo_save")
IF loaded% THEN
    PRINT "    State restored from spool!"
    PRINT "    HP: "; HP%; ", GOLD: "; GOLD%
ELSE
    PRINT "    ERROR: Could not load spool"
ENDIF
PRINT ""

REM --- Final state ---
PRINT "========================================"
PRINT "Demo complete!"
PRINT ""
PRINT "Final state:"
PRINT "  HP% = "; HP%
PRINT "  GOLD% = "; GOLD%
PRINT "  ROOM% = "; ROOM%
PRINT "  PLAYER$ = "; PLAYER$
PRINT "  LEVEL% = "; LEVEL%
PRINT ""
PRINT "Events flagged:"
PRINT "  game_start, entered_dungeon, room_changed"
PRINT ""
PRINT "Snapshots taken:"
PRINT "  beginning"
PRINT ""
PRINT "Skin applied: paper_retro"
PRINT "Spool saved: demo_save"
PRINT ""
PRINT "Press any key to exit..."
REM Wait for keypress
A$ = GET$
END
