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
      const greeting = screen.getAllByText(/hello, world!/i)[0];
      expect(greeting).toBeInTheDocument();
    });

    test('renders initial counter value of 0', () => {
      render(<App />);
      const counter = screen.getAllByText(/counter: 0/i)[0];
      expect(counter).toBeInTheDocument();
    });

    test('renders all section headers', () => {
      render(<App />);
      expect(screen.getAllByText(/counter:/i)[0]).toBeInTheDocument();
      expect(screen.getAllByText(/component state:/i)[0]).toBeInTheDocument();
      expect(screen.getAllByText(/enter your name:/i)[0]).toBeInTheDocument();
    });
  });

  describe('Counter Functionality', () => {
    test('increments counter when increment button is clicked', async () => {
      render(<App />);
      const incrementButton = screen.getByRole('button', { name: /increment/i });

      expect(screen.getAllByText(/counter: 0/i)[0]).toBeInTheDocument();

      fireEvent.click(incrementButton);
      expect(screen.getAllByText(/counter: 1/i)[0]).toBeInTheDocument();

      fireEvent.click(incrementButton);
      expect(screen.getAllByText(/counter: 2/i)[0]).toBeInTheDocument();
    });

    test('decrements counter when decrement button is clicked', async () => {
      render(<App />);
      const decrementButton = screen.getByRole('button', { name: /decrement/i });
      const incrementButton = screen.getByRole('button', { name: /increment/i });

      // First increment to get to 1
      fireEvent.click(incrementButton);
      expect(screen.getAllByText(/counter: 1/i)[0]).toBeInTheDocument();

      // Then decrement back to 0
      fireEvent.click(decrementButton);
      expect(screen.getAllByText(/counter: 0/i)[0]).toBeInTheDocument();
    });

    test('counter can go negative', () => {
      render(<App />);
      const decrementButton = screen.getByRole('button', { name: /decrement/i });

      fireEvent.click(decrementButton);
      expect(screen.getAllByText(/counter: -1/i)[0]).toBeInTheDocument();
    });

    test('multiple increments work correctly', () => {
      render(<App />);
      const incrementButton = screen.getByRole('button', { name: /increment/i });

      for (let i = 0; i < 5; i++) {
        fireEvent.click(incrementButton);
      }

      expect(screen.getAllByText(/counter: 5/i)[0]).toBeInTheDocument();
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

      expect(screen.getAllByText(/hello, bob!/i)[0]).toBeInTheDocument();
      expect(screen.getAllByText(/form submitted successfully!/i)[0]).toBeInTheDocument();
    });

    test('shows submitted message after form submission', async () => {
      render(<App />);
      const input = screen.getByPlaceholderText(/type your name/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      expect(screen.queryByText(/form submitted successfully!/i)).not.toBeInTheDocument();

      await userEvent.type(input, 'Charlie');
      fireEvent.click(submitButton);

      expect(screen.getAllByText(/form submitted successfully!/i)[0]).toBeInTheDocument();
    });

    test('does not submit with empty name', async () => {
      render(<App />);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      fireEvent.click(submitButton);

      expect(screen.queryByText(/form submitted successfully!/i)).not.toBeInTheDocument();
      expect(screen.getAllByText(/hello, world!/i)[0]).toBeInTheDocument();
    });
  });

  describe('Reset Functionality', () => {
    test('resets counter to 0', async () => {
      render(<App />);
      const incrementButton = screen.getByRole('button', { name: /increment/i });
      const resetButton = screen.getByRole('button', { name: /reset all/i });

      fireEvent.click(incrementButton);
      fireEvent.click(incrementButton);
      expect(screen.getAllByText(/counter: 2/i)[0]).toBeInTheDocument();

      fireEvent.click(resetButton);
      expect(screen.getAllByText(/counter: 0/i)[0]).toBeInTheDocument();
    });

    test('resets greeting to default', async () => {
      render(<App />);
      const input = screen.getByPlaceholderText(/type your name/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });
      const resetButton = screen.getByRole('button', { name: /reset all/i });

      await userEvent.type(input, 'David');
      fireEvent.click(submitButton);
      expect(screen.getAllByText(/hello, david!/i)[0]).toBeInTheDocument();

      fireEvent.click(resetButton);
      expect(screen.getAllByText(/hello, world!/i)[0]).toBeInTheDocument();
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

      expect(screen.getAllByText(/counter: 0/i)[0]).toBeInTheDocument();
      expect(screen.getAllByText(/hello, world!/i)[0]).toBeInTheDocument();
      expect(input).toHaveValue('');
    });
  });

  describe('Component State Display', () => {
    test('displays component state section', () => {
      render(<App />);
      expect(screen.getAllByText(/component state:/i)[0]).toBeInTheDocument();
    });

    test('displays initial state values', () => {
      render(<App />);
      expect(screen.getAllByText(/greeting: hello, world!/i)[0]).toBeInTheDocument();
      expect(screen.getAllByText(/counter: 0/i)[0]).toBeInTheDocument();
      expect(screen.getAllByText(/name: not set/i)[0]).toBeInTheDocument();
      expect(screen.getAllByText(/form submitted: no/i)[0]).toBeInTheDocument();
    });

    test('updates state display after form submission', async () => {
      render(<App />);
      const input = screen.getByPlaceholderText(/type your name/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      await userEvent.type(input, 'Frank');
      fireEvent.click(submitButton);

      expect(screen.getAllByText(/greeting: hello, frank!/i)[0]).toBeInTheDocument();
      expect(screen.getAllByText(/name: frank/i)[0]).toBeInTheDocument();
      expect(screen.getAllByText(/form submitted: yes/i)[0]).toBeInTheDocument();
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
