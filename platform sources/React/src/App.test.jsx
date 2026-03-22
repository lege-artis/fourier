import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import App from './App';

/**
 * React Component Tests
 *
 * Tests for the App component covering:
 * - Initial rendering
 * - State management with useState
 * - Event handling
 * - User interactions
 */

describe('App Component', () => {
  describe('Initial Rendering', () => {
    test('renders the main heading', () => {
      render(<App />);
      const heading = screen.getByRole('heading', { name: /react hello world test/i });
      expect(heading).toBeInTheDocument();
    });

    test('renders initial greeting', () => {
      render(<App />);
      const greeting = screen.getByText(/hello, world!/i);
      expect(greeting).toBeInTheDocument();
    });

    test('renders initial counter value of 0', () => {
      render(<App />);
      const counter = screen.getByText(/counter: 0/i);
      expect(counter).toBeInTheDocument();
    });

    test('renders all section headers', () => {
      render(<App />);
      expect(screen.getByText(/counter:/i)).toBeInTheDocument();
      expect(screen.getByText(/component state:/i)).toBeInTheDocument();
      expect(screen.getByText(/enter your name:/i)).toBeInTheDocument();
    });
  });

  describe('Counter Functionality', () => {
    test('increments counter when increment button is clicked', async () => {
      render(<App />);
      const incrementButton = screen.getByRole('button', { name: /increment/i });

      expect(screen.getByText(/counter: 0/i)).toBeInTheDocument();

      fireEvent.click(incrementButton);
      expect(screen.getByText(/counter: 1/i)).toBeInTheDocument();

      fireEvent.click(incrementButton);
      expect(screen.getByText(/counter: 2/i)).toBeInTheDocument();
    });

    test('decrements counter when decrement button is clicked', async () => {
      render(<App />);
      const decrementButton = screen.getByRole('button', { name: /decrement/i });
      const incrementButton = screen.getByRole('button', { name: /increment/i });

      // First increment to get to 1
      fireEvent.click(incrementButton);
      expect(screen.getByText(/counter: 1/i)).toBeInTheDocument();

      // Then decrement back to 0
      fireEvent.click(decrementButton);
      expect(screen.getByText(/counter: 0/i)).toBeInTheDocument();
    });

    test('counter can go negative', () => {
      render(<App />);
      const decrementButton = screen.getByRole('button', { name: /decrement/i });

      fireEvent.click(decrementButton);
      expect(screen.getByText(/counter: -1/i)).toBeInTheDocument();
    });

    test('multiple increments work correctly', () => {
      render(<App />);
      const incrementButton = screen.getByRole('button', { name: /increment/i });

      for (let i = 0; i < 5; i++) {
        fireEvent.click(incrementButton);
      }

      expect(screen.getByText(/counter: 5/i)).toBeInTheDocument();
    });
  });

  describe('Form Functionality', () => {
    test('renders form input field', () => {
      render(<App />);
      const input = screen.getByPlaceholderText(/type your name/i);
      expect(input).toBeInTheDocument();
      expect(input).toHaveValue('');
    });

    test('updates input value when user types', async () => {
      render(<App />);
      const input = screen.getByPlaceholderText(/type your name/i);

      await userEvent.type(input, 'Alice');

      expect(input).toHaveValue('Alice');
    });

    test('submits form and updates greeting', async () => {
      render(<App />);
      const input = screen.getByPlaceholderText(/type your name/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      await userEvent.type(input, 'Bob');
      fireEvent.click(submitButton);

      expect(screen.getByText(/hello, bob!/i)).toBeInTheDocument();
      expect(screen.getByText(/form submitted successfully!/i)).toBeInTheDocument();
    });

    test('shows submitted message after form submission', async () => {
      render(<App />);
      const input = screen.getByPlaceholderText(/type your name/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      expect(screen.queryByText(/form submitted successfully!/i)).not.toBeInTheDocument();

      await userEvent.type(input, 'Charlie');
      fireEvent.click(submitButton);

      expect(screen.getByText(/form submitted successfully!/i)).toBeInTheDocument();
    });

    test('does not submit with empty name', async () => {
      render(<App />);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      fireEvent.click(submitButton);

      expect(screen.queryByText(/form submitted successfully!/i)).not.toBeInTheDocument();
      expect(screen.getByText(/hello, world!/i)).toBeInTheDocument();
    });
  });

  describe('Reset Functionality', () => {
    test('resets counter to 0', async () => {
      render(<App />);
      const incrementButton = screen.getByRole('button', { name: /increment/i });
      const resetButton = screen.getByRole('button', { name: /reset all/i });

      fireEvent.click(incrementButton);
      fireEvent.click(incrementButton);
      expect(screen.getByText(/counter: 2/i)).toBeInTheDocument();

      fireEvent.click(resetButton);
      expect(screen.getByText(/counter: 0/i)).toBeInTheDocument();
    });

    test('resets greeting to default', async () => {
      render(<App />);
      const input = screen.getByPlaceholderText(/type your name/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });
      const resetButton = screen.getByRole('button', { name: /reset all/i });

      await userEvent.type(input, 'David');
      fireEvent.click(submitButton);
      expect(screen.getByText(/hello, david!/i)).toBeInTheDocument();

      fireEvent.click(resetButton);
      expect(screen.getByText(/hello, world!/i)).toBeInTheDocument();
    });

    test('resets all state values together', async () => {
      render(<App />);
      const input = screen.getByPlaceholderText(/type your name/i);
      const incrementButton = screen.getByRole('button', { name: /increment/i });
      const submitButton = screen.getByRole('button', { name: /submit/i });
      const resetButton = screen.getByRole('button', { name: /reset all/i });

      await userEvent.type(input, 'Eve');
      fireEvent.click(incrementButton);
      fireEvent.click(incrementButton);
      fireEvent.click(submitButton);

      fireEvent.click(resetButton);

      expect(screen.getByText(/counter: 0/i)).toBeInTheDocument();
      expect(screen.getByText(/hello, world!/i)).toBeInTheDocument();
      expect(input).toHaveValue('');
    });
  });

  describe('Component State Display', () => {
    test('displays component state section', () => {
      render(<App />);
      expect(screen.getByText(/component state:/i)).toBeInTheDocument();
    });

    test('displays initial state values', () => {
      render(<App />);
      expect(screen.getByText(/greeting: hello, world!/i)).toBeInTheDocument();
      expect(screen.getByText(/counter: 0/i)).toBeInTheDocument();
      expect(screen.getByText(/name: not set/i)).toBeInTheDocument();
      expect(screen.getByText(/form submitted: no/i)).toBeInTheDocument();
    });

    test('updates state display after form submission', async () => {
      render(<App />);
      const input = screen.getByPlaceholderText(/type your name/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      await userEvent.type(input, 'Frank');
      fireEvent.click(submitButton);

      expect(screen.getByText(/greeting: hello, frank!/i)).toBeInTheDocument();
      expect(screen.getByText(/name: frank/i)).toBeInTheDocument();
      expect(screen.getByText(/form submitted: yes/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('all buttons are keyboard accessible', () => {
      render(<App />);
      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        expect(button).toBeInTheDocument();
      });
    });

    test('form input has associated label', () => {
      render(<App />);
      const label = screen.getByLabelText(/enter your name:/i);
      expect(label).toBeInTheDocument();
    });
  });
});
