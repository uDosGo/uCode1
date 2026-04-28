#!/usr/bin/env python3
"""
Modal Component for uCode1 UI

A flexible modal dialog component for displaying content in an overlay.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable


@dataclass
class Modal:
    """Reusable modal component"""
    
    # Modal title
    title: str = "Modal Title"
    
    # Modal content (HTML or text)
    content: str = ""
    
    # Unique identifier
    id: Optional[str] = None
    
    # Modal size (sm, md, lg, xl)
    size: str = "md"
    
    # Show modal state
    is_open: bool = False
    
    # Close on outside click
    close_on_outside_click: bool = True
    
    # Close on escape key
    close_on_escape: bool = True
    
    # Footer buttons
    footer_buttons: List[Dict[str, Any]] = field(default_factory=list)
    
    # Custom CSS classes
    css_classes: Optional[str] = None
    
    # Callback for when modal is closed
    on_close: Optional[Callable[[], None]] = None
    
    def __post_init__(self):
        """Initialize modal with defaults"""
        if self.id is None:
            self.id = f"modal-{hash(self.title) % 10000}"
    
    def render_html(self) -> str:
        """Render modal as HTML"""
        classes = ["modal", f"modal-{self.size}"]
        
        if self.css_classes:
            classes.extend(self.css_classes.split())
        
        if self.is_open:
            classes.append("open")
        
        # Modal overlay
        overlay_attrs = {
            "class": "modal-overlay",
            "onclick": f"closeModal('{self.id}')" if self.close_on_outside_click else ""
        }
        
        overlay_attrs_str = " ".join(f'{key}="{value}"' for key, value in overlay_attrs.items() if value)
        
        # Modal content
        modal_attrs = {
            "id": self.id,
            "class": "modal-content " + " ".join(classes)
        }
        
        modal_attrs_str = " ".join(f'{key}="{value}"' for key, value in modal_attrs.items())
        
        # Header
        header_html = f"""
        <div class="modal-header">
            <h3>{self.title}</h3>
            <button class="modal-close" onclick="closeModal('{self.id}')">×</button>
        </div>
        """
        
        # Body
        body_html = f"""
        <div class="modal-body">
            {self.content}
        </div>
        """
        
        # Footer
        footer_html = ""
        if self.footer_buttons:
            buttons = []
            for button in self.footer_buttons:
                text = button.get("text", "Button")
                onclick = button.get("onclick", "")
                css_class = button.get("class", "btn btn-primary")
                buttons.append(f'<button class="{css_class}" onclick="{onclick}">{text}</button>')
            
            footer_html = f"""
            <div class="modal-footer">
                {' '.join(buttons)}
            </div>
            """
        
        # Combine all parts
        return f"""
        <div {overlay_attrs_str}>
            <div {modal_attrs_str}>
                {header_html}
                {body_html}
                {footer_html}
            </div>
        </div>
        """
    
    def render_js(self) -> str:
        """Generate JavaScript for modal functionality"""
        return f"""
        function closeModal(modalId) {{
            const modal = document.getElementById(modalId);
            if (modal) {{
                modal.classList.remove('open');
                document.querySelector('.modal-overlay').style.display = 'none';
                {f"if (typeof {self.id}_onClose === 'function') {{ {self.id}_onClose(); }}" if self.on_close else ""}
            }}
        }}
        
        function openModal(modalId) {{
            const modal = document.getElementById(modalId);
            if (modal) {{
                modal.classList.add('open');
                document.querySelector('.modal-overlay').style.display = 'block';
            }}
        }}
        
        // Close on escape key
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape' && {str(self.close_on_escape).lower()}) {{
                closeModal('{self.id}');
            }}
        }});
        """
    
    def open(self):
        """Open the modal"""
        self.is_open = True
    
    def close(self):
        """Close the modal"""
        self.is_open = False
        if self.on_close:
            self.on_close()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert modal to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "size": self.size,
            "is_open": self.is_open,
            "close_on_outside_click": self.close_on_outside_click,
            "close_on_escape": self.close_on_escape,
            "footer_buttons": self.footer_buttons,
            "css_classes": self.css_classes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Modal':
        """Create modal from dictionary"""
        return cls(
            title=data.get("title", "Modal Title"),
            content=data.get("content", ""),
            id=data.get("id"),
            size=data.get("size", "md"),
            is_open=data.get("is_open", False),
            close_on_outside_click=data.get("close_on_outside_click", True),
            close_on_escape=data.get("close_on_escape", True),
            footer_buttons=data.get("footer_buttons", []),
            css_classes=data.get("css_classes")
        )


# Example usage
if __name__ == "__main__":
    # Create a simple modal
    simple_modal = Modal(
        title="Welcome",
        content="<p>This is a simple modal dialog.</p><p>It supports HTML content.</p>",
        footer_buttons=[
            {"text": "Close", "onclick": "closeModal('modal-1234')", "class": "btn btn-secondary"},
            {"text": "Save", "onclick": "saveData()", "class": "btn btn-primary"}
        ]
    )
    
    print("Simple Modal HTML:")
    print(simple_modal.render_html())
    
    print("\nSimple Modal JS:")
    print(simple_modal.render_js())
    
    # Create a modal from dict
    modal_dict = {
        "title": "Confirm Action",
        "content": "<p>Are you sure you want to proceed?</p>",
        "size": "sm",
        "footer_buttons": [
            {"text": "Cancel", "onclick": "closeModal('confirm-modal')", "class": "btn btn-secondary"},
            {"text": "Confirm", "onclick": "confirmAction()", "class": "btn btn-danger"}
        ]
    }
    
    confirm_modal = Modal.from_dict(modal_dict)
    print("\nConfirm Modal HTML:")
    print(confirm_modal.render_html())