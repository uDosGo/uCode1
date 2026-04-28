# uCode1 Resource Registry

**Purpose**: Central index of all uCode1 learning resources, references, and external links

## Resource Categories

### 1. Official References
- BBC Micro documentation
- BBC BASIC manuals
- uCode1 language specification

### 2. Tutorials & Guides
- Getting started with uCode1
- Teletext programming
- Game development
- Vault operations

### 3. Example Programs
- Classic games in uCode1
- Teletext applications
- Utility scripts
- Demo programs

### 4. External Resources
- BBC Micro archives
- Retro computing references
- Modern BASIC resources

## Resource Format

Each resource follows this structure:

```
Resource/
├── metadata.json      # Resource metadata
├── content.md         # Main content
├── examples/          # Example code
└── assets/            # Images, diagrams
```

### metadata.json Format

```json
{
  "id": "bbc-basic-manual",
  "title": "BBC BASIC Reference Manual",
  "description": "Complete BBC BASIC language reference",
  "version": "1.0",
  "authors": ["Acorn Computers"],
  "source": "https://www.bbcbasic.co.uk/bbcsdl/manual/index.html",
  "tags": ["reference", "manual", "bbc", "basic"],
  "format": "markdown",
  "license": "Public Domain",
  "created": "1981-01-01",
  "updated": "2024-01-01"
}
```

## External Resource Index

### BBC Micro Resources

1. **BBC Micro Computer**
   - URL: https://www.bbcmicro.co.uk
   - Type: Archive
   - Description: Complete BBC Micro archive

2. **BBC BASIC Reference**
   - URL: https://www.bbcbasic.co.uk
   - Type: Manual
   - Description: Official BBC BASIC documentation

3. **BBCSDL Manual**
   - URL: https://www.bbcbasic.co.uk/bbcsdl/manual/index.html
   - Type: Manual
   - Description: Modern BBC BASIC implementation

### Retro Computing Resources

1. **8-Bit Software Archive**
   - URL: https://8bs.com
   - Type: Archive
   - Description: Classic software preservation

2. **World of Spectrum**
   - URL: https://worldofspectrum.org
   - Type: Archive
   - Description: Sinclair Spectrum resources

## uDos Feed Integration

Resources can be converted to uDos feed format:

```json
{
  "feed": {
    "id": "ucode1-resources",
    "title": "uCode1 Resource Library",
    "description": "Learning resources for uCode1 programming",
    "version": "1.0",
    "items": [
      {
        "id": "bbc-basic-manual",
        "title": "BBC BASIC Reference Manual",
        "type": "reference",
        "url": "https://www.bbcbasic.co.uk/bbcsdl/manual/index.html",
        "content": "Complete BBC BASIC language reference...",
        "tags": ["bbc", "basic", "manual", "reference"]
      },
      {
        "id": "teletext-guide",
        "title": "Teletext Programming Guide",
        "type": "tutorial",
        "url": "/resources/guides/teletext.md",
        "content": "How to create teletext applications...",
        "tags": ["teletext", "guide", "tutorial"]
      }
    ]
  }
}
```

## Resource Management

### Adding New Resources

1. Create resource directory in appropriate category
2. Add `metadata.json` with resource information
3. Add content in Markdown format
4. Add examples if applicable
5. Update registry index

### Updating Resources

1. Modify content files
2. Update metadata version and date
3. Test examples
4. Update registry

### Removing Resources

1. Archive old version
2. Remove from registry
3. Update any dependencies

## Integration with uCode1

### Resource Browser

```python
# ucode1/resources/browser.py
class ResourceBrowser:
    def __init__(self):
        self.registry = self.load_registry()
        
    def load_registry(self):
        """Load resource registry"""
        with open("resources/registry/index.json") as f:
            return json.load(f)
    
    def search(self, query):
        """Search resources by tag or title"""
        return [r for r in self.registry if 
                query in r["title"] or query in r["tags"]]
    
    def get_resource(self, resource_id):
        """Load specific resource"""
        path = f"resources/{resource_id}/content.md"
        with open(path) as f:
            return f.read()
```

### Feed Generator

```python
# ucode1/feeds/generator.py
class FeedGenerator:
    def __init__(self):
        self.browser = ResourceBrowser()
        
    def generate_feed(self, tag_filter=None):
        """Generate uDos feed from resources"""
        resources = self.browser.registry
        
        if tag_filter:
            resources = [r for r in resources if tag_filter in r["tags"]]
        
        return {
            "feed": {
                "id": "ucode1-resources",
                "title": "uCode1 Resources",
                "items": resources
            }
        }
```

## Example Resource

### BBC BASIC Manual

```
resources/references/bbc-basic-manual/
├── metadata.json
├── content.md
└── examples/
    ├── hello.bas
    └── graphics.bas
```

**metadata.json**:
```json
{
  "id": "bbc-basic-manual",
  "title": "BBC BASIC Reference Manual",
  "description": "Complete reference for BBC BASIC programming language",
  "source": "https://www.bbcbasic.co.uk/bbcsdl/manual/index.html",
  "tags": ["reference", "manual", "bbc", "basic", "programming"],
  "format": "markdown",
  "license": "Public Domain",
  "related": ["teletext-guide", "bbc-micro-history"]
}
```

**content.md**:
```markdown
# BBC BASIC Reference Manual

## Introduction

BBC BASIC is a version of the BASIC programming language that was designed for the BBC Micro computer...

## Language Reference

### Commands

- `PRINT`: Display text
- `INPUT`: Get user input
- `GOTO`: Jump to line
- `IF...THEN`: Conditional execution
- `FOR...NEXT`: Loops

### Graphics

- `PLOT`: Draw points
- `DRAW`: Draw lines
- `CIRCLE`: Draw circles
- `MODE`: Set graphics mode

## Examples

See `examples/` directory for sample programs.
```

**examples/hello.bas**:
```basic
10 PRINT "Hello, BBC Micro!"
20 INPUT "What is your name? ", name$
30 PRINT "Hello, "; name$;
40 END
```

## Integration with uCode1

uCode1 extends BBC BASIC with modern features while maintaining compatibility.
```

## License

All resources are indexed with their original licenses preserved.
```

## Maintenance

### Resource Curators

- **External Links**: Check quarterly for availability
- **Internal Content**: Review annually for accuracy
- **Examples**: Test with each uCode1 release

### Versioning

Resources follow semantic versioning:
- `MAJOR`: Breaking changes
- `MINOR`: New content
- `PATCH`: Corrections

## Future Enhancements

1. **Automated Scraping**: Pull updates from external sources
2. **User Contributions**: Allow community submissions
3. **Rating System**: Popular/high-quality resources
4. **Search Engine**: Full-text search across resources
5. **Translation**: Multilingual resources

---

This resource library provides a comprehensive reference system for uCode1 developers, integrating external BBC resources with internal documentation and examples, all accessible through the uDos feed format.