//! USXD grid operations

use super::{UsxdDocument, UsxdCell};
use std::collections::HashMap;

/// Grid operations for USXD documents
pub trait UsxdGridOperations {
    /// Get grid as string representation
    fn to_string_representation(&self) -> String;
    
    /// Get grid as string representation with colors
    fn to_colored_string(&self) -> String;
    
    /// Get subgrid
    fn get_subgrid(&self, row: usize, col: usize, height: usize, width: usize) -> Result<UsxdDocument, String>;
    
    /// Find cells by character
    fn find_cells_by_char(&self, ch: char) -> Vec<(usize, usize)>;
    
    /// Count occurrences of character
    fn count_char_occurrences(&self, ch: char) -> usize;
    
    /// Get grid statistics
    fn get_statistics(&self) -> HashMap<char, usize>;
}

impl UsxdGridOperations for UsxdDocument {
    fn to_string_representation(&self) -> String {
        let mut result = String::new();
        for row in &self.grid {
            for cell in row {
                result.push(cell.char);
            }
            result.push('\n');
        }
        result
    }

    fn to_colored_string(&self) -> String {
        let mut result = String::new();
        for row in &self.grid {
            for cell in row {
                // Simple ANSI color support
                if let Some(fg) = &cell.fg_color {
                    match fg.as_str() {
                        "red" => result.push_str("\x1b[31m"),
                        "green" => result.push_str("\x1b[32m"),
                        "yellow" => result.push_str("\x1b[33m"),
                        "blue" => result.push_str("\x1b[34m"),
                        "magenta" => result.push_str("\x1b[35m"),
                        "cyan" => result.push_str("\x1b[36m"),
                        "white" => result.push_str("\x1b[37m"),
                        _ => {}
                    }
                }
                result.push(cell.char);
                if cell.fg_color.is_some() {
                    result.push_str("\x1b[0m"); // Reset
                }
            }
            result.push('\n');
        }
        result
    }

    fn get_subgrid(&self, row: usize, col: usize, height: usize, width: usize) -> Result<UsxdDocument, String> {
        if row + height > self.dimensions.0 || col + width > self.dimensions.1 {
            return Err(format!("Subgrid out of bounds: ({}, {}) + ({}, {}) > ({}, {})", 
                row, col, height, width, self.dimensions.0, self.dimensions.1));
        }

        let mut subgrid_doc = UsxdDocument::new(
            &format!("Subgrid of {}", self.title),
            height,
            width
        );

        for r in 0..height {
            for c in 0..width {
                let cell = self.get_cell(row + r, col + c).unwrap().clone();
                subgrid_doc.set_cell(r, c, cell).unwrap();
            }
        }

        Ok(subgrid_doc)
    }

    fn find_cells_by_char(&self, ch: char) -> Vec<(usize, usize)> {
        let mut positions = Vec::new();
        for (row_idx, row) in self.grid.iter().enumerate() {
            for (col_idx, cell) in row.iter().enumerate() {
                if cell.char == ch {
                    positions.push((row_idx, col_idx));
                }
            }
        }
        positions
    }

    fn count_char_occurrences(&self, ch: char) -> usize {
        self.find_cells_by_char(ch).len()
    }

    fn get_statistics(&self) -> HashMap<char, usize> {
        let mut stats = HashMap::new();
        for row in &self.grid {
            for cell in row {
                *stats.entry(cell.char).or_insert(0) += 1;
            }
        }
        stats
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_to_string_representation() {
        let mut doc = UsxdDocument::new("Test", 2, 3);
        
        let mut cell1 = UsxdCell::default();
        cell1.char = 'A';
        doc.set_cell(0, 0, cell1).unwrap();
        
        let mut cell2 = UsxdCell::default();
        cell2.char = 'B';
        doc.set_cell(0, 1, cell2).unwrap();
        
        let mut cell3 = UsxdCell::default();
        cell3.char = 'C';
        doc.set_cell(1, 2, cell3).unwrap();

        let result = doc.to_string_representation();
        let lines: Vec<&str> = result.trim().split('\n').collect();
        assert_eq!(lines.len(), 2);
        assert_eq!(lines[0], "AB ");
        assert_eq!(lines[1], "  C");
    }

    #[test]
    fn test_find_cells_by_char() {
        let mut doc = UsxdDocument::new("Test", 3, 3);
        
        let mut cell = UsxdCell::default();
        cell.char = 'X';
        doc.set_cell(0, 0, cell.clone()).unwrap();
        doc.set_cell(1, 1, cell.clone()).unwrap();
        doc.set_cell(2, 2, cell).unwrap();

        let positions = doc.find_cells_by_char('X');
        assert_eq!(positions.len(), 3);
        assert!(positions.contains(&(0, 0)));
        assert!(positions.contains(&(1, 1)));
        assert!(positions.contains(&(2, 2)));
    }

    #[test]
    fn test_count_char_occurrences() {
        let mut doc = UsxdDocument::new("Test", 2, 2);
        
        let mut cell_a = UsxdCell::default();
        cell_a.char = 'A';
        doc.set_cell(0, 0, cell_a.clone()).unwrap();
        doc.set_cell(0, 1, cell_a.clone()).unwrap();
        
        let mut cell_b = UsxdCell::default();
        cell_b.char = 'B';
        doc.set_cell(1, 0, cell_b).unwrap();

        assert_eq!(doc.count_char_occurrences('A'), 2);
        assert_eq!(doc.count_char_occurrences('B'), 1);
        assert_eq!(doc.count_char_occurrences(' '), 1); // The remaining cell
    }

    #[test]
    fn test_get_statistics() {
        let mut doc = UsxdDocument::new("Test", 2, 2);
        
        let mut cell_a = UsxdCell::default();
        cell_a.char = 'A';
        doc.set_cell(0, 0, cell_a.clone()).unwrap();
        doc.set_cell(0, 1, cell_a).unwrap();
        
        let mut cell_b = UsxdCell::default();
        cell_b.char = 'B';
        doc.set_cell(1, 0, cell_b).unwrap();

        let stats = doc.get_statistics();
        assert_eq!(stats.get(&'A'), Some(&2));
        assert_eq!(stats.get(&'B'), Some(&1));
        assert_eq!(stats.get(&' '), Some(&1));
    }

    #[test]
    fn test_get_subgrid() {
        let mut doc = UsxdDocument::new("Test", 4, 4);
        
        // Create a pattern
        for i in 0..4 {
            let mut cell = UsxdCell::default();
            cell.char = char::from_u32('A' as u32 + i).unwrap();
            doc.set_cell(0, i as usize, cell).unwrap();
        }

        let subgrid = doc.get_subgrid(0, 1, 2, 2).unwrap();
        assert_eq!(subgrid.dimensions, (2, 2));
        assert_eq!(subgrid.get_cell(0, 0).unwrap().char, 'B');
        assert_eq!(subgrid.get_cell(0, 1).unwrap().char, 'C');
        assert_eq!(subgrid.get_cell(1, 0).unwrap().char, ' ');
        assert_eq!(subgrid.get_cell(1, 1).unwrap().char, ' ');
    }

    #[test]
    fn test_get_subgrid_out_of_bounds() {
        let doc = UsxdDocument::new("Test", 2, 2);
        let result = doc.get_subgrid(1, 1, 2, 2);
        assert!(result.is_err());
    }
}