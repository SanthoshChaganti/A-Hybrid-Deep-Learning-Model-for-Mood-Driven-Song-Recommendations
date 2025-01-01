// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import './App.css';

import About from './components/About';
import Features from './components/Features';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="navbar">
          <Link to="/" className="navbar-title">Moodify</Link>
          <nav className="navbar-links">
            <Link to="/about">About</Link>
            <Link to="/features">Features</Link>
          </nav>
        </header>

        <main>
          <Routes>
            <Route path="/" element={<div className="home">Welcome to Moodify!</div>} />
            <Route path="/about" element={<About />} />
            <Route path="/features" element={<Features />} />
          </Routes>
        </main>

        <footer className="footer">
          © 2024 Moodify. All rights reserved.
        </footer>
      </div>
    </Router>
  );
}

export default App;
