"""
Markdown Processing Module

Provides markdown formatting, rendering, and conversion utilities.
Uses Python's built-in html module or external markdown library if available.
"""

import re
import html
from typing import Optional, Callable, Dict, List, Any
from .exceptions import MarkdownError


def format_markdown(md_text: str, **kwargs) -> str:
    """Format markdown text with simple processing.
    
    Handles basic markdown: headers, bold, italic, lists, links.
    
    Args:
        md_text: Markdown text to format
        **kwargs: Additional formatting options
    
    Returns:
        Formatted text (still markdown, but potentially processed)
    """
    # This is a passthrough - use render_markdown for actual rendering
    return md_text


def render_markdown(md_text: str, use_html: bool = True, 
                    escape_html: bool = True) -> str:
    """Render markdown to HTML.
    
    Priority:
    1. Use markdown library if available
    2. Use built-in simple markdown parser
    
    Args:
        md_text: Markdown text to render
        use_html: If True, render to HTML; otherwise plain text
        escape_html: If True, escape HTML special characters
    
    Returns:
        Rendered HTML or plain text
    """
    import sys
    
    # Try to use markdown library if available
    try:
        import markdown as md_lib
        html_output = md_lib.markdown(md_text)
        return html_output if use_html else strip_markdown(html_output)
    except ImportError:
        pass
    
    # Fall back to built-in simple markdown parser
    return _simple_markdown_to_html(md_text)


def _simple_markdown_to_html(md_text: str) -> str:
    """Simple markdown to HTML parser.
    
    Handles: headers, bold, italic, lists, links, images, code.
    """
    lines = md_text.split('\n')
    html_lines = []
    in_list = False
    in_code_block = False
    in_blockquote = False
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines (but preserve in code blocks)
        if not stripped and not in_code_block:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if in_blockquote:
                html_lines.append('</blockquote>')
                in_blockquote = False
            html_lines.append('<p><br/></p>') if html_lines and html_lines[-1] != '<p><br/></p>' else None
            continue
        
        # Code blocks (```)
        if stripped.startswith('```'):
            if in_code_block:
                html_lines.append('</code></pre>')
                in_code_block = False
                continue
            else:
                lang = stripped[3:].strip()
                html_lines.append(f'<pre><code class="language-{lang}">')
                in_code_block = True
                continue
        
        if in_code_block:
            html_lines.append(html.escape(stripped))
            continue
        
        # Headers
        header_match = re.match(r'^(#{1,6})\s+(.*?)\s*$', stripped)
        if header_match:
            level = len(header_match.group(1))
            header_text = _process_inline_markdown(header_match.group(2))
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if in_blockquote:
                html_lines.append('</blockquote>')
                in_blockquote = False
            html_lines.append(f'<h{level}>{header_text}</h{level}>')
            continue
        
        # Blockquotes
        if stripped.startswith('>'):
            if not in_blockquote:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append('<blockquote>')
                in_blockquote = True
            content = stripped[1:].strip()
            html_lines.append(f'<p>{_process_inline_markdown(content)}</p>')
            continue
        
        if in_blockquote:
            html_lines.append('</blockquote>')
            in_blockquote = False
        
        # Horizontal rule
        if stripped in ('---', '***', '___'):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if in_blockquote:
                html_lines.append('</blockquote>')
                in_blockquote = False
            html_lines.append('<hr/>')
            continue
        
        # Lists
        ul_match = re.match(r'^(\s*)[\*\-+]\s+(.*)', stripped)
        ol_match = re.match(r'^(\s*)\d+\.\s+(.*)', stripped)
        
        if ul_match:
            if not in_list:
                if in_blockquote:
                    html_lines.append('</blockquote>')
                    in_blockquote = False
                html_lines.append('<ul>')
                in_list = True
            content = _process_inline_markdown(ul_match.group(2))
            html_lines.append(f'<li>{content}</li>')
            continue
        
        if ol_match:
            if not in_list:
                if in_blockquote:
                    html_lines.append('</blockquote>')
                    in_blockquote = False
                # For simplicity, we'll use UL for all lists in basic implementation
                html_lines.append('<ul>')
                in_list = True
            content = _process_inline_markdown(ol_match.group(2))
            html_lines.append(f'<li>{content}</li>')
            continue
        
        if in_list:
            html_lines.append('</ul>')
            in_list = False
        
        # Check for code (tab-indented old style)
        if stripped.startswith('    ') or stripped.startswith('\t'):
            if not in_code_block:
                html_lines.append('<pre><code>')
                in_code_block = True
            html_lines.append(html.escape(stripped))
            continue
        
        if in_code_block:
            html_lines.append('</code></pre>')
            in_code_block = False
        
        # Image
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', stripped)
        if img_match:
            alt = img_match.group(1)
            src = img_match.group(2)
            html_lines.append(f'<img src="{src}" alt="{alt}"/>')
            continue
        
        # Link
        link_match = re.match(r'\[(.*?)\]\((.*?)\)', stripped)
        if link_match and not img_match:  # Already handled images above
            text = link_match.group(1)
            url = link_match.group(2)
            html_lines.append(f'<a href="{url}">{text}</a>')
            continue
        
        # If we get here, it's a paragraph or the line content
        if stripped:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if in_blockquote:
                html_lines.append('</blockquote>')
                in_blockquote = False
            html_lines.append(f'<p>{_process_inline_markdown(stripped)}</p>')
    
    # Close any open tags
    if in_code_block:
        html_lines.append('</code></pre>')
    if in_list:
        html_lines.append('</ul>')
    if in_blockquote:
        html_lines.append('</blockquote>')
    
    return '\n'.join(html_lines)


def _process_inline_markdown(text: str) -> str:
    """Process inline markdown (bold, italic, code, links)."""
    # Escape HTML first
    result = html.escape(text)
    
    # Strike-through: ~~text~~
    result = re.sub(r'~~(.*?)~~', r'<s>\1</s>', result)
    
    # Bold: **text** or __text__
    result = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', result)
    result = re.sub(r'__(.*?)__', r'<strong>\1</strong>', result)
    
    # Italic: *text* or _text_
    result = re.sub(r'\*(.*?)\*', r'<em>\1</em>', result)
    result = re.sub(r'(?<!\w)_(.*?)_(?!\w)', r'<em>\1</em>', result)
    
    # Inline code: `code`
    result = re.sub(r'`(.*?)`', r'<code>\1</code>', result)
    
    return result


def html_to_markdown(html_text: str) -> str:
    """Convert HTML to markdown (limited support).
    
    Args:
        html_text: HTML text to convert
    
    Returns:
        Markdown text
    """
    # Simple HTML to markdown conversion
    md = html_text
    
    # Headers
    md = re.sub(r'<h(\d)>(.*?)</h\1>', lambda m: '#' * int(m.group(1)) + ' ' + m.group(2), md)
    
    # Bold/Strong
    md = re.sub(r'<(strong|b)>(.*?)</\1>', r'**\2**', md)
    
    # Italic/Emphasis
    md = re.sub(r'<(em|i)>(.*?)</\1>', r'*\2*', md)
    
    # Code
    md = re.sub(r'<(code|tt)>(.*?)</\1>', r'`\2`', md)
    
    # Strike-through
    md = re.sub(r'<s>(.*?)</s>', r'~~\1~~', md)
    
    # Links
    md = re.sub(r'<a href="(.*?)">(.*?)</a>', r'[\2](\1)', md)
    
    # Images
    md = re.sub(r'<img src="(.*?)" alt="(.*?)"', r'![\2](\1)', md)
    
    # Paragraphs (remove <p> tags but keep line breaks)
    md = re.sub(r'<p>(.*?)</p>', r'\1', md)
    
    # Line breaks
    md = re.sub(r'<br\s*/?>', '\n', md)
    
    # Remove other tags
    md = re.sub(r'<[^>]+>', '', md)
    
    return md


def markdown_to_html(md_text: str) -> str:
    """Alias for render_markdown."""
    return render_markdown(md_text)


def strip_markdown(md_text: str) -> str:
    """Remove markdown formatting, returning plain text.
    
    Args:
        md_text: Markdown text
    
    Returns:
        Plain text with markdown removed
    """
    result = md_text
    
    # Headers
    result = re.sub(r'^(#{1,6})\s+', '', result, flags=re.MULTILINE)
    
    # Bold/Italic
    result = re.sub(r'[\*_]{1,2}(.*?)[\*_]{1,2}', r'\1', result)
    
    # Code blocks
    result = re.sub(r'```.*?\n(.*?)```', r'\1', result, flags=re.DOTALL)
    result = re.sub(r'`(.*?)`', r'\1', result)
    
    # Links
    result = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', result)
    
    # Images
    result = re.sub(r'!\[(.*?)\]\(.*?\)', r'\1', result)
    
    # Horizontal rules
    result = re.sub(r'^[\-\*_]{3,}\s*$', '', result, flags=re.MULTILINE)
    
    # HTML entities
    result = html.unescape(result)
    
    return result


class MarkdownFormatter:
    """Advanced markdown formatter."""
    
    def __init__(self, extensions: Optional[List[str]] = None):
        """Initialize formatter.
        
        Args:
            extensions: List of markdown extensions to enable
        """
        self.extensions = extensions or []
    
    def format(self, md_text: str) -> str:
        """Format markdown text.
        
        Args:
            md_text: Markdown to format
        
        Returns:
            Formatted markdown
        """
        # For now, just return the text
        # With proper markdown library, this would apply formatting
        return md_text
    
    def render(self, md_text: str) -> str:
        """Render markdown to HTML.
        
        Args:
            md_text: Markdown to render
        
        Returns:
            HTML output
        """
        return render_markdown(md_text)


class MarkdownRenderer:
    """Render markdown with customization options."""
    
    def __init__(self, **options):
        """Initialize renderer.
        
        Args:
            **options: Rendering options
        """
        self.options = options
    
    def render(self, md_text: str) -> str:
        """Render markdown to HTML.
        
        Args:
            md_text: Markdown to render
        
        Returns:
            HTML output
        """
        return render_markdown(md_text, **self.options)
    
    def render_to_plaintext(self, md_text: str) -> str:
        """Render markdown to plain text.
        
        Args:
            md_text: Markdown to convert
        
        Returns:
            Plain text
        """
        return strip_markdown(md_text)
