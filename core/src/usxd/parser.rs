//! USXD parser implementation

use super::{UsxdDocument, UsxdCell, UsxdComponent};
use std::collections::HashMap;

/// Parse a simple ASCII grid into a USXD document
pub fn parse_ascii_grid(title: &str, grid: &[&str]) -> UsxdDocument {
    let rows = grid.len();
    if rows == 0 {
        return UsxdDocument::new(title, 0, 0);
    }
    let cols = grid[0].len();

    let mut doc = UsxdDocument::new(title, rows, cols);

    for (row_idx, row) in grid.iter().enumerate() {
        for (col_idx, ch) in row.chars().enumerate() {
            let mut cell = UsxdCell::default();
            cell.char = ch;
            doc.set_cell(row_idx, col_idx, cell).unwrap();
        }
    }

    doc
}

/// Parse a USXD document with components
pub fn parse_with_components(title: &str, grid: &[&str], components: &[UsxdComponent]) -> UsxdDocument {
    let mut doc = parse_ascii_grid(title, grid);

    for component in components {
        doc.add_component(component.clone());
        
        // Mark cells as belonging to this component
        for (row, col) in &component.cells {
            if let Some(_cell) = doc.get_cell(*row, *col) {
                // This would need to be handled differently since we can't mutate through get_cell
                // In a real implementation, we'd need to update the cell properly
            }
        }
    }

    doc
}

/// Parse a simple USXD format from text
/// Format:
/// title: My Grid
/// rows: 3
/// cols: 3
/// grid:
/// ABC
/// DEF
/// GHI
pub fn parse_simple_usxd(text: &str) -> Result<UsxdDocument, String> {
    let mut title = "Untitled".to_string();
    let mut rows = 0;
    let mut cols = 0;
    let mut grid_lines = Vec::new();

    let mut in_grid = false;

    for line in text.lines() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }

        if line.starts_with("title:") {
            title = line["title:".len()..].trim().to_string();
        } else if line.starts_with("rows:") {
            rows = line["rows:".len()..].trim().parse().map_err(|e| format!("Invalid rows: {}", e))?;
        } else if line.starts_with("cols:") {
            cols = line["cols:".len()..].trim().parse().map_err(|e| format!("Invalid cols: {}", e))?;
        } else if line == "grid:" {
            in_grid = true;
        } else if in_grid {
            grid_lines.push(line.to_string());
        }
    }

    if grid_lines.len() != rows {
        return Err(format!("Expected {} rows, got {}", rows, grid_lines.len()));
    }

    for line in &grid_lines {
        if line.len() != cols {
            return Err(format!("Expected {} cols, got {}", cols, line.len()));
        }
    }

    let grid_refs: Vec<&str> = grid_lines.iter().map(|s| s.as_str()).collect();
    Ok(parse_ascii_grid(&title, &grid_refs))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    #[test]
    fn test_parse_ascii_grid() {
        let grid = vec![
            "ABC",
            "DEF",
            "GHI",
        ];
        let grid_refs: Vec<String> = grid.iter().cloned().collect();

        let doc = parse_ascii_grid("Test Grid", &grid_refs);
        
        assert_eq!(doc.title, "Test Grid");
        assert_eq!(doc.dimensions, (3, 3));
        
        assert_eq!(doc.get_cell(0, 0).unwrap().char, 'A');
        assert_eq!(doc.get_cell(0, 1).unwrap().char, 'B');
        assert_eq!(doc.get_cell(0, 2).unwrap().char, 'C');
        
        assert_eq!(doc.get_cell(1, 0).unwrap().char, 'D');
        assert_eq!(doc.get_cell(1, 1).unwrap().char, 'E');
        assert_eq!(doc.get_cell(1, 2).unwrap().char, 'F');
        
        assert_eq!(doc.get_cell(2, 0).unwrap().char, 'G');
        assert_eq!(doc.get_cell(2, 1).unwrap().char, 'H');
        assert_eq!(doc.get_cell(2, 2).unwrap().char, 'I');
    }

    #[test]
    fn test_parse_with_components() {
        let grid = vec![
            "ABC",
            "DEF",
            "GHI",
        ];
        let grid_refs: Vec<String> = grid.iter().cloned().collect();

        let components = vec![
            UsxdComponent {
                id: "comp1".to_string(),
                name: "Component1".to_string(),
                r#type: "widget".to_string(),
                properties: HashMap::new(),
                cells: vec![(0, 0), (1, 1)],
            },
        ];

        let doc = parse_with_components("Test Grid", &grid_refs, &components);
        
        assert_eq!(doc.title, "Test Grid");
        assert_eq!(doc.components.len(), 1);
        assert!(doc.get_component("comp1").is_some());
    }

    #[test]
    fn test_parse_simple_usxd() {
        let text = 
"title: My Test Grid
rows: 2
cols: 3
grid:
ABC
DEF";

        let doc = parse_simple_usxd(text).unwrap();
        
        assert_eq!(doc.title, "My Test Grid");
        assert_eq!(doc.dimensions, (2, 3));
        
        assert_eq!(doc.get_cell(0, 0).unwrap().char, 'A');
        assert_eq!(doc.get_cell(0, 1).unwrap().char, 'B');
        assert_eq!(doc.get_cell(0, 2).unwrap().char, 'C');
        
        assert_eq!(doc.get_cell(1, 0).unwrap().char, 'D');
        assert_eq!(doc.get_cell(1, 1).unwrap().char, 'E');
        assert_eq!(doc.get_cell(1, 2).unwrap().char, 'F');
    }

    #[test]
    fn test_parse_simple_usxd_errors() {
        // Test invalid rows
        let text1 = 
"title: Test
rows: abc
cols: 3
grid:
ABC
DEF";
        assert!(parse_simple_usxd(text1).is_err());

        // Test row count mismatch
        let text2 = 
"title: Test
rows: 3
cols: 3
grid:
ABC
DEF";
        assert!(parse_simple_usxd(text2).is_err());

        // Test col count mismatch
        let text3 = 
"title: Test
rows: 2
cols: 3
grid:
ABC
DEFG";
        assert!(parse_simple_usxd(text3).is_err());
    }
}