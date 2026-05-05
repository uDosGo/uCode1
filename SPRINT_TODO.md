# uCode1 Completion Sprint - Master Todo List

## ✅ Phase 6: Testing & CI (COMPLETE)
- [x] 6.1 Run all existing tests and fix failures
- [x] 6.2 Add interpreter program execution tests
- [x] 6.3 Add integration tests (full pipeline)
- [x] 6.4 Add LENS/SKIN/MCP end-to-end tests
- [x] 6.5 Add snack container integration tests
- [x] 6.6 Enhance GitHub Actions CI workflow
- [x] 6.7 Add Docker Compose test setup
- [x] 6.8 Add pre-commit hook

---

## 🚀 Sprint 1: Core Interpreter Completion (Phase 1)

**Goal**: Make the BBC BASIC interpreter fully functional for running real programs (Eamon, NetHack, custom games).

### 1.1 Fix `evaluate()` delegation to BBCEvaluator
- [x] Wire `evaluate()` to delegate complex expressions to `BBCEvaluator` (currently uses inline `_evaluate_numeric`)
- [x] Ensure `BBCEvaluator` handles all BBC BASIC operators (AND, OR, NOT, MOD, ^)
- [x] Add proper string expression evaluation (concatenation with `+`)

### 1.2 Implement WHILE/ENDWHILE with proper loop stack
- [x] Add `while_stack` to `BBCBasicState`
- [x] `_stmt_while`: evaluate condition, push loop context, skip if false
- [x] `_stmt_endwhile`: jump back to matching WHILE if condition still true
- [x] Handle nested WHILE loops

### 1.3 Implement CASE/OF/OTHERWISE/ENDCASE
- [x] Add `case_stack` to `BBCBasicState`
- [x] `_stmt_case`: evaluate selector expression, push to stack
- [x] `_stmt_of`: check if value matches selector
- [x] `_stmt_otherwise`: default case
- [x] `_stmt_endcase`: pop case stack

### 1.4 Implement ON ERROR / RESUME error handling
- [x] Add `on_error_line` to `BBCBasicState`
- [x] `_stmt_on`: parse ON ERROR GOTO/GOSUB line number
- [x] `_stmt_error`: trigger error with message
- [x] `_stmt_resume`: resume execution after error
- [x] Wire error handling into main execution loop

### 1.5 Implement PROC/FN with proper parameter passing
- [x] Add `proc_stack` to `BBCBasicState` (for nested calls)
- [x] `_stmt_def`: parse DEF PROC/FN definitions with parameters
- [x] `_stmt_proc`: call procedure with parameter passing
- [x] `_stmt_endproc`: return from procedure
- [x] `_stmt_fn`: call user-defined function
- [x] `_stmt_local`: declare local variables
- [x] Handle LOCAL variables with proper scoping

### 1.6 Implement DATA/READ/RESTORE with data pointer
- [x] Add `data_pointer` to `BBCBasicState`
- [x] `_stmt_data`: collect DATA values during program load
- [x] `_stmt_read`: read next DATA value into variable
- [x] `_stmt_restore`: reset data pointer to beginning or specific line
- [x] Handle mixed types (numbers and strings) in DATA

### 1.7 Add PROC_*/FN_* extension dispatch for LENS/SKIN/MCP/Spool
- [x] Add `_handle_proc_extension()` to dispatch PROC_LENS_*, PROC_SKIN_*, PROC_MCP_*, PROC_SPOOL_*
- [x] Add `_handle_fn_extension()` to dispatch FN_LENS_*, FN_MCP_*, FN_SPOOL_*
- [x] Add `_dispatch_lens()` / `_dispatch_skin()` / `_dispatch_mcp()` / `_dispatch_spool()` handlers
- [x] Add `_fn_dispatch_lens()` / `_fn_dispatch_mcp()` / `_fn_dispatch_spool()` function handlers
- [x] Wire PROC_* check into `_execute_statement()` before "Unknown command" error
- [x] Wire FN_* check into `evaluate()` before "Unknown command" error

### 1.8 Add REPL mode with line editing
- [ ] Add REPL loop to `BBCBasicInterpreter`
- [ ] Support line number entry (add to program) vs immediate execution
- [ ] Add line editing (backspace, cursor movement)
- [ ] Add `_stmt_old`: recover program after NEW

### 1.8 Add error recovery and line number reporting
- [x] Ensure all errors report correct line numbers
- [x] Add `_stmt_trace`: execution tracing
- [x] Add `_stmt_quit`: clean exit from interpreter
- [x] Add `_stmt_break`: Ctrl+C handling
- [x] Add `_stmt_escape`: escape key handling

### 1.9 Fix RND with proper seeding
- [x] `_fn_rnd(0)`: return random float 0-1
- [x] `_fn_rnd(n)`: return random integer 1-n
- [x] Add `RND(-n)` for seeding the random generator

---

## 🚀 Sprint 2: LENS/SKIN/MCP/Spool Polish (Phase 2)

**Goal**: Complete the integration layers for real game capture and control.

### 2.1 Add LENS memory region breakpoints for 6502 emulation
- [ ] Add `MemoryRegion` dataclass (address, size, callback)
- [ ] Add `set_breakpoint()` / `clear_breakpoint()` to LENSEngine
- [ ] Add `on_memory_write()` callback mechanism
- [ ] Add `capture_intervals` configuration (frame, room_change, save)
- [ ] Add `_on_change_callbacks` for variable change detection

### 2.2 Add SKIN CeefaxThinUI renderer bridge
- [ ] Add `CeefaxThinUIBridge` class in `skin.py`
- [ ] Implement `render_frame()`: convert teletext grid to CeefaxThinUI format
- [ ] Implement `render_text()`: apply skin styles to text output
- [ ] Add `export_png()`: render current frame to PNG
- [ ] Add `export_html()`: render current frame to HTML

### 2.3 Add MCP gRPC server integration
- [ ] Add `MCPGrpcServer` class in `mcp_bridge.py`
- [ ] Implement gRPC `SendCommand` service handler
- [ ] Implement gRPC `Subscribe` service handler (for Feed events)
- [ ] Wire MCP bridge to gRPC server via `set_external_source()`
- [ ] Add `start_grpc_server()` / `stop_grpc_server()` methods

### 2.4 Add Spool compression (MessagePack/Zstd)
- [ ] Add `SpoolCodec` base class
- [ ] Add `JsonCodec` (existing, refactor)
- [ ] Add `MessagePackCodec` using `msgpack` library
- [ ] Add `ZstdMessagePackCodec` using `zstd` library
- [ ] Add `compress()` / `decompress()` methods to SpoolBridge
- [ ] Add `--format` flag to spool save/load

### 2.5 Add Spool cross-snack import/export
- [ ] Add `CrossSnackData` dataclass (character_bridge, world_bridge)
- [ ] Add `export_for_snack(target_snack)` method
- [ ] Add `import_from_snack(source_spool)` method
- [ ] Add data transformation rules (Eamon -> ACS mapping)
- [ ] Add validation for cross-snack data integrity

### 2.6 Add LENS auto-capture interval configuration
- [ ] Add `set_capture_interval(seconds)` to LENSEngine
- [ ] Add `set_capture_interval_type(frame|time|event)` to LENSEngine
- [ ] Add `auto_capture()` integration with game loop
- [ ] Add `capture_on_event(event_name)` configuration

---

## 🚀 Sprint 3: Snack Container CLI (Phase 3)

**Goal**: Complete the CLI for managing snacks (register, run, stop, pack, install).

### 3.1 Add `snack create` command
- [ ] Add `_cmd_snack_create()` to CLI
- [ ] Generate snack directory structure (snack.yaml, emulator/, lens/, skin/, mcp/, scripts/)
- [ ] Generate default snack.yaml manifest
- [ ] Generate boot.bbc entrypoint template
- [ ] Add `--lang` flag (bbc, python)
- [ ] Add `--entry` flag for custom entrypoint

### 3.2 Add `snack run` command
- [ ] Add `_cmd_snack_run()` to CLI
- [ ] Load snack manifest from directory
- [ ] Initialize interpreter with snack config
- [ ] Attach LENS/SKIN/MCP/Spool engines
- [ ] Execute entrypoint script
- [ ] Add `--skin` flag for skin selection
- [ ] Add `--export` flag for export format

### 3.3 Add `snack stop` command
- [ ] Add `_cmd_snack_stop()` to CLI
- [ ] Send MCP QUIT command to running snack
- [ ] Wait for process termination
- [ ] Handle force kill with SIGKILL

### 3.4 Add `snack list` command
- [ ] Add `_cmd_snack_list()` to CLI
- [ ] Scan snack directories
- [ ] Display registered snacks with metadata
- [ ] Add `--lane` filter (ucode1, ucode2, ucode3)

### 3.5 Add `snack pack` command
- [ ] Add `_cmd_snack_pack()` to CLI
- [ ] Create .snack archive (tar.gz or zip)
- [ ] Include all snack files
- [ ] Add manifest validation before packing

### 3.6 Add `snack install` command
- [ ] Add `_cmd_snack_install()` to CLI
- [ ] Extract .snack archive to snacks directory
- [ ] Validate manifest after extraction
- [ ] Register snack in snack registry

### 3.7 Add `snackpack run` command
- [ ] Add `_cmd_snackpack_run()` to CLI
- [ ] Load snackpack manifest
- [ ] Display snack selection menu
- [ ] Launch selected snack with shared LENS/SKIN

### 3.8 Add `mcp send` command
- [ ] Add `_cmd_mcp_send()` to CLI
- [ ] Connect to running snack's MCP channel
- [ ] Send command and wait for response
- [ ] Support `snack:name command:cmd` syntax

### 3.9 Add `spool` commands
- [ ] Add `_cmd_spool_list()` to CLI
- [ ] Add `_cmd_spool_export()` to CLI
- [ ] Add `_cmd_spool_import()` to CLI
- [ ] Add `--format` flag (json, msgpack, zstd)

---

## 🚀 Sprint 4: NetHack & Eamon Integration (Phase 4)

**Goal**: Get real classic games running in uCode1 with full LENS/SKIN/MCP support.

### 4.1 Create NetHack snack manifest
- [ ] Create `snacks/nethack/snack.yaml`
- [ ] Configure tty backend for teletext rendering
- [ ] Set up LENS auto-capture for HP%, GOLD%, ROOM%, etc.
- [ ] Set up SKIN with teletext_classic default
- [ ] Add MCP commands (PAUSE, RESUME, SAVE, RESTORE)

### 4.2 Create NetHack boot script
- [ ] Create `snacks/nethack/scripts/boot.bbc`
- [ ] Initialize LENS/SKIN/MCP engines
- [ ] Launch NetHack with tty backend
- [ ] Set up teletext renderer bridge
- [ ] Add auto-capture on game state changes

### 4.3 Create Eamon snack manifest
- [ ] Create `snacks/eamon/snack.yaml` (enhance existing)
- [ ] Configure Apple II emulation (or BBC BASIC port)
- [ ] Set up LENS for Eamon variables (HP%, GOLD%, ROOM%, WEAPON%, ARMOR%)
- [ ] Set up SKIN with paper_retro default
- [ ] Add disk-swapping script for master + adventure disks

### 4.4 Create Eamon boot script
- [ ] Create `snacks/eamon/scripts/boot.bbc`
- [ ] Initialize LENS/SKIN/MCP engines
- [ ] Load Eamon master disk
- [ ] Display adventure selection menu
- [ ] Set up teletext renderer bridge

### 4.5 Add teletext renderer bridge for game output
- [ ] Create `core_py/ceefax/bridge.py`
- [ ] Implement `GameToTeletextBridge` class
- [ ] Convert game output (ANSI/ASCII) to teletext grid (40x25)
- [ ] Apply SKIN styles to teletext output
- [ ] Handle colour mapping (game colours -> teletext palette)

### 4.6 Add game-specific LENS extraction rules
- [ ] Add NetHack variable mapping (HP -> HP%, XP -> XP%, etc.)
- [ ] Add Eamon variable mapping (strength -> STR%, etc.)
- [ ] Add room/level change detection
- [ ] Add combat event detection
- [ ] Add item pickup/drop detection

### 4.7 Create classic_adventures snackpack
- [ ] Create `snackpacks/classic_adventures/snackpack.yaml`
- [ ] Include nethack and eamon snacks
- [ ] Add shared LENS rules for common variables
- [ ] Add shared SKIN rules
- [ ] Add launcher menu script

### 4.8 Add game state export for publishing
- [ ] Add NetHack spool export (character dump)
- [ ] Add Eamon spool export (adventure state)
- [ ] Add export to Tailwind Prose format
- [ ] Add export to Marp slide format
- [ ] Add export to JSON for external tools

---

## 🚀 Sprint 5: Documentation & Release (Phase 7)

**Goal**: Ship uCode1 v0.1.0 with complete documentation and release pipeline.

### 5.1 Write CLI documentation
- [ ] Document all CLI commands (snack, mcp, spool)
- [ ] Add usage examples for each command
- [ ] Add command reference with all flags
- [ ] Add exit codes and error handling docs

### 5.2 Write BBC BASIC extension documentation
- [ ] Document all PROC_LENS_* extensions
- [ ] Document all PROC_SKIN_* extensions
- [ ] Document all PROC_MCP_* / FN_MCP_* extensions
- [ ] Document all PROC_SPOOL_* / FN_SPOOL_* extensions
- [ ] Add code examples for each extension

### 5.3 Write quick-start tutorial
- [ ] "Hello, Teletext World!" tutorial
- [ ] "Adding LENS to your game" tutorial
- [ ] "Changing SKIN at runtime" tutorial
- [ ] "Saving and loading with Spool" tutorial
- [ ] "Packaging your game as a Snack" tutorial

### 5.4 Write snack/snackpack developer guide
- [ ] Document snack.yaml manifest format
- [ ] Document snackpack.yaml format
- [ ] Document LENS configuration
- [ ] Document SKIN configuration
- [ ] Document MCP command handlers
- [ ] Document dependency resolution

### 5.5 Set up pip package
- [ ] Create `setup.py` or `pyproject.toml`
- [ ] Configure package metadata (name, version, author)
- [ ] List dependencies (grpcio, msgpack, zstd, etc.)
- [ ] Add console_scripts entry point
- [ ] Test pip install from local source

### 5.6 Add version management
- [ ] Add `__version__` to `ucode1/__init__.py`
- [ ] Add `version` command to CLI
- [ ] Add version check on startup
- [ ] Add `--version` flag to CLI

### 5.7 Create release checklist
- [ ] Run full test suite
- [ ] Run CI checks (lint, format, type-check)
- [ ] Build pip package
- [ ] Tag release in git
- [ ] Create GitHub release with changelog
- [ ] Publish to PyPI (optional)

### 5.8 Add changelog
- [ ] Create `CHANGELOG.md`
- [ ] Document v0.1.0 features
- [ ] Document known issues
- [ ] Document future roadmap

---

## 📋 Execution Order

1. **Sprint 1** → Core Interpreter (unlocks everything)
2. **Sprint 2** → LENS/SKIN/MCP/Spool Polish (integration layers)
3. **Sprint 3** → Snack Container CLI (user-facing tooling)
4. **Sprint 4** → NetHack & Eamon Integration (real games)
5. **Sprint 5** → Documentation & Release (ship it)
