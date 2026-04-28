import React from 'react';
import ReactDOM from 'react-dom/client';
import MilkdownEditor from './MilkdownEditor';

const App = () => {
  const [content, setContent] = React.useState('# Hello uDos!\n\nThis is a **Markdown** editor.');

  const handleChange = (markdown) => {
    setContent(markdown);
    console.log('Content updated:', markdown);
    // Here you would typically save to your backend
    // e.g., saveToBackend(markdown);
  };

  return (
    <div style={{ width: '100%', height: '100vh', padding: '20px', boxSizing: 'border-box' }}>
      <h1 style={{ color: '#fff', marginBottom: '20px' }}>uDos Markdown Editor</h1>
      <div style={{ height: 'calc(100% - 60px)', border: '1px solid #444', borderRadius: '4px' }}>
        <MilkdownEditor initialContent={content} onChange={handleChange} />
      </div>
      <div style={{ marginTop: '20px', padding: '10px', background: '#222', borderRadius: '4px' }}>
        <h3 style={{ color: '#fff', margin: '0 0 10px 0' }}>Preview:</h3>
        <pre style={{ color: '#ccc', whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
          {content}
        </pre>
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);