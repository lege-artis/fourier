import React, { useState } from 'react';
import './App.css';

/**
 * React Hello World Test Component
 *
 * A simple React application that demonstrates:
 * - Functional components
 * - useState hook
 * - Event handling
 * - Conditional rendering
 */
function App() {
  const [count, setCount] = useState(0);
  const [greeting, setGreeting] = useState('Hello, World!');
  const [name, setName] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleIncrement = () => {
    setCount(count + 1);
  };

  const handleDecrement = () => {
    setCount(count - 1);
  };

  const handleGreetingChange = (event) => {
    setGreeting(event.target.value);
  };

  const handleNameChange = (event) => {
    setName(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (name.trim()) {
      setGreeting(`Hello, ${name}!`);
      setSubmitted(true);
    }
  };

  const handleReset = () => {
    setName('');
    setGreeting('Hello, World!');
    setSubmitted(false);
    setCount(0);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>React Hello World Test</h1>

        <section className="greeting-section">
          <h2>{greeting}</h2>
          <p>From React Component</p>
        </section>

        <section className="counter-section">
          <h3>Counter: {count}</h3>
          <div className="button-group">
            <button onClick={handleDecrement}>- Decrement</button>
            <button onClick={handleIncrement}>+ Increment</button>
          </div>
        </section>

        <section className="form-section">
          <form onSubmit={handleSubmit}>
            <label htmlFor="nameInput">Enter your name: </label>
            <input
              id="nameInput"
              type="text"
              value={name}
              onChange={handleNameChange}
              placeholder="Type your name"
            />
            <button type="submit">Submit</button>
          </form>

          {submitted && (
            <div className="submitted-message">
              <p>Form submitted successfully!</p>
              <p>Greeting: {greeting}</p>
            </div>
          )}
        </section>

        <section className="info-section">
          <h3>Component State:</h3>
          <ul>
            <li>Greeting: {greeting}</li>
            <li>Counter: {count}</li>
            <li>Name: {name || 'Not set'}</li>
            <li>Form Submitted: {submitted ? 'Yes' : 'No'}</li>
          </ul>
        </section>

        <div className="reset-button">
          <button onClick={handleReset}>Reset All</button>
        </div>

        <footer className="footer">
          <p>React version: {React.version}</p>
        </footer>
      </header>
    </div>
  );
}

export default App;
