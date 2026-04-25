// TUI - Terminal User Interface for uCode1
// Grid/teletext renderer with block graphics

use ratatui::{
    prelude::*,
    widgets::{Block, Borders, Paragraph, List, ListItem, Wrap},
};
use crossterm::{
    event::{self, Event, KeyCode, KeyEventKind},
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
    execute,
};
use std::io;

pub struct AppState {
    pub current_screen: Screen,
    pub vault_path: String,
    pub notes: Vec<String>,
    pub selected_note: Option<String>,
    pub note_content: String,
    pub input_mode: InputMode,
    pub input_buffer: String,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Screen {
    NotesList,
    NoteView,
    Help,
    Quit,
}

#[derive(Debug, Clone, PartialEq)]
pub enum InputMode {
    Normal,
    Editing,
}

impl AppState {
    pub fn new(vault_path: &str) -> Self {
        AppState {
            current_screen: Screen::NotesList,
            vault_path: vault_path.to_string(),
            notes: Vec::new(),
            selected_note: None,
            note_content: String::new(),
            input_mode: InputMode::Normal,
            input_buffer: String::new(),
        }
    }

    pub async fn load_notes(&mut self) {
        let mut vault = ucode1_vault_bridge::Vault::new(&self.vault_path, &self.vault_path);
        match vault.list_notes() {
            Ok(notes) => {
                self.notes = notes;
            }
            Err(e) => {
                log::error!("Failed to load notes: {}", e);
            }
        }
    }

    pub async fn load_note_content(&mut self, note_name: &str) {
        let mut vault = ucode1_vault_bridge::Vault::new(&self.vault_path, &self.vault_path);
        match vault.read_note(note_name) {
            Ok(note) => {
                self.note_content = note.content;
            }
            Err(e) => {
                log::error!("Failed to load note {}: {}", note_name, e);
                self.note_content = format!("Error loading note: {}", e);
            }
        }
    }
}

pub struct Tui {
    terminal: Terminal<CrosstermBackend<std::io::Stderr>>,
    pub should_quit: bool,
}

impl Tui {
    pub fn new() -> io::Result<Self> {
        enable_raw_mode()?;
        let mut stdout = io::stderr();
        execute!(stdout, EnterAlternateScreen)?;
        let backend = CrosstermBackend::new(stdout);
        let terminal = Terminal::new(backend)?;
        
        Ok(Tui {
            terminal,
            should_quit: false,
        })
    }

    pub fn draw(&mut self, state: &AppState) -> io::Result<()> {
        self.terminal.draw(|f| {
            let size = f.size();
            
            // Create layout
            let layout = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Length(1), // Header
                    Constraint::Min(1),    // Main content
                    Constraint::Length(1), // Footer
                ].as_ref())
                .split(size);
            
            // Header
            let header = Paragraph::new("uCode1 TUI")
                .block(Block::default().borders(Borders::ALL).title("Header"))
                .alignment(Alignment::Center);
            f.render_widget(header, layout[0]);
            
            // Main content based on current screen
            match state.current_screen {
                Screen::NotesList => {
                    // Draw notes list
                    let items: Vec<ListItem> = state.notes.iter()
                        .map(|note| ListItem::new(note.clone()))
                        .collect();
                    
                    let list = List::new(items)
                        .block(Block::default().borders(Borders::ALL).title("Notes"))
                        .highlight_style(Style::default().add_modifier(Modifier::BOLD));
                    
                    f.render_widget(list, layout[1]);
                }
                Screen::NoteView => {
                    // Draw note view
                    let paragraph = Paragraph::new(state.note_content.clone())
                        .block(Block::default().borders(Borders::ALL).title("Note Content"))
                        .wrap(Wrap { trim: true });
                    
                    f.render_widget(paragraph, layout[1]);
                }
                Screen::Help => {
                    // Draw help
                    let help_text = "
uCode1 TUI Help

Navigation:
  ↑/↓: Navigate lists
  Enter: Select item
  q: Quit current screen
  ?: Show this help

Screens:
  Notes List: View all notes
  Note View: Read note content
  Help: This screen

Mode indicators:
  NORMAL: Navigation mode
  EDIT: Input mode
";
                    
                    let paragraph = Paragraph::new(help_text)
                        .block(Block::default().borders(Borders::ALL).title("Help"))
                        .wrap(Wrap { trim: true });
                    
                    f.render_widget(paragraph, layout[1]);
                }
                Screen::Quit => {
                    // Draw quit
                    let paragraph = Paragraph::new("Goodbye!")
                        .block(Block::default().borders(Borders::ALL).title("Quit"))
                        .alignment(Alignment::Center);
                    
                    f.render_widget(paragraph, layout[1]);
                }
            }
            
            // Footer
            let footer = Paragraph::new("Press 'q' to quit, '?' for help")
                .block(Block::default().borders(Borders::ALL).title("Footer"))
                .alignment(Alignment::Center);
            f.render_widget(footer, layout[2]);
        })?;
        
        Ok(())
    }


}

impl Drop for Tui {
    fn drop(&mut self) {
        disable_raw_mode().unwrap();
        execute!(self.terminal.backend_mut(), LeaveAlternateScreen).unwrap();
    }
}

pub async fn run_tui(vault_path: &str) -> io::Result<()> {
    // Initialize TUI
    let mut tui = Tui::new()?;
    let mut state = AppState::new(vault_path);
    
    // Load initial data
    state.load_notes().await;
    
    // Main event loop
    while !tui.should_quit {
        tui.draw(&state)?;
        
        // Handle events
        if event::poll(std::time::Duration::from_millis(16))? {
            if let Event::Key(key) = event::read()? {
                if key.kind == KeyEventKind::Press {
                    match key.code {
                        KeyCode::Char('q') => {
                            tui.should_quit = true;
                        }
                        KeyCode::Char('?') => {
                            state.current_screen = Screen::Help;
                        }
                        KeyCode::Esc => {
                            state.current_screen = Screen::NotesList;
                        }
                        KeyCode::Enter => {
                            if state.current_screen == Screen::NotesList {
                                if let Some(selected) = state.notes.first() {
                                    let note_name = selected.clone();
                                    state.selected_note = Some(note_name.clone());
                                    state.load_note_content(&note_name).await;
                                    state.current_screen = Screen::NoteView;
                                }
                            }
                        }
                        _ => {}
                    }
                }
            }
        }
    }
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_app_state_initialization() {
        let state = AppState::new("/tmp/test");
        assert_eq!(state.current_screen, Screen::NotesList);
        assert_eq!(state.input_mode, InputMode::Normal);
    }

    #[test]
    fn test_screen_transitions() {
        let mut state = AppState::new("/tmp/test");
        state.current_screen = Screen::Help;
        assert_eq!(state.current_screen, Screen::Help);
    }
}