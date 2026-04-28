import React, { useState, useEffect } from 'react';
import { Editor, rootCtx } from '@milkdown/core';
import { useEditor } from '@milkdown/react';
import { commonmark } from '@milkdown/preset-commonmark';
import { nord } from '@milkdown/theme-nord';

const MilkdownEditor = ({ initialContent = '', onChange }) => {
  const [content, setContent] = useState(initialContent);
  const editor = useEditor((root) => {
    return Editor.make()
      .config((ctx) => {
        ctx.set(rootCtx, root);
        ctx.set(commonmark.key, commonmark);
      })
      .use(nord);
  });

  useEffect(() => {
    if (editor) {
      const updateContent = async () => {
        await editor.action((ctx) => {
          const editor = ctx.get(rootCtx);
          editor.setMarkdown(content);
        });
      };
      updateContent();
    }
  }, [editor, content]);

  const handleChange = async (markdown) => {
    setContent(markdown);
    if (onChange) {
      onChange(markdown);
    }
  };

  if (!editor) return <div>Loading editor...</div>;

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div ref={editor.ref} />
    </div>
  );
};

export default MilkdownEditor;