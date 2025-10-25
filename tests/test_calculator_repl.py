import unittest
from unittest.mock import patch, MagicMock, ANY
from decimal import Decimal
import io
import logging

# Adjust imports based on your actual project structure
from app.calculator_repl import calculator_repl
from app.exceptions import ValidationError, OperationError
# Import observer classes for mocking
from app.history import AutoSaveObserver, LoggingObserver 

# Mock classes to simulate operations without complex setup
class MockOperation:
    """A minimal mock operation class for factory use."""
    def __str__(self):
        return "MockOperation"
    
    # Needs an execute method, though we mock perform_operation in Calculator
    def execute(self, a, b):
        return a + b
    
    # Needs a validate_operands method for the REPL operation flow
    def validate_operands(self, a, b):
        pass


class TestCalculatorREPL(unittest.TestCase):

    def setUp(self):
        # Patch sys.stdout to capture output printed by the REPL
        self.stdout_patch = patch('sys.stdout', new_callable=io.StringIO)
        self.mock_stdout = self.stdout_patch.start()
        
    def tearDown(self):
        self.stdout_patch.stop()

    # FIX 1: Update helper to accept optional 'count' argument
    def assert_output_contains(self, expected_substring, count=1):
        """Check if the captured output contains the specified substring (count times)."""
        output = self.mock_stdout.getvalue()
        actual_count = output.count(expected_substring)
        self.assertEqual(actual_count, count, 
                         f"Expected '{expected_substring}' to appear {count} time(s), but found {actual_count} in output:\n---\n{output}\n---")


    # FIX: Mock the Observer classes to assert calls based on mock return values
    @patch('app.calculator_repl.AutoSaveObserver')
    @patch('app.calculator_repl.LoggingObserver')
    @patch('app.calculator_repl.OperationFactory')
    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input')
    def test_repl_help_and_exit(self, mock_input, MockCalculator, MockFactory, MockLoggingObserver, MockAutoSaveObserver):
        """Test 'help' command, initialization, and graceful 'exit'."""
        
        # Configure input to return a sequence of commands, ending with 'exit'
        mock_input.side_effect = ['help', 'exit']
        
        mock_calc = MockCalculator.return_value
        # Mock save_history call on exit
        mock_calc.save_history.return_value = None

        calculator_repl()
        
        # 1. Test Initialization and Observers
        MockCalculator.assert_called_once()
        self.assertEqual(mock_calc.add_observer.call_count, 2)
        
        # Verify the Observer classes were instantiated correctly
        MockLoggingObserver.assert_called_once()
        MockAutoSaveObserver.assert_called_once_with(mock_calc)
        
        # Verify the instantiated mock objects were passed to add_observer
        mock_calc.add_observer.assert_any_call(MockLoggingObserver.return_value)
        mock_calc.add_observer.assert_any_call(MockAutoSaveObserver.return_value)
        
        # 2. Test 'help' command output
        self.assert_output_contains("Available commands:")
        self.assert_output_contains("add, subtract, multiply, divide, power, root")
        
        # 3. Test 'exit' command logic
        mock_calc.save_history.assert_called_once()
        self.assert_output_contains("History saved successfully.")
        self.assert_output_contains("Goodbye!")
        
    @patch('app.calculator_repl.OperationFactory')
    @patch('app.calculator_repl.Calculator')
    # Use ['undo', 'undo'] and ['redo', 'redo'] to ensure we test both success and failure paths
    @patch('builtins.input', side_effect=['clear', 'history', 'undo', 'undo', 'redo', 'redo', 'unknown', 'exit'])
    def test_repl_state_and_unknown_commands(self, mock_input, MockCalculator, MockFactory):
        """Test history, clear, undo, redo, and unknown commands."""
        
        mock_calc = MockCalculator.return_value
        
        # Mock history command output
        mock_calc.show_history.return_value = ["1. 1 + 1 = 2"]
        
        # Sequence of calls: undo (success), undo (failure)
        mock_calc.undo.side_effect = [True, False] 
        # Sequence of calls: redo (success), redo (failure)
        mock_calc.redo.side_effect = [True, False] 
        
        calculator_repl()
        
        # Check 'clear'
        mock_calc.clear_history.assert_called_once()
        self.assert_output_contains("History cleared")
        
        # Check 'history'
        mock_calc.show_history.assert_called_once()
        self.assert_output_contains("Calculation History:")
        self.assert_output_contains("1. 1 + 1 = 2")
        
        # Check 'undo' success and failure
        self.assert_output_contains("Operation undone")
        self.assert_output_contains("Nothing to undo") 

        # Check 'redo' success and failure
        self.assert_output_contains("Operation redone")
        self.assert_output_contains("Nothing to redo")
        
        # Check unknown command
        self.assert_output_contains("Unknown command: 'unknown'. Type 'help' for available commands.")

    @patch('app.calculator_repl.OperationFactory')
    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['add', '1', '2', 'exit'])
    def test_repl_successful_arithmetic_operation(self, mock_input, MockCalculator, MockFactory):
        """Test a successful arithmetic operation."""
        
        mock_calc = MockCalculator.return_value
        
        mock_op = MockOperation()
        MockFactory.create_operation.return_value = mock_op
        
        # Mock a successful calculation result
        mock_calc.perform_operation.return_value = Decimal('3.00')
        
        calculator_repl()
        
        # Check OperationFactory call
        MockFactory.create_operation.assert_called_with('add')
        
        # Check Calculator method calls
        mock_calc.set_operation.assert_called_with(mock_op)
        mock_calc.perform_operation.assert_called_with('1', '2')
        
        # Check result output
        self.assert_output_contains("Result: 3") 

    @patch('app.calculator_repl.OperationFactory')
    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['add', 'a', '2', 'divide', '1', '0', 'exit'])
    def test_repl_arithmetic_error_handling(self, mock_input, MockCalculator, MockFactory):
        """Test error handling for ValidationError and OperationError."""
        
        mock_calc = MockCalculator.return_value
        MockFactory.create_operation.return_value = MockOperation()
        
        # Mock errors for perform_operation
        mock_calc.perform_operation.side_effect = [
            ValidationError("Invalid input 'a'"),
            OperationError("Division by zero")
        ]
        
        calculator_repl()
        
        # Check Validation Error handling
        self.assert_output_contains("Error: Invalid input 'a'")
        
        # Check Operation Error handling
        self.assert_output_contains("Error: Division by zero")

    @patch('app.calculator_repl.Calculator', side_effect=Exception("Fatal config error"))
    @patch('app.calculator_repl.logging.error')
    @patch('builtins.input', side_effect=['exit']) # Exit is never reached
    def test_repl_fatal_error_on_init(self, mock_input, MockCalculator, mock_logging_error):
        """Test fatal error handling during calculator initialization."""
        
        # The REPL re-raises the exception after handling it
        with self.assertRaisesRegex(Exception, "Fatal config error"):
             calculator_repl()

        self.assert_output_contains("Fatal error: Fatal config error")
        mock_logging_error.assert_called_once()
        
    @patch('app.calculator_repl.OperationFactory')
    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=[EOFError])
    def test_repl_interrupt_and_eof(self, MockCalculator, MockFactory):
        """Test EOF and KeyboardInterrupt handling."""
        
        # Simulate Ctrl+D (EOFError)
        # Note: KeyboardInterrupt is generally tested by patching input and asserting the error handler is hit, 
        # but the current setup only allows for checking EOFError easily in one run.
        
        calculator_repl()
        
        # Check for EOFError output
        self.assert_output_contains("Input terminated. Exiting...")
        
        # Assert save_history is still called on exit
        MockCalculator.return_value.save_history.assert_called()


    @patch('app.calculator_repl.OperationFactory')
    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['clear', 'history', 'exit'])
    def test_repl_empty_history_output(self, mock_input, MockCalculator, MockFactory):
        """Test the 'history' command when history is empty (Covers Line 63)."""
        mock_calc = MockCalculator.return_value
        # Mock show_history to return an empty list
        mock_calc.show_history.return_value = [] 
        
        calculator_repl()
        
        self.assert_output_contains("History cleared")
        self.assert_output_contains("No calculations in history")

    # FIX 2: Added autospec=True to logging for robustness
    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.logging', autospec=True) 
    @patch('builtins.input', side_effect=['exit'])
    def test_repl_exit_with_save_failure(self, mock_input, MockLogging, MockCalculator):
        """Test 'exit' command when save_history fails (Covers Lines 54-55)."""
        mock_calc = MockCalculator.return_value
        # Mock save_history to raise an exception
        mock_calc.save_history.side_effect = Exception("File save error") 
        
        calculator_repl()
        
        # Check that the warning message is displayed
        self.assert_output_contains("Warning: Could not save history: File save error")
        self.assert_output_contains("Goodbye!")
        
        # Assert logging.warning was called with exc_info=True
        MockLogging.warning.assert_called_with(ANY, exc_info=True)


    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['save', 'load', 'save', 'load', 'exit'])
    def test_repl_save_load_failure_paths(self, mock_input, MockCalculator):
        """Test successful and unsuccessful paths for 'save' and 'load' commands (Covers Lines 94-99, 103-108)."""
        mock_calc = MockCalculator.return_value
        
        # Setup side effects for save and load: Success, Failure, Success, Failure
        mock_calc.save_history.side_effect = [None, OperationError("Save failed"), None]
        mock_calc.load_history.side_effect = [None, OperationError("Load failed")]
        
        calculator_repl()
        
        # Test Save Success (1st call)
        self.assert_output_contains("History saved successfully")
        
        # Test Load Success (1st call)
        self.assert_output_contains("History loaded successfully")

        # FIX 3: Corrected assertion string for Save Failure (REPL prints "Error saving history:...")
        self.assert_output_contains("Error saving history: Save failed")
        
        # FIX 3: Corrected assertion string for Load Failure (REPL prints "Error loading history:...")
        self.assert_output_contains("Error loading history: Load failed")

    @patch('app.calculator_repl.OperationFactory')
    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['add', 'cancel', 'divide', '10', 'cancel', 'exit'])
    def test_repl_operation_cancel_input(self, mock_input, MockCalculator, MockFactory):
        """Test 'cancel' input for the first and second operand prompts (Covers Lines 116-117, 120-121)."""
        calculator_repl()
        
        # Assert perform_operation was never called
        self.assertEqual(MockCalculator.return_value.perform_operation.call_count, 0)
        
        # FIX 1: 'count' argument is now supported by the helper function
        self.assert_output_contains("Operation cancelled", count=2)


    @patch('app.calculator_repl.OperationFactory')
    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['add', '1', '2', 'exit'])
    def test_repl_operation_unexpected_error(self, mock_input, MockCalculator, MockFactory):
        """Test handling a general unexpected exception during operation (Covers Lines 138-140)."""
        mock_calc = MockCalculator.return_value
        MockFactory.create_operation.return_value = MockOperation()
        
        # Mock a generic exception that is not a ValidationError or OperationError
        mock_calc.perform_operation.side_effect = Exception("Unexpected system error")

        calculator_repl()
        
        # Check that the unexpected error path was hit
        self.assert_output_contains("Unexpected error: Unexpected system error")
        
        # FIX 4: Check for the prompt string "Enter command: " (appears twice: initial, and after error)
        self.assert_output_contains("Enter command: ", count=2)


    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['history', 'exit'])
    def test_repl_main_loop_unexpected_error(self, mock_input, MockCalculator):
        """Test a general unexpected exception in the main REPL loop (Covers Lines 154-157)."""
        mock_calc = MockCalculator.return_value
        # Mock show_history to raise a general exception
        mock_calc.show_history.side_effect = Exception("Error in history access")
        
        calculator_repl()
        
        # Check that the general loop error path was hit
        self.assert_output_contains("Error: Error in history access")
        
        # FIX 4: Check for the prompt string "Enter command: " (appears twice: initial, and after error)
        self.assert_output_contains("Enter command: ", count=2)