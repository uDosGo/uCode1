# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-13

### Added
- Grid/Cell foundation with UDX addressing (L{level}-{gridXY}-{cellXY}-{layer})
- BBC BASIC interpreter with 40 lessons across 4 levels (Beginner → Advanced)
- Teletext engine (Ceefax-style page viewer with 3-digit navigation)
- Grid algebra core: GridCell, GridTransform, ColourPalette, TeletextPage
- 5 example BBC BASIC programs (hello.bas, calculator.bas, etc.)
- 16 integration tests covering cell, character, CLI, feed, MCP, skins, VDU-to-Ceetex
- MCP server integration for agent-based interactions
- Feed event archiving to Cells
- Liquid template engine for dynamic content
- Snack CLI for snack/container management
- VDU-to-Ceetex converter for teletext rendering
- Agent API with adventure demo snack
- Skins system for visual customization
- Narrator lexicon integration

### Changed
- Version bumped from 0.1.0 to 1.0.0
- Stripped dead ceefax/ directory and dead core_py modules
- Removed docs/legacy/ and docs/review/ directories
- Updated all documentation for v1.0.0 release

### Fixed
- Test suite passes consistently (16/16 tests)
- CLI entry point resolves correctly
- Package metadata updated for PyPI readiness

### Security
- No external network dependencies
- Fully local execution model
- No cloud or telemetry

[1.0.0]: https://github.com/uDosGo/uCode1/releases/tag/v1.0.0
