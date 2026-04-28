#!/usr/bin/env python3
"""
Card Component for uCode1 UI

A flexible card component for displaying content in a structured way.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class Card:
    """Reusable card component"""
    
    # Card title
    title: Optional[str] = None
    
    # Card content (HTML or text)
    content: str = ""
    
    # Unique identifier
    id: Optional[str] = None
    
    # Footer content
    footer: Optional[str] = None
    
    # Header actions (buttons, links, etc.)
    header_actions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Footer actions
    footer_actions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Custom CSS classes
    css_classes: Optional[str] = None
    
    # Card image URL
    image_url: Optional[str] = None
    
    # Card image position (top, bottom, left, right)
    image_position: str = "top"
    
    # Collapsible state
    collapsible: bool = False
    
    # Initially collapsed
    collapsed: bool = False
    
    def __post_init__(self):
        """Initialize card with defaults"""
        if self.id is None and self.title:
            self.id = f"card-{hash(self.title) % 10000}"
        elif self.id is None:
            self.id = f"card-{hash(self.content) % 10000}"
    
    def render_html(self) -> str:
        """Render card as HTML"""
        classes = ["card"]
        
        if self.css_classes:
            classes.extend(self.css_classes.split())
        
        if self.collapsible:
            classes.append("collapsible")
        
        if self.collapsed:
            classes.append("collapsed")
        
        # Card header
        header_html = ""
        if self.title or self.header_actions:
            header_html = f"""
            <div class="card-header">
                {f'<h3>{self.title}</h3>' if self.title else ''}
                {''.join(self._render_actions(self.header_actions))}
            </div>
            """
        
        # Card image
        image_html = ""
        if self.image_url:
            if self.image_position in ["top", "bottom"]:
                image_html = f'<img src="{self.image_url}" class="card-img-{self.image_position}" alt="Card image">'
            else:
                image_html = f'<img src="{self.image_url}" class="card-img-{self.image_position}" alt="Card image">'
        
        # Card body
        body_html = f"""
        <div class="card-body">
            {image_html if self.image_position == 'top' else ''}
            <div class="card-content">{self.content}</div>
            {image_html if self.image_position == 'bottom' else ''}
        </div>
        """
        
        # Card footer
        footer_html = ""
        if self.footer or self.footer_actions:
            footer_html = f"""
            <div class="card-footer">
                {f'<div class="card-footer-text">{self.footer}</div>' if self.footer else ''}
                {''.join(self._render_actions(self.footer_actions))}
            </div>
            """
        
        # Combine all parts
        return f"""
        <div class="{' '.join(classes)}" id="{self.id}">
            {header_html}
            {body_html}
            {footer_html}
        </div>
        """
    
    def _render_actions(self, actions: List[Dict[str, Any]]) -> str:
        """Render action buttons/links"""
        if not actions:
            return ""
        
        action_html = []
        for action in actions:
            tag = action.get("tag", "button")
            text = action.get("text", "Action")
            onclick = action.get("onclick", "")
            href = action.get("href", "#")
            css_class = action.get("class", "btn btn-primary")
            
            if tag == "button":
                action_html.append(f'<button class="{css_class}" onclick="{onclick}">{text}</button>')
            else:
                action_html.append(f'<a href="{href}" class="{css_class}">{text}</a>')
        
        return '\n'.join(action_html)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert card to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "footer": self.footer,
            "header_actions": self.header_actions,
            "footer_actions": self.footer_actions,
            "css_classes": self.css_classes,
            "image_url": self.image_url,
            "image_position": self.image_position,
            "collapsible": self.collapsible,
            "collapsed": self.collapsed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Card':
        """Create card from dictionary"""
        return cls(
            title=data.get("title"),
            content=data.get("content", ""),
            id=data.get("id"),
            footer=data.get("footer"),
            header_actions=data.get("header_actions", []),
            footer_actions=data.get("footer_actions", []),
            css_classes=data.get("css_classes"),
            image_url=data.get("image_url"),
            image_position=data.get("image_position", "top"),
            collapsible=data.get("collapsible", False),
            collapsed=data.get("collapsed", False)
        )


# Example usage
if __name__ == "__main__":
    # Create a simple card
    simple_card = Card(
        title="Welcome",
        content="<p>This is a simple card component.</p><p>It supports HTML content.</p>",
        footer="Card footer text"
    )
    
    print("Simple Card HTML:")
    print(simple_card.render_html())
    
    # Create a card with actions
    action_card = Card(
        title="Action Card",
        content="<p>This card has action buttons.</p>",
        header_actions=[
            {"tag": "button", "text": "Save", "onclick": "saveCard()", "class": "btn btn-success"},
            {"tag": "button", "text": "Delete", "onclick": "deleteCard()", "class": "btn btn-danger"}
        ],
        footer_actions=[
            {"tag": "a", "text": "Learn More", "href": "https://example.com", "class": "btn btn-info"}
        ]
    )
    
    print("\nAction Card HTML:")
    print(action_card.render_html())
    
    # Create a card with image
    image_card = Card(
        title="Image Card",
        content="<p>This card has an image at the top.</p>",
        image_url="https://via.placeholder.com/300x200",
        image_position="top"
    )
    
    print("\nImage Card HTML:")
    print(image_card.render_html())