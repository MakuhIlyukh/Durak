import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  // StrictMode call hooks twice (this is for debugging)
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
