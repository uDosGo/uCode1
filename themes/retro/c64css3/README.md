# C64CSS3 Theme - uCode1 BBC BASIC Interpreter

This is the **C64CSS3** theme by Pixelambacht, adapted for use with the uCode1 BBC BASIC interpreter.

## Features

- **Authentic C64 Look & Feel** - Uses the original CSS3 C64 styling
- **C64 User Mono Font** - Includes the authentic Commodore 64 font
- **BBC BASIC Interpreter UI** - Full-featured BBC BASIC environment
- **Codec Editor** - Edit BBC BASIC programs with syntax highlighting
- **Interactive Console** - Direct command entry with `>_` prompt
- **VDU Command Support** - Process BBC BASIC VDU commands
- **Screen Mode Selection** - All 8 BBC Micro modes
- **Color Controls** - Foreground and background color selection
- **Program Management** - RUN, STOP, LIST, NEW, LOAD, SAVE, CLS
- **Real-time Clock** - Status bar clock
- **Line Counter** - Track program lines

## Files

- `index.html` - Main BBC BASIC Interpreter UI
- `css.css` - C64-themed stylesheet
- `fonts/` - C64 User Mono and Giana fonts
- `prefixfree.min.js` - CSS prefix handling for cross-browser compatibility
- `pixelambacht-logo.png` - Original author logo
- `README.md` - This file

## Usage

### Standalone
Simply open `index.html` in any modern web browser. The UI provides:

- Code editor with BBC BASIC program entry
- Interactive console with authentic C64 styling
- Toolbar with common BBC BASIC commands
- VDU mode and color selectors

### Integration with uCode1

The UI exposes a JavaScript API for integration with the actual BBC BASIC interpreter:

```javascript
window.C64BBCBasic = {
    print: (text) => {},        // Print text to output
    clear: () => {},             // Clear the screen
    setStatus: (status) => {},   // Set status indicator
    execute: (code) => {}        // Execute BBC BASIC code
};
```

To integrate with the Python uCode1 core:

```python
from ucode1.core_py.bbc import BBCBasicInterpreter, VDUDriver

# Create VDU driver
vdu = VDUDriver()

# Create interpreter
interpreter = BBCBasicInterpreter(vdu_handler=vdu)

# Load and run program
program = [
    '10 PRINT "HELLO WORLD"',
    '20 PRINT "FROM BBC BASIC"',
    '30 END'
]
interpreter.load_program(program)
interpreter.run()

# Get output
output = vdu.get_output()
```

## BBC BASIC Commands

### Program Management
- `RUN` - Run the program
- `STOP` - Stop program execution
- `NEW` - Clear the program
- `LIST` - List the program
- `LOAD` - Load program from file (WIP)
- `SAVE` - Save program to file (WIP)
- `CLS` - Clear the screen

### Editor
- Type line number followed by BASIC code (e.g., `10 PRINT "HELLO"`)
- Press Enter to add line to program
- Use Escape to clear input

### VDU Commands
| Command | Description |
|---------|-------------|
| VDU 17,c | Set text color (0-7) |
| VDU 18,c,b | Set text and background colors |
| VDU 22,n | Set screen mode (0-7) |
| VDU 32-126 | Print ASCII characters |

### Screen Modes
- Mode 0: 640x560, 8 colors
- Mode 1: 320x256, 4 colors
- Mode 2: 640x512, 2 colors
- Mode 3: Text (80x25)
- Mode 4: 320x256, 16 colors
- Mode 5: 640x512, 4 colors
- Mode 6: Teletext 40x25
- Mode 7: Teletext 40x25 (default)

### Colors
| Code | Color |
|------|-------|
| 0 | Black |
| 1 | Red |
| 2 | Green |
| 3 | Yellow |
| 4 | Blue |
| 5 | Magenta |
| 6 | Cyan |
| 7 | White |

## Theme Customization

The theme uses the following colors:
- Background: `#222`
- Container: `#1a1a2e`
- Borders: `#000`
- Text: `#0ff` (Cyan)
- Accent: `#0ff` (Cyan)
- Danger: `#f00` (Red)

To customize, modify the inline styles in `index.html`.

## Credits

- **Original C64CSS3 Theme**: [Pixelambacht](https://pixelambacht.nl/2013/css3-c64/) - CSS Framework
- **BBC BASIC Integration**: uCode1/uDos Development Team
- **Fonts**: C64 User Mono by various authors

## License

The original C64CSS3 theme is licensed under its original terms. The uCode1 integration is licensed under MIT.

## Links

- [Original C64CSS3 Theme](https://pixelambacht.nl/2013/css3-c64/)
- [uCode1 Documentation](https://github.com/fredbook/DevStudio)
- [BBC BASIC Reference](https://en.wikipedia.org/wiki/BBC_BASIC)

---

**Part of uCode1 - The universal code execution framework for uDos**
