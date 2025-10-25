import unittest
import datetime
from decimal import Decimal
from typing import Dict, Any

# Adjust imports based on your actual project structure
from app.calculator_memento import CalculatorMemento
from app.calculation import Calculation

# Create actual Calculation objects for testing Memento's history
# Calculation automatically computes the result upon initialization
CALC_ADD = Calculation(operation="Addition", operand1=Decimal('10'), operand2=Decimal('5'), result='15')
CALC_SUB = Calculation(operation="Subtraction", operand1=Decimal('20'), operand2=Decimal('3'),result='17')

class TestCalculatorMemento(unittest.TestCase):

    def setUp(self):
        """Setup a list of calculations and a test memento instance."""
        self.mock_history = [CALC_ADD, CALC_SUB]
        # Use a fixed timestamp for predictable serialization/deserialization
        self.mock_timestamp = datetime.datetime(2025, 1, 1, 10, 30, 0)
        self.memento = CalculatorMemento(
            history=self.mock_history.copy(), # Use copy for isolation
            timestamp=self.mock_timestamp
        )

    def test_memento_initialization(self):
        """Test that the memento is initialized correctly."""
        memento_auto_time = CalculatorMemento(history=[])
        self.assertIsInstance(memento_auto_time.timestamp, datetime.datetime)
        self.assertEqual(memento_auto_time.history, [])

        self.assertEqual(self.memento.history, self.mock_history)
        self.assertEqual(self.memento.timestamp, self.mock_timestamp)

    def test_to_dict_serialization(self):
        """Test the conversion of Memento to a dictionary."""
        memento_dict = self.memento.to_dict()
        
        self.assertIsInstance(memento_dict, dict)
        self.assertIn('history', memento_dict)
        self.assertIn('timestamp', memento_dict)
        self.assertEqual(memento_dict['timestamp'], self.mock_timestamp.isoformat())
        self.assertEqual(len(memento_dict['history']), 2)

        # Check the serialized calculation data
        calc_dict_1 = memento_dict['history'][0]
        self.assertEqual(calc_dict_1['operation'], 'Addition')
        self.assertEqual(calc_dict_1['result'], '15') 

    def test_from_dict_deserialization(self):
        """Test the creation of a Memento instance from a dictionary."""
        
        # Manually create the dictionary expected from to_dict
        mock_data: Dict[str, Any] = {
            'history': [
                CALC_ADD.to_dict(),
                CALC_SUB.to_dict()
            ],
            'timestamp': self.mock_timestamp.isoformat()
        }
        
        new_memento = CalculatorMemento.from_dict(mock_data)
        
        self.assertIsInstance(new_memento, CalculatorMemento)
        self.assertEqual(new_memento.timestamp, self.mock_timestamp)
        self.assertEqual(len(new_memento.history), 2)

        # Check that the restored history items are correct Calculation instances
        restored_calc_1 = new_memento.history[0]
        
        self.assertIsInstance(restored_calc_1, Calculation)
        self.assertEqual(restored_calc_1.operation, 'Addition')
        self.assertEqual(restored_calc_1.operand1, Decimal('10'))
        self.assertEqual(restored_calc_1.result, '15')
        
        # Compare the full state using to_dict for comprehensive check
        self.assertEqual(restored_calc_1.to_dict(), CALC_ADD.to_dict())
        
if __name__ == '__main__':
    unittest.main()