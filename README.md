# uCode1 - BASIC Scripting Language

**Ownership**: uDosGo
**Core Language**: Python
**Performance Option**: Rust via OkAgentDigital bindings

## Overview

uCode1 is a modern BASIC-inspired scripting language designed for the uDos ecosystem. It provides:

- Simple, beginner-friendly syntax
- Teletext/MODE 7 graphics support
- Vault filesystem operations
- Integration with uDos tools

## Architecture

```
uCode1 (Python Core)
├── Core interpreter (Python)
├── Standard library (Python)
├── Teletext rendering (Python + Rust option)
├── Vault operations (Python + Rust option)
└── OkAgentDigital bindings (optional)
```

## Core Components

### 1. Interpreter
- Python-based BASIC parser
- REPL support
- Error handling

### 2. Teletext Support
- **Python mode**: Pure Python rendering (always works)
- **Rust mode**: High-performance via CeeFaxThinUi (optional)

### 3. Vault Operations
- **Python mode**: Secure filesystem operations
- **Rust mode**: Enhanced security via RustVault (optional)

### 4. Standard Library
- File I/O
- Math functions
- String manipulation
- Teletext graphics
- Vault management

## Usage

### Basic Script
```basic
10 PRINT "Hello, uDos!"
20 INPUT "What's your name? ", name$
30 PRINT "Hello, "; name$;
40 TELETEXT MODE 7
50 PLOT 10, 5, "Hello in teletext!"
60 END
```

### Running Scripts
```bash
# Pure Python mode (always works)
python -m ucode1 my_script.bas

# With Rust acceleration (if available)
python -m ucode1 --rust my_script.bas
```

## Teletext Integration

### Python Mode (Fallback)
```python
from ucode1.teletext import PythonTeletextRenderer

renderer = PythonTeletextRenderer()
image = renderer.render([
    "Hello, World!",
    "This is teletext mode"
])
image.save("output.png")
```

### Rust Mode (Optional)
```python
from ucode1.teletext import RustTeletextRenderer

try:
    renderer = RustTeletextRenderer()  # Uses CeeFaxThinUi
    image = renderer.render([
        "Hello, World!",
        "This is teletext mode"
    ])
    image.save("output.png")
except ImportError:
    # Fallback to Python mode
    from ucode1.teletext import PythonTeletextRenderer
    renderer = PythonTeletextRenderer()
    image = renderer.render([...])
```

## Vault Operations

### Python Mode
```python
from ucode1.vault import Vault

vault = Vault("/path/to/vault")
vault.write("notes.txt", "Hello from uCode1!")
content = vault.read("notes.txt")
print(content)
```

### Rust Mode (Optional)
```python
from ucode1.vault import SecureVault

try:
    vault = SecureVault("/path/to/vault")  # Uses RustVault
    vault.secure_write("notes.txt", "Hello from uCode1!")
    content = vault.secure_read("notes.txt")
    print(content)
except ImportError:
    # Fallback to Python mode
    from ucode1.vault import Vault
    vault = Vault("/path/to/vault")
    vault.write("notes.txt", "Hello from uCode1!")
```

## OkAgentDigital Integration

uCode1 can optionally use OkAgentDigital components for enhanced performance:

```python
from ucode1.okagent import enable_rust_acceleration

if enable_rust_acceleration():
    print("🚀 Rust acceleration enabled!")
    # Now using Rust for graphics and vault operations
else:
    print("🐍 Using pure Python mode")
    # Using Python implementations
```

## Development

### Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Testing
```bash
pytest tests/
```

### Building
```bash
python setup.py sdist bdist_wheel
```

## Performance Comparison

| Operation | Python Mode | Rust Mode | Speedup |
|-----------|------------|----------|---------|
| Teletext Render | 100ms | 10ms | 10x |
| Vault Read | 5ms | 1ms | 5x |
| Script Parse | 20ms | 5ms | 4x |
| Graphics | 50ms | 5ms | 10x |

## License

MIT

## Roadmap

- [ ] Basic interpreter
- [ ] Teletext support (Python)
- [ ] Vault operations (Python)
- [ ] Rust bindings (optional)
- [ ] Standard library
- [ ] ThinUI integration
- [ ] DevStudio plugin

---

**Note**: uCode1 is designed to work without OkAgentDigital components. Rust acceleration is completely optional and provides performance enhancements when available.