---
title: "uCode1 User Guide"
status: draft
last_updated: 2026-06-06T12:00:42+10:00
category: guide
tags: [guide, ucode1]
description: "- [Part A: Core uDos Commands](#part-a-core-udos-commands)"
---
# uCode1 User Guide

## Table of Contents

- [Part A: Core uDos Commands](#part-a-core-udos-commands)
- [Part B: BBC BASIC Command Set Reference](#part-b-bbc-basic-command-set-reference)
- [Part C: m6502 Emulator & Game-Skit Variables](#part-c-m6502-emulator--game-skit-variables)
- [Part D: Teletext & Ceefax Integration](#part-d-teletext--ceefax-integration)
- [Part E: Adventure Game Creator & Story Scripting Engine](#part-e-adventure-game-creator--story-scripting-engine)
- [Part F: Education Program & Curriculum](#part-f-education-program--curriculum)

---

## Part A: Core uDos Commands

uCode1 runs on the uDos operating system. These are the core commands
available in the uCode1 terminal.

### System Commands

| Command | Description |
|---------|-------------|
| `HELP` | Display this help screen |
| `CLS` | Clear the screen |
| `DATE` | Show current date and time |
| `TIME` | Show current time |
| `VER` | Show uCode1 version |
| `STATUS` | Show system status |
| `MEM` | Show memory usage |
| `DIR` | List files in current directory |
| `CAT` | Display file contents |
| `TYPE` | Display file contents (alias for CAT) |
| `SAVE` | Save current program |
| `LOAD` | Load a program |
| `RUN` | Run the current program |
| `STOP` | Stop the current program |
| `NEW` | Clear the current program |
| `LIST` | List the current program lines |
| `DELETE` | Delete a program line |
| `RENUMBER` | Renumber program lines |
| `BYE` | Exit uCode1 |

### Mode Commands

| Command | Description |
|---------|-------------|
| `MODE 0` | Teletext/Ceefax mode (40x24, Teletext50 font) |
| `MODE 1` | Terminal mode (40x24, NES/C64 font) |
| `MODE 2` | Grid mode (80x48, small font) |
| `MODE 3` | Split mode (terminal + teletext) |
| `MODE 4` | Adventure mode (full-screen text) |
| `MODE 5` | Education mode (tutorial overlay) |
| `MODE 6` | BBC BASIC mode (full BASIC editor) |
| `MODE 7` | Teletext mode (hardware-accurate) |

### Teletext Commands

| Command | Description |
|---------|-------------|
| `TELETEXT` | Enter teletext mode |
| `PAGE <n>` | Go to teletext page number |
| `INDEX` | Show teletext index page |
| `NEWS` | Show news pages |
| `WEATHER` | Show weather pages |
| `SPORTS` | Show sports pages |
| `GUIDE` | Show TV guide pages |
| `SUBTITLE <on/off>` | Toggle subtitles |
| `REVEAL` | Reveal hidden answers |
| `HOLD` | Hold current page |
| `MIX` | Mix text and graphics |

### BBC BASIC Commands

| Command | Description |
|---------|-------------|
| `BASIC` | Enter BBC BASIC mode |
| `EDIT` | Open the BASIC editor |
| `AUTO` | Auto-number lines |
| `TRACE` | Enable line tracing |
| `TRACE OFF` | Disable line tracing |
| `RENUMBER` | Renumber BASIC lines |
| `OLD` | Recover deleted program |
| `LOAD "file"` | Load BASIC program |
| `SAVE "file"` | Save BASIC program |
| `CHAIN "file"` | Load and run BASIC program |

### Adventure Game Commands

| Command | Description |
|---------|-------------|
| `ADVENT` | Enter adventure mode |
| `QUIT` | Quit adventure |
| `SAVE GAME` | Save adventure state |
| `LOAD GAME` | Load adventure state |
| `SCORE` | Show adventure score |
| `INVENTORY` | Show inventory |
| `LOOK` | Look around |
| `EXAMINE <object>` | Examine an object |
| `TAKE <object>` | Take an object |
| `DROP <object>` | Drop an object |
| `GO <direction>` | Move in a direction |
| `USE <object>` | Use an object |
| `TALK <character>` | Talk to a character |

### Education Commands

| Command | Description |
|---------|-------------|
| `EDUCATE` | Enter education mode |
| `LESSON <n>` | Load lesson number |
| `TUTORIAL` | Start tutorial |
| `QUIZ` | Start quiz |
| `SCORE` | Show quiz score |
| `HELP` | Show education help |
| `NEXT` | Next lesson |
| `BACK` | Previous lesson |
| `REVIEW` | Review current lesson |

---

## Part B: BBC BASIC Command Set Reference

uCode1 includes a BBC BASIC interpreter compatible with the BBC Micro
(BBC Model B, Acorn Electron) BASIC II/III command set.

### Program Control

| Command | Syntax | Description |
|---------|--------|-------------|
| `RUN` | `RUN` | Execute the current program |
| `STOP` | `STOP` | Halt program execution |
| `END` | `END` | End program execution |
| `CONT` | `CONT` | Continue after STOP/END |
| `GOTO` | `GOTO <line>` | Jump to line number |
| `GOSUB` | `GOSUB <line>` | Call subroutine |
| `RETURN` | `RETURN` | Return from subroutine |
| `FOR` | `FOR var = start TO end [STEP n]` | Start FOR loop |
| `NEXT` | `NEXT [var]` | End FOR loop |
| `REPEAT` | `REPEAT` | Start REPEAT loop |
| `UNTIL` | `UNTIL <condition>` | End REPEAT loop |
| `WHILE` | `WHILE <condition>` | Start WHILE loop |
| `ENDWHILE` | `ENDWHILE` | End WHILE loop |
| `IF` | `IF condition THEN ... [ELSE ...]` | Conditional |
| `CASE` | `CASE var OF WHEN val: ... ENDCASE` | Multi-way branch |
| `ON` | `ON expr GOTO/GOSUB line1,line2,...` | Computed branch |
| `PROC` | `PROCname` | Call named procedure |
| `DEF PROC` | `DEF PROCname` | Define procedure |
| `ENDPROC` | `ENDPROC` | End procedure |
| `FN` | `FNname(args)` | Call function |
| `DEF FN` | `DEF FNname(args)=expr` | Define function |
| `LOCAL` | `LOCAL var1,var2,...` | Declare local variables |

### Input/Output

| Command | Syntax | Description |
|---------|--------|-------------|
| `PRINT` | `PRINT expr1,expr2,...` | Print to screen |
| `INPUT` | `INPUT ["prompt"] var` | Input from keyboard |
| `GET` | `var = GET` | Get single character |
| `GET$` | `var$ = GET$` | Get single character as string |
| `INKEY` | `var = INKEY(timeout)` | Check keyboard buffer |
| `INKEY$` | `var$ = INKEY$(timeout)` | Get key with timeout |
| `PRINT TAB` | `PRINT TAB(x,y)` | Print at position |
| `PRINT SPC` | `PRINT SPC(n)` | Print n spaces |
| `PRINT STRING$` | `PRINT STRING$(n,char)` | Print repeated character |
| `VDU` | `VDU n1,n2,...` | Send to VDU driver |
| `SOUND` | `SOUND channel,pitch,duration` | Play sound |
| `ENVELOPE` | `ENVELOPE n,...` | Define sound envelope |

### Graphics (Teletext Mode 7)

| Command | Syntax | Description |
|---------|--------|-------------|
| `COLOUR` | `COLOUR n` | Set text colour (0-7) |
| `COLOUR 128+n` | `COLOUR 128+n` | Set background colour |
| `COLOUR 129` | `COLOUR 129` | Flash on |
| `COLOUR 130` | `COLOUR 130` | Flash off |
| `COLOUR 131` | `COLOUR 131` | Double height on |
| `COLOUR 132` | `COLOUR 132` | Double height off |
| `COLOUR 133` | `COLOUR 133` | Conceal on |
| `COLOUR 134` | `COLOUR 134` | Conceal off |
| `COLOUR 135` | `COLOUR 135` | Boxed text on |
| `COLOUR 136` | `COLOUR 136` | Boxed text off |
| `CLS` | `CLS` | Clear screen |
| `CLG` | `CLG` | Clear graphics |
| `PLOT` | `PLOT x,y` | Plot point |
| `DRAW` | `DRAW x,y` | Draw line |
| `MOVE` | `MOVE x,y` | Move cursor |
| `CIRCLE` | `CIRCLE x,y,r` | Draw circle |
| `FILL` | `FILL x,y` | Flood fill |
| `TAB` | `TAB(x,y)` | Position cursor |
| `PRINT @%` | `PRINT @%` | Print formatted number |

### String Operations

| Function | Syntax | Description |
|----------|--------|-------------|
| `LEFT$` | `LEFT$(str$,n)` | Left n characters |
| `RIGHT$` | `RIGHT$(str$,n)` | Right n characters |
| `MID$` | `MID$(str$,start[,n])` | Middle characters |
| `LEN` | `LEN(str$)` | String length |
| `STR$` | `STR$(expr)` | Convert to string |
| `VAL` | `VAL(str$)` | Convert to number |
| `ASC` | `ASC(char$)` | ASCII value |
| `CHR$` | `CHR$(n)` | Character from ASCII |
| `INSTR` | `INSTR(str$,search$)` | Find substring |
| `STRING$` | `STRING$(n,char$)` | Repeat string |
| `UPPER$` | `UPPER$(str$)` | Convert to uppercase |
| `LOWER$` | `LOWER$(str$)` | Convert to lowercase |
| `STRIP$` | `STRIP$(str$)` | Remove whitespace |

### Mathematical Functions

| Function | Syntax | Description |
|----------|--------|-------------|
| `ABS` | `ABS(n)` | Absolute value |
| `SGN` | `SGN(n)` | Sign (-1, 0, 1) |
| `INT` | `INT(n)` | Integer part |
| `SQR` | `SQR(n)` | Square root |
| `RND` | `RND[(n)]` | Random number |
| `SIN` | `SIN(angle)` | Sine (radians) |
| `COS` | `COS(angle)` | Cosine (radians) |
| `TAN` | `TAN(angle)` | Tangent (radians) |
| `ASN` | `ASN(n)` | Arc sine |
| `ACS` | `ACS(n)` | Arc cosine |
| `ATN` | `ATN(n)` | Arc tangent |
| `RAD` | `RAD(deg)` | Degrees to radians |
| `DEG` | `DEG(rad)` | Radians to degrees |
| `PI` | `PI` | Value of pi |
| `LOG` | `LOG(n)` | Natural logarithm |
| `LOG10` | `LOG10(n)` | Base-10 logarithm |
| `EXP` | `EXP(n)` | Exponential |
| `MOD` | `a MOD b` | Modulo |
| `DIV` | `a DIV b` | Integer division |
| `MAX` | `MAX(a,b)` | Maximum |
| `MIN` | `MIN(a,b)` | Minimum |
| `CLAMP` | `CLAMP(n,lo,hi)` | Clamp value |

### File Operations

| Command | Syntax | Description |
|---------|--------|-------------|
| `OPENIN` | `ptr = OPENIN("file")` | Open for input |
| `OPENOUT` | `ptr = OPENOUT("file")` | Open for output |
| `OPENUP` | `ptr = OPENUP("file")` | Open for update |
| `CLOSE#` | `CLOSE#ptr` | Close file |
| `INPUT#` | `INPUT#ptr,var1,...` | Read from file |
| `PRINT#` | `PRINT#ptr,expr1,...` | Write to file |
| `EOF#` | `EOF#ptr` | End of file test |
| `EXT#` | `EXT#ptr` | File extent (size) |
| `PTR#` | `PTR#ptr` | File pointer position |
| `BPUT#` | `BPUT#ptr,byte` | Write byte |
| `BGET#` | `var = BGET#ptr` | Read byte |
| `OSCLI` | `OSCLI "command"` | Execute OS command |

### Special uCode1 Extensions

| Command | Syntax | Description |
|---------|--------|-------------|
| `GRID` | `GRID x,y,char$` | Write to grid cell |
| `CELL` | `CELL x,y` | Read grid cell |
| `TELETEXT` | `TELETEXT page$` | Show teletext page |
| `PAGE` | `PAGE n` | Set teletext page |
| `ADVENT` | `ADVENT "story"` | Load adventure story |
| `SPRITE` | `SPRITE n,data$` | Define sprite |
| `SCROLL` | `SCROLL dx,dy` | Scroll display |
| `PALETTE` | `PALETTE n,colour$` | Set palette entry |
| `FONT` | `FONT name$` | Set font |
| `MODE` | `MODE n` | Set display mode |
| `SOUND` | `SOUND ch,pitch,dur` | Play sound |
| `MUSIC` | `MUSIC "notes"` | Play music string |
| `JOYSTICK` | `JOYSTICK` | Read joystick |
| `MOUSE` | `MOUSE` | Read mouse position |
| `TIMER` | `TIMER` | Read system timer |
| `DELAY` | `DELAY ms` | Delay milliseconds |
| `EVENT` | `EVENT n,PROChandler` | Set event handler |
| `ON ERROR` | `ON ERROR GOTO line` | Error handler |
| `ON ESCAPE` | `ON ESCAPE GOTO line` | Escape handler |
| `ON TIME` | `ON TIME PROChandler` | Timer event |
| `ON KEY` | `ON KEY PROChandler` | Key press event |

---

## Part C: m6502 Emulator & Game-Skit Variables

uCode1 includes a Python-based m6502 microprocessor emulator that can
run 6502 assembly programs and game-skit scripts.

### m6502 Emulator

The m6502 emulator is based on the python-6502-emulator by hspaans
(https://github.com/hspaans/python-6502-emulator).

**Features:**
- Full 6502 instruction set (56 instructions)
- 16-bit address bus (64KB address space)
- 8-bit data bus
- All registers: A, X, Y, PC, SP, P (status flags)
- All addressing modes: implied, accumulator, immediate, absolute,
  zero-page, indexed, indirect, relative
- Interrupt handling (IRQ, NMI, RESET)
- Cycle-accurate timing

**Registers:**

| Register | Size | Description |
|----------|------|-------------|
| A | 8-bit | Accumulator |
| X | 8-bit | X index register |
| Y | 8-bit | Y index register |
| PC | 16-bit | Program counter |
| SP | 8-bit | Stack pointer (page 1) |
| P | 8-bit | Status flags |

**Status Flags (P register):**

| Bit | Flag | Description |
|-----|------|-------------|
| 7 | N | Negative |
| 6 | V | Overflow |
| 5 | - | Unused (always 1) |
| 4 | B | Break |
| 3 | D | Decimal mode |
| 2 | I | Interrupt disable |
| 1 | Z | Zero |
| 0 | C | Carry |

**Memory Map:**

| Address Range | Description |
|---------------|-------------|
| $0000-$00FF | Zero page |
| $0100-$01FF | Stack |
| $0200-$5FFF | RAM |
| $6000-$7FFF | I/O space |
| $8000-$FFFF | ROM |

### Game-Skit Variables

Game-skit scripts use a set of predefined variables to control
game state, player attributes, and world properties.

**Player Variables:**

| Variable | Type | Description |
|----------|------|-------------|
| `PLAYER_NAME` | string | Player character name |
| `PLAYER_HP` | integer | Hit points |
| `PLAYER_MAX_HP` | integer | Maximum hit points |
| `PLAYER_MP` | integer | Magic points |
| `PLAYER_MAX_MP` | integer | Maximum magic points |
| `PLAYER_LEVEL` | integer | Experience level |
| `PLAYER_EXP` | integer | Experience points |
| `PLAYER_GOLD` | integer | Gold coins |
| `PLAYER_STR` | integer | Strength |
| `PLAYER_DEX` | integer | Dexterity |
| `PLAYER_INT` | integer | Intelligence |
| `PLAYER_WIS` | integer | Wisdom |
| `PLAYER_CON` | integer | Constitution |
| `PLAYER_CHA` | integer | Charisma |
| `PLAYER_X` | integer | X position on map |
| `PLAYER_Y` | integer | Y position on map |
| `PLAYER_Z` | integer | Z position (floor/dungeon level) |
| `PLAYER_DIR` | string | Facing direction (N/S/E/W) |
| `PLAYER_WEAPON` | string | Equipped weapon |
| `PLAYER_ARMOR` | string | Equipped armor |
| `PLAYER_SHIELD` | string | Equipped shield |
| `PLAYER_RING` | string | Equipped ring |
| `PLAYER_AMULET` | string | Equipped amulet |

**Inventory Variables:**

| Variable | Type | Description |
|----------|------|-------------|
| `INVENTORY` | list | Array of item names |
| `INVENTORY_COUNT` | integer | Number of items |
| `INVENTORY_MAX` | integer | Maximum inventory size |
| `INVENTORY_WEIGHT` | integer | Total inventory weight |
| `INVENTORY_GOLD` | integer | Gold in inventory |
| `EQUIPPED_WEAPON` | string | Currently equipped weapon |
| `EQUIPPED_ARMOR` | string | Currently equipped armor |
| `EQUIPPED_SHIELD` | string | Currently equipped shield |
| `EQUIPPED_RING` | string | Currently equipped ring |
| `EQUIPPED_AMULET` | string | Currently equipped amulet |

**World Variables:**

| Variable | Type | Description |
|----------|------|-------------|
| `WORLD_NAME` | string | World/area name |
| `WORLD_TIME` | integer | Game time (ticks) |
| `WORLD_DAY` | integer | Game day number |
| `WORLD_HOUR` | integer | Game hour (0-23) |
| `WORLD_MINUTE` | integer | Game minute (0-59) |
| `WORLD_WEATHER` | string | Current weather |
| `WORLD_TEMPERATURE` | integer | Temperature |
| `WORLD_VISIBILITY` | integer | Visibility range |
| `WORLD_MUSIC` | string | Background music |
| `WORLD_AMBIENT` | string | Ambient sound |
| `MAP_WIDTH` | integer | Map width in tiles |
| `MAP_HEIGHT` | integer | Map height in tiles |
| `MAP_TILES` | 2D array | Tile data |
| `MAP_OBJECTS` | 2D array | Object data |
| `MAP_MOBS` | list | Mobile entities |

**Combat Variables:**

| Variable | Type | Description |
|----------|------|-------------|
| `COMBAT_ACTIVE` | boolean | Is combat active |
| `COMBAT_TURN` | integer | Current combat turn |
| `COMBAT_TARGET` | string | Current target name |
| `COMBAT_TARGET_HP` | integer | Target hit points |
| `COMBAT_TARGET_MAX_HP` | integer | Target max HP |
| `COMBAT_DAMAGE` | integer | Damage dealt this turn |
| `COMBAT_DEFENSE` | integer | Defense bonus |
| `COMBAT_ATTACK_BONUS` | integer | Attack bonus |
| `COMBAT_CRITICAL` | float | Critical hit chance |
| `COMBAT_DODGE` | float | Dodge chance |

**Quest Variables:**

| Variable | Type | Description |
|----------|------|-------------|
| `QUEST_ACTIVE` | string | Current active quest |
| `QUEST_COMPLETED` | list | Completed quests |
| `QUEST_STEP` | integer | Current quest step |
| `QUEST_OBJECTIVE` | string | Current objective |
| `QUEST_REWARD` | string | Quest reward |
| `QUEST_TIME_LIMIT` | integer | Time limit (ticks) |
| `QUEST_FAILED` | boolean | Has quest failed |

**Dialogue Variables:**

| Variable | Type | Description |
|----------|------|-------------|
| `DIALOGUE_NPC` | string | Current NPC name |
| `DIALOGUE_LINE` | integer | Current dialogue line |
| `DIALOGUE_CHOICES` | list | Available choices |
| `DIALOGUE_CHOSEN` | integer | Chosen option |
| `DIALOGUE_FLAGS` | dict | Dialogue state flags |
| `NPC_RELATIONSHIP` | integer | NPC relationship (0-100) |
| `NPC_KNOWN` | boolean | Has NPC been met |
| `NPC_TALKED` | integer | Times talked to NPC |

**Flag Variables:**

| Variable | Type | Description |
|----------|------|-------------|
| `FLAG_<name>` | boolean | Arbitrary game flag |
| `FLAGS` | dict | All game flags |
| `GLOBAL_FLAGS` | dict | Persistent across saves |
| `CHAPTER` | integer | Story chapter |
| `SCENE` | integer | Current scene |
| `SCORE` | integer | Game score |
| `TURNS` | integer | Total turns taken |
| `DEATHS` | integer | Times died |
| `SAVES` | integer | Times saved |

---

## Part D: Teletext & Ceefax Integration

uCode1 includes a full teletext rendering system based on the BBC
Micro Mode 7 teletext standard, powered by the Ceefax container.

### Teletext Modes

| Mode | Description | Font | Resolution |
|------|-------------|------|------------|
| Mode 0 | Teletext (standard) | Teletext50 | 40x24 |
| Mode 7 | Teletext (hardware-accurate) | Teletext50 | 40x24 |

### Teletext Colour Palette

| Code | Colour | Hex |
|------|--------|-----|
| 0 | Black | #000000 |
| 1 | Red | #ff0000 |
| 2 | Green | #00ff00 |
| 3 | Yellow | #ffff00 |
| 4 | Blue | #0000ff |
| 5 | Magenta | #ff00ff |
| 6 | Cyan | #00ffff |
| 7 | White | #ffffff |

### Teletext Control Codes

| Code | Function |
|------|----------|
| 128-135 | Foreground colours (0-7) |
| 136-143 | Background colours (0-7) |
| 144 | Flash on |
| 145 | Flash off |
| 146 | Steady (flash off) |
| 147 | End of box |
| 148 | Start of box |
| 149 | Normal size |
| 150 | Double height |
| 151 | Double width |
| 152 | Double size |
| 153 | Conceal on |
| 154 | Conceal off |
| 155 | Contiguous graphics |
| 156 | Separated graphics |
| 157 | ESC (escape) |
| 158 | Newline |
| 159 | Hold graphics |

### Ceefax Page Structure

Each Ceefax page is 24 rows x 40 columns:

```
Row 0:   Status line (page number, time, date)
Row 1:   Header (service name)
Row 2:   Sub-header
Row 3-21: Content area (19 rows)
Row 22:  Footer (navigation hints)
Row 23:  Status line (subtitle/caption)
```

### Page Numbering Convention

| Range | Content |
|-------|---------|
| 100 | Index |
| 101-199 | News |
| 200-299 | Weather |
| 300-399 | Sports |
| 400-499 | TV Guide |
| 500-599 | uDos System |
| 600-699 | BBC BASIC Tutorial |
| 700-799 | m6502 Status |
| 800-899 | User pages |

### Ceefax Container

The Ceefax service runs as a Docker container:

```bash
# Build
cd ceefax
docker build -t ceefax:latest .

# Run
docker run -p 8080:8080 \
  -v ~/Code/Vendor/ceetex:/vendor/ceetex \
  ceefax:latest
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Ceefax index (HTML) |
| GET | `/page/{n}` | Get teletext page |
| POST | `/page/{n}` | Set teletext page |
| GET | `/search?q=` | Search pages |
| GET | `/health` | Health check |
| WS | `/ws` | WebSocket updates |

### Teletext in BBC BASIC

```basic
10 REM Teletext Demo
20 MODE 7
30 COLOUR 2: REM Green text
40 PRINT TAB(0,0);"CEEFAX 100"
50 COLOUR 6: REM Cyan
60 PRINT TAB(0,2);"Welcome to Ceefax"
70 COLOUR 3: REM Yellow
80 PRINT TAB(0,4);"Page 100 - Index"
90 COLOUR 1: REM Red
100 PRINT TAB(0,6);"101 News"
110 PRINT TAB(0,7);"200 Weather"
120 PRINT TAB(0,8);"300 Sports"
130 GOTO 130
```

---

## Part E: Adventure Game Creator & Story Scripting Engine

uCode1 includes a full adventure game creation system with a story
scripting engine for text adventures, RPGs, and interactive fiction.

### Story Script Format

Adventure stories are written in a simple scripting language:

```yaml
title: "The Lost Crown"
author: "uDos"
version: "1.0"

start:
  location: entrance
  message: "You stand at the entrance to a dark cave."

locations:
  entrance:
    description: "A cave entrance with vines hanging down."
    exits:
      north: tunnel
      east: forest_path
    objects:
      - torch
      - rope
    mobs:
      - rat

  tunnel:
    description: "A narrow tunnel lit by glowing moss."
    exits:
      south: entrance
      east: chamber
    objects:
      - key
    mobs: []

  chamber:
    description: "A vast chamber with a stone pedestal."
    exits:
      west: tunnel
    objects:
      - crown
    mobs:
      - guardian
    condition:
      require: key
      message: "The door is locked. You need a key."

objects:
  torch:
    name: "Torch"
    description: "A wooden torch, unlit."
    takeable: true
    use:
      action: light
      result: "The torch bursts into flame, illuminating the area."

  rope:
    name: "Rope"
    description: "A sturdy rope, 10 meters long."
    takeable: true
    use:
      action: climb
      result: "You tie the rope securely."

  key:
    name: "Rusty Key"
    description: "An old iron key, covered in rust."
    takeable: true
    use:
      action: unlock
      result: "The key fits perfectly!"

  crown:
    name: "Golden Crown"
    description: "A magnificent golden crown studded with jewels."
    takeable: true
    use:
      action: wear
      result: "You place the crown on your head."
    win_condition: true

mobs:
  rat:
    name: "Giant Rat"
    description: "A rat the size of a dog."
    hp: 5
    attack: 2
    defense: 1
    loot:
      - gold: 3

  guardian:
    name: "Stone Guardian"
    description: "A towering statue come to life."
    hp: 20
    attack: 5
    defense: 3
    loot:
      - gold: 50
      - gem

dialogues:
  merchant:
    - "Welcome, traveller!"
    - "I have wares if you have coin."
    choices:
      - text: "What are you selling?"
        response: "I have potions and scrolls."
        action: open_shop
      - text: "Goodbye."
        response: "Safe travels!"
        action: end_dialogue

events:
  on_enter_tunnel:
    - message: "You hear dripping water ahead."
    - check: has_torch
      if_true: "Your torch reveals ancient carvings on the walls."
      if_false: "It's too dark to see anything."

  on_take_crown:
    - message: "As you take the crown, the ground trembles!"
    - spawn: guardian
    - set_flag: crown_taken

  on_defeat_guardian:
    - message: "The guardian crumbles to dust."
    - remove: guardian
    - set_flag: guardian_defeated
    - give: gem

win_conditions:
  - has: crown
    message: "You have found the Golden Crown! You are the true ruler!"
```

### Scripting Engine Commands

| Command | Description |
|---------|-------------|
| `message: "text"` | Display a message |
| `check: variable` | Check a condition |
| `if_true: "text"` | Execute if true |
| `if_false: "text"` | Execute if false |
| `set_flag: name` | Set a game flag |
| `clear_flag: name` | Clear a game flag |
| `give: item` | Give item to player |
| `take: item` | Remove item from player |
| `spawn: mob` | Spawn a monster |
| `remove: mob` | Remove a monster |
| `heal: amount` | Heal the player |
| `damage: amount` | Damage the player |
| `teleport: location` | Teleport player |
| `play: sound` | Play a sound |
| `music: track` | Play background music |
| `fade: colour` | Fade screen to colour |
| `shake: intensity` | Screen shake effect |
| `wait: seconds` | Wait for duration |
| `choice: options` | Present player choice |
| `random: options` | Random outcome |
| `score: points` | Add to score |
| `save` | Auto-save |
| `end_game` | End the game |

### Adventure Mode Commands

| Command | Description |
|---------|-------------|
| `LOOK` | Describe current location |
| `EXAMINE <object>` | Examine an object |
| `TAKE <object>` | Pick up an object |
| `DROP <object>` | Drop an object |
| `USE <object>` | Use an object |
| `GO <direction>` | Move in a direction |
| `N/S/E/W` | Short direction commands |
| `INVENTORY` | Show inventory |
| `SCORE` | Show current score |
| `SAVE` | Save game |
| `LOAD` | Load game |
| `QUIT` | Quit adventure |
| `HELP` | Show adventure help |
| `TALK <npc>` | Talk to an NPC |
| `ATTACK <mob>` | Attack a monster |
| `CAST <spell>` | Cast a spell |
| `SEARCH` | Search area for hidden items |
| `WAIT` | Wait (pass time) |
| `STATUS` | Show player status |

---

## Part F: Education Program & Curriculum

uCode1 includes an education mode with structured lessons covering
programming concepts, computer science, and retro computing.

### Education Mode

Enter education mode with the `EDUCATE` command or `MODE 5`.

### Lesson Structure

Each lesson includes:
- **Title** and **topic**
- **Learning objectives**
- **Explanation** with examples
- **Interactive exercises**
- **Quiz** to test understanding
- **Summary** of key points

### Curriculum Overview

#### Level 1: Introduction to Programming (Ages 8-12)

| Lesson | Topic | Concepts |
|--------|-------|----------|
| 1.1 | What is a Computer? | Input, output, processing |
| 1.2 | Your First Program | PRINT, RUN, LIST |
| 1.3 | Numbers and Math | Variables, arithmetic |
| 1.4 | Words and Text | Strings, INPUT, PRINT |
| 1.5 | Making Decisions | IF, THEN, ELSE |
| 1.6 | Loops | FOR, NEXT, REPEAT |
| 1.7 | Simple Games | Random numbers, timing |
| 1.8 | Drawing with Text | TAB, PRINT formatting |
| 1.9 | Sounds and Music | SOUND, ENVELOPE |
| 1.10 | Your First Adventure | Simple story game |

#### Level 2: Building Skills (Ages 10-14)

| Lesson | Topic | Concepts |
|--------|-------|----------|
| 2.1 | Procedures | PROC, DEF PROC, ENDPROC |
| 2.2 | Functions | FN, DEF FN |
| 2.3 | Arrays | DIM, array indexing |
| 2.4 | Strings in Depth | LEFT$, RIGHT$, MID$ |
| 2.5 | File Handling | SAVE, LOAD, OPEN |
| 2.6 | Graphics | PLOT, DRAW, CIRCLE |
| 2.7 | Animation | Sprites, movement |
| 2.8 | Collision Detection | Hit boxes, boundaries |
| 2.9 | Data Structures | Records, lists |
| 2.10 | Text Adventures | Location, objects, NPCs |

#### Level 3: Advanced Concepts (Ages 12-16)

| Lesson | Topic | Concepts |
|--------|-------|----------|
| 3.1 | Recursion | Recursive functions |
| 3.2 | Sorting Algorithms | Bubble, selection, quick |
| 3.3 | Search Algorithms | Linear, binary |
| 3.4 | Linked Lists | Dynamic data structures |
| 3.5 | Binary Trees | Tree traversal |
| 3.6 | State Machines | Game states, transitions |
| 3.7 | Event-Driven Programming | ON KEY, ON TIME |
| 3.8 | Interrupts | IRQ, NMI handling |
| 3.9 | Assembly Language | 6502 opcodes, addressing modes |
| 3.10 | Compiler Basics | Tokenisation, parsing |

#### Level 4: Retro Computing (Ages 14-18)

| Lesson | Topic | Concepts |
|--------|-------|----------|
| 4.1 | BBC Micro Architecture | MOS, VDU, memory map |
| 4.2 | Teletext Mode 7 | Control codes, colour palette |
| 4.3 | 6502 Assembly Programming | Opcodes, registers, flags |
| 4.4 | Memory Management | Zero page, stack, heap |
| 4.5 | Interrupt Handling | IRQ, NMI, BRK |
| 4.6 | Sound Programming | SOUND, ENVELOPE, noise |
| 4.7 | Graphics Programming | Mode 7, sprites, animation |
| 4.8 | File Systems | DFS, ADFS, disk access |
| 4.9 | Networking | Econet, serial, MODEM |
| 4.10 | Emulator Construction | CPU, memory, I/O simulation |

### Quiz System

Each lesson includes a quiz with multiple-choice questions:

```basic
10 REM Lesson 1.5 Quiz
20 MODE 7
30 COLOUR 3
40 PRINT TAB(0,2);"Lesson 1.5 Quiz"
50 PRINT TAB(0,4);"What does IF do?"
60 PRINT TAB(0,6);"1. Makes a decision"
70 PRINT TAB(0,7);"2. Prints text"
80 PRINT TAB(0,8);"3. Loops forever"
90 INPUT "Answer (1-3): ";A
100 IF A=1 THEN PRINT "Correct!" ELSE PRINT "Try again"
```

### Progress Tracking

Education mode tracks:
- Completed lessons
- Quiz scores
- Time spent per lesson
- Concepts mastered
- Areas needing review

Use `SCORE` to view progress, `REVIEW` to revisit weak areas.
