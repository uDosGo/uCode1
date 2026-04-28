#!/usr/bin/env python3
"""
Button Component for uCode1 UI

A flexible button component that can be rendered in various UI frameworks.
"""

from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Any
from enum import Enum


class ButtonVariant(Enum):
    """Button visual variants"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    LIGHT = "light"
    DARK = "dark"
    LINK = "link"


class ButtonSize(Enum):
    """Button size options"""
    SMALL = "sm"
    MEDIUM = "md"
    LARGE = "lg"


@dataclass
class Button:
    """Reusable button component"""
    
    # Button text/content
    text: str
    
    # Unique identifier
    id: Optional[str] = None
    
    # Visual variant
    variant: ButtonVariant = ButtonVariant.PRIMARY
    
    # Size
    size: ButtonSize = ButtonSize.MEDIUM
    
    # Click handler
    on_click: Optional[Callable[[], None]] = None
    
    # Additional HTML attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Icon (optional)
    icon: Optional[str] = None
    
    # Disabled state
    disabled: bool = False
    
    # Custom CSS classes
    css_classes: Optional[str] = None
    
    def __post_init__(self):
        """Initialize button with defaults"""
        if self.id is None:
            self.id = f"btn-{hash(self.text) % 10000}"
    
    def render_html(self) -> str:
        """Render button as HTML"""
        classes = [
            "btn",
            f"btn-{self.variant.value}",
            f"btn-{self.size.value}"
        ]
        
        if self.css_classes:
            classes.extend(self.css_classes.split())
        
        if self.disabled:
            classes.append("disabled")
        
        attributes = {
            "id": self.id,
            "class": " ".join(classes),
            **self.attributes
        }
        
        if self.disabled:
            attributes["disabled"] = "disabled"
        
        if self.on_click:
            attributes["onclick"] = f"{self.id}_click()"
        
        # Build attribute string
        attr_str = " ".join(f'{key}="{value}"' for key, value in attributes.items())
        
        # Button content
        content = self.text
        if self.icon:
            content = f'<i class="{self.icon}"></i> {content}'
        
        return f'<button {attr_str}>{content}</button>'
    
    def render_js(self) -> str:
        """Generate JavaScript for button click handler"""
        return f"""
        function {self.id}_click() {{
            // Button click handler
            console.log('Button {self.id} clicked');
            // Custom handler would go here
        }}
        """
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert button to dictionary"""
        return {
            "id": self.id,
            "text": self.text,
            "variant": self.variant.value,
            "size": self.size.value,
            "icon": self.icon,
            "disabled": self.disabled,
            "css_classes": self.css_classes,
            "attributes": self.attributes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Button':
        """Create button from dictionary"""
        return cls(
            text=data["text"],
            id=data.get("id"),
            variant=ButtonVariant(data.get("variant", "primary")),
            size=ButtonSize(data.get("size", "md")),
            icon=data.get("icon"),
            disabled=data.get("disabled", False),
            css_classes=data.get("css_classes"),
            attributes=data.get("attributes", {})
        )


# Example usage
if __name__ == "__main__":
    # Create a primary button
    primary_btn = Button(
        text="Click Me",
        variant=ButtonVariant.PRIMARY,
        size=ButtonSize.LARGE,
        icon="fas fa-rocket"
    )
    
    print("Button HTML:")
    print(primary_btn.render_html())
    
    print("\nButton Dict:")
    print(primary_btn.to_dict())
    
    # Create from dict
    btn_dict = {
        "text": "Submit",
        "variant": "success",
        "size": "md",
        "disabled": False
    }
    
    submit_btn = Button.from_dict(btn_dict)
    print("\nSubmit Button HTML:")
    print(submit_btn.render_html())