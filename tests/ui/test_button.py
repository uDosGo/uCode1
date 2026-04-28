#!/usr/bin/env python3
"""
Test cases for Button component
"""

import unittest
from ui.components.button import Button, ButtonVariant, ButtonSize


class TestButton(unittest.TestCase):
    """Test Button component functionality"""
    
    def test_button_creation(self):
        """Test basic button creation"""
        btn = Button(text="Click Me")
        self.assertEqual(btn.text, "Click Me")
        self.assertEqual(btn.variant, ButtonVariant.PRIMARY)
        self.assertEqual(btn.size, ButtonSize.MEDIUM)
        self.assertFalse(btn.disabled)
        self.assertIsNotNone(btn.id)
    
    def test_button_with_custom_id(self):
        """Test button with custom ID"""
        btn = Button(text="Test", id="custom-btn")
        self.assertEqual(btn.id, "custom-btn")
    
    def test_button_variants(self):
        """Test all button variants"""
        variants = [
            ButtonVariant.PRIMARY,
            ButtonVariant.SECONDARY,
            ButtonVariant.SUCCESS,
            ButtonVariant.DANGER,
            ButtonVariant.WARNING,
            ButtonVariant.INFO,
            ButtonVariant.LIGHT,
            ButtonVariant.DARK,
            ButtonVariant.LINK
        ]
        
        for variant in variants:
            btn = Button(text="Test", variant=variant)
            self.assertEqual(btn.variant, variant)
    
    def test_button_sizes(self):
        """Test all button sizes"""
        sizes = [ButtonSize.SMALL, ButtonSize.MEDIUM, ButtonSize.LARGE]
        
        for size in sizes:
            btn = Button(text="Test", size=size)
            self.assertEqual(btn.size, size)
    
    def test_button_with_icon(self):
        """Test button with icon"""
        btn = Button(text="Click", icon="fas fa-rocket")
        self.assertEqual(btn.icon, "fas fa-rocket")
    
    def test_button_disabled(self):
        """Test disabled button"""
        btn = Button(text="Disabled", disabled=True)
        self.assertTrue(btn.disabled)
    
    def test_button_html_rendering(self):
        """Test button HTML rendering"""
        btn = Button(text="Test Button", variant=ButtonVariant.SUCCESS, size=ButtonSize.LARGE)
        html = btn.render_html()
        
        self.assertIn('btn-success', html)
        self.assertIn('btn-lg', html)
        self.assertIn('Test Button', html)
        self.assertIn('button', html)
    
    def test_button_with_icon_html(self):
        """Test button with icon HTML rendering"""
        btn = Button(text="Click", icon="fas fa-star")
        html = btn.render_html()
        
        self.assertIn('fas fa-star', html)
        self.assertIn('Click', html)
    
    def test_button_disabled_html(self):
        """Test disabled button HTML rendering"""
        btn = Button(text="Disabled", disabled=True)
        html = btn.render_html()
        
        self.assertIn('disabled', html)
        self.assertIn('disabled', html)
    
    def test_button_to_dict(self):
        """Test button to_dict method"""
        btn = Button(
            text="Test",
            id="test-btn",
            variant=ButtonVariant.INFO,
            size=ButtonSize.SMALL,
            icon="fas fa-check",
            disabled=False,
            css_classes="custom-class"
        )
        
        btn_dict = btn.to_dict()
        
        self.assertEqual(btn_dict['text'], 'Test')
        self.assertEqual(btn_dict['id'], 'test-btn')
        self.assertEqual(btn_dict['variant'], 'info')
        self.assertEqual(btn_dict['size'], 'sm')
        self.assertEqual(btn_dict['icon'], 'fas fa-check')
        self.assertEqual(btn_dict['disabled'], False)
        self.assertEqual(btn_dict['css_classes'], 'custom-class')
    
    def test_button_from_dict(self):
        """Test button from_dict method"""
        btn_dict = {
            'text': 'From Dict',
            'id': 'dict-btn',
            'variant': 'warning',
            'size': 'lg',
            'icon': 'fas fa-exclamation',
            'disabled': True,
            'css_classes': 'another-class'
        }
        
        btn = Button.from_dict(btn_dict)
        
        self.assertEqual(btn.text, 'From Dict')
        self.assertEqual(btn.id, 'dict-btn')
        self.assertEqual(btn.variant, ButtonVariant.WARNING)
        self.assertEqual(btn.size, ButtonSize.LARGE)
        self.assertEqual(btn.icon, 'fas fa-exclamation')
        self.assertTrue(btn.disabled)
        self.assertEqual(btn.css_classes, 'another-class')
    
    def test_button_js_rendering(self):
        """Test button JavaScript rendering"""
        btn = Button(text="Click Me", id="test-btn")
        js = btn.render_js()
        
        self.assertIn('test-btn_click', js)
        self.assertIn('Button test-btn clicked', js)
    
    def test_button_custom_attributes(self):
        """Test button with custom attributes"""
        btn = Button(
            text="Custom",
            attributes={'data-test': 'value', 'aria-label': 'Custom Button'}
        )
        html = btn.render_html()
        
        self.assertIn('data-test="value"', html)
        self.assertIn('aria-label="Custom Button"', html)


if __name__ == '__main__':
    unittest.main()