import React from 'react';
import '../About.css';   // Make sure to import the new CSS for styling.

function About() {
  return (
    <div className="about">
      <h1 className="about-title">Santhosh's Music Recommendation System</h1>
      <p className="about-description">
        Welcome to Santhosh's Music Recommendation System! This platform analyzes your mood through an image and generates a personalized Spotify playlist. Whether you're feeling happy, sad, or anything in between, Moodify helps you find the perfect soundtrack.
      </p>

      <h2 className="about-section-title">Features</h2>
      <ul className="about-list">
        <li><strong>Image Mood Analysis:</strong> Upload an image to analyze your mood.</li>
        <li><strong>Spotify Playlist Generation:</strong> Get a playlist tailored to your mood.</li>
        <li><strong>User-Friendly Interface:</strong> Easy to navigate and use.</li>
        <li><strong>Responsive Design:</strong> Works seamlessly on all devices.</li>
      </ul>

      <h2 className="about-section-title">About the Developer</h2>
      <p className="about-text">
        Hello there! I'm Santhosh Chaganti, a passionate developer dedicated to creating innovative and user-friendly solutions. Here's a bit about me:
      </p>
      <ul className="about-list">
        <li><strong>Contact:</strong> +91 9182757161</li>
        <li><strong>Email:</strong> santhoshchaganti897@gmail.com</li>
        <li><strong>LinkedIn:</strong> <a href="https://linkedin.com/in/your-profile" target="_blank" rel="noopener noreferrer" className="about-link">LinkedIn Profile</a></li>
        <li><strong>GitHub:</strong> <a href="https://github.com/your-profile" target="_blank" rel="noopener noreferrer" className="about-link">GitHub Profile</a></li>
      </ul>
      <p className="about-text">
        As a developer, my goal is to deliver high-quality software that meets your needs. Whether you have questions, suggestions, or feedback, feel free to reach out. I'm here to assist you on your journey with our products.
      </p>
    </div>
  );
}

export default About;
