#!/usr/bin/env python3
"""
Test cases for Card component
"""

import unittest
from ui.components.card import Card


class TestCard(unittest.TestCase):
    """Test Card component functionality"""
    
    def test_simple_card_creation(self):
        """Test basic card creation"""
        card = Card(title="Test Card", content="<p>Test content</p>")
        self.assertEqual(card.title, "Test Card")
        self.assertEqual(card.content, "<p>Test content</p>")
        self.assertIsNotNone(card.id)
    
    def test_card_with_custom_id(self):
        """Test card with custom ID"""
        card = Card(title="Custom", id="custom-card")
        self.assertEqual(card.id, "custom-card")
    
    def test_card_with_footer(self):
        """Test card with footer"""
        card = Card(title="Test", content="Content", footer="Footer text")
        self.assertEqual(card.footer, "Footer text")
    
    def test_card_with_image(self):
        """Test card with image"""
        card = Card(
            title="Image Card",
            content="Content",
            image_url="https://example.com/image.jpg",
            image_position="top"
        )
        self.assertEqual(card.image_url, "https://example.com/image.jpg")
        self.assertEqual(card.image_position, "top")
    
    def test_card_html_rendering(self):
        """Test card HTML rendering"""
        card = Card(title="Test", content="<p>Test content</p>")
        html = card.render_html()
        
        self.assertIn('Test', html)
        self.assertIn('Test content', html)
        self.assertIn('card', html)
    
    def test_card_with_actions(self):
        """Test card with header and footer actions"""
        card = Card(
            title="Action Card",
            content="<p>Content</p>",
            header_actions=[
                {"text": "Save", "onclick": "save()", "class": "btn btn-primary"}
            ],
            footer_actions=[
                {"text": "Close", "onclick": "close()", "class": "btn btn-secondary"}
            ]
        )
        html = card.render_html()
        
        self.assertIn('Save', html)
        self.assertIn('Close', html)
        self.assertIn('btn-primary', html)
        self.assertIn('btn-secondary', html)
    
    def test_card_with_image_html(self):
        """Test card with image HTML rendering"""
        card = Card(
            title="Image Card",
            content="<p>Content</p>",
            image_url="https://example.com/image.jpg",
            image_position="top"
        )
        html = card.render_html()
        
        self.assertIn('image.jpg', html)
        self.assertIn('card-img-top', html)
    
    def test_card_collapsible(self):
        """Test collapsible card"""
        card = Card(title="Collapsible", content="Content", collapsible=True)
        self.assertTrue(card.collapsible)
        
        html = card.render_html()
        self.assertIn('collapsible', html)
    
    def test_card_to_dict(self):
        """Test card to_dict method"""
        card = Card(
            title="Test",
            content="Content",
            id="test-card",
            footer="Footer",
            image_url="image.jpg",
            image_position="bottom",
            collapsible=True,
            collapsed=False
        )
        
        card_dict = card.to_dict()
        
        self.assertEqual(card_dict['title'], 'Test')
        self.assertEqual(card_dict['content'], 'Content')
        self.assertEqual(card_dict['id'], 'test-card')
        self.assertEqual(card_dict['footer'], 'Footer')
        self.assertEqual(card_dict['image_url'], 'image.jpg')
        self.assertEqual(card_dict['image_position'], 'bottom')
        self.assertTrue(card_dict['collapsible'])
        self.assertFalse(card_dict['collapsed'])
    
    def test_card_from_dict(self):
        """Test card from_dict method"""
        card_dict = {
            'title': 'From Dict',
            'content': '<p>Dict content</p>',
            'id': 'dict-card',
            'footer': 'Dict footer',
            'image_url': 'dict.jpg',
            'image_position': 'top',
            'collapsible': True,
            'collapsed': True
        }
        
        card = Card.from_dict(card_dict)
        
        self.assertEqual(card.title, 'From Dict')
        self.assertEqual(card.content, '<p>Dict content</p>')
        self.assertEqual(card.id, 'dict-card')
        self.assertEqual(card.footer, 'Dict footer')
        self.assertEqual(card.image_url, 'dict.jpg')
        self.assertEqual(card.image_position, 'top')
        self.assertTrue(card.collapsible)
        self.assertTrue(card.collapsed)


if __name__ == '__main__':
    unittest.main()