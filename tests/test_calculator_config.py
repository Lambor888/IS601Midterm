import unittest
import os
from unittest.mock import patch, MagicMock
from pathlib import Path
from decimal import Decimal
import datetime

# Adjust imports based on your actual project structure
from app.calculator_config import CalculatorConfig, get_project_root
from app.exceptions import ConfigurationError

# Define a consistent mock path for testing get_project_root
MOCK_PROJECT_ROOT = Path('/mock_project')

class TestCalculatorConfig(unittest.TestCase):

    @patch('app.calculator_config.Path')
    def test_get_project_root(self, MockPath):
        """Test that get_project_root correctly determines the root directory."""
        # Mock Path(__file__) behavior to navigate up two levels
        mock_file_path = MagicMock()
        mock_file_path.parent.parent = MOCK_PROJECT_ROOT
        MockPath.return_value = mock_file_path

        root = get_project_root()
        self.assertEqual(root, MOCK_PROJECT_ROOT)

    @patch.dict(os.environ, {
        'CALCULATOR_MAX_HISTORY_SIZE': '50',
        'CALCULATOR_AUTO_SAVE': 'False',
        'CALCULATOR_PRECISION': '5',
        'CALCULATOR_MAX_INPUT_VALUE': '1000',
        'CALCULATOR_DEFAULT_ENCODING': 'utf-16'
    }, clear=True)
    @patch('app.calculator_config.get_project_root', return_value=MOCK_PROJECT_ROOT)
    def test_config_init_from_env_vars(self, mock_get_root):
        """Test initialization when values are loaded from mocked environment variables."""
        config = CalculatorConfig()
        
        self.assertEqual(config.max_history_size, 50)
        self.assertFalse(config.auto_save)
        self.assertEqual(config.precision, 5)
        self.assertEqual(config.max_input_value, Decimal('1000'))
        self.assertEqual(config.default_encoding, 'utf-16')
        self.assertEqual(config.base_dir, MOCK_PROJECT_ROOT.resolve())
        
        # Test property methods based on base_dir default
        expected_root = MOCK_PROJECT_ROOT.resolve()
        self.assertEqual(config.log_dir, expected_root / 'logs')
        self.assertEqual(config.history_dir, expected_root / 'history')
        self.assertEqual(config.history_file, expected_root / 'history' / 'calculator_history.csv')

    @patch('app.calculator_config.get_project_root', return_value=MOCK_PROJECT_ROOT)
    def test_config_init_with_explicit_args(self, mock_get_root):
        """Test initialization with explicit arguments overriding environment variables."""
        
        # Mock environment variables to ensure they are ignored when args are passed
        with patch.dict(os.environ, {'CALCULATOR_MAX_HISTORY_SIZE': '9999'}, clear=True):
            
            custom_base_dir = Path('/custom/base')
            config = CalculatorConfig(
                base_dir=custom_base_dir,
                max_history_size=10,
                auto_save=True,
                precision=20,
                max_input_value=Decimal('9999.99'),
                default_encoding='latin-1'
            )
            
            self.assertEqual(config.base_dir, custom_base_dir.resolve())
            self.assertEqual(config.max_history_size, 10)
            self.assertTrue(config.auto_save)
            self.assertEqual(config.precision, 20)
            self.assertEqual(config.max_input_value, Decimal('9999.99'))

    # Helper function to ensure validation passes for standard case
    @patch('app.calculator_config.get_project_root', return_value=MOCK_PROJECT_ROOT)
    def test_config_validation_success(self, mock_get_root):
        """Test validation for a valid configuration."""
        config = CalculatorConfig(max_history_size=1, precision=1, max_input_value=1)
        # Should not raise any exception
        config.validate()

    # FIX: Mock __init__ to prevent it from calling self.validate() prematurely.
    @patch('app.calculator_config.CalculatorConfig.__init__', return_value=None)
    @patch('app.calculator_config.get_project_root', return_value=MOCK_PROJECT_ROOT)
    def test_config_validation_failure(self, mock_get_root, mock_init):
        """Test validation for invalid configuration parameters."""
        
        # When __init__ is mocked, we must manually set the required attributes
        
        # 1. Test max_history_size <= 0
        config_history = CalculatorConfig()
        config_history.max_history_size = 0
        config_history.precision = 10
        config_history.max_input_value = Decimal('1000')

        with self.assertRaisesRegex(ConfigurationError, "max_history_size must be positive"):
            config_history.validate()

        # 2. Test precision <= 0
        config_precision = CalculatorConfig()
        config_precision.max_history_size = 1
        config_precision.precision = 0
        config_precision.max_input_value = Decimal('1000')
        with self.assertRaisesRegex(ConfigurationError, "precision must be positive"):
            config_precision.validate()
            
        # 3. Test max_input_value <= 0
        config_input = CalculatorConfig()
        config_input.max_history_size = 1
        config_input.precision = 1
        config_input.max_input_value = Decimal('0')
        with self.assertRaisesRegex(ConfigurationError, "max_input_value must be positive"):
            config_input.validate()

    def test_auto_save_parsing(self):
        """Test various environment variable values for auto_save."""
        
        # Test 'true'
        with patch.dict(os.environ, {'CALCULATOR_AUTO_SAVE': 'true'}, clear=True):
            self.assertTrue(CalculatorConfig().auto_save)
            
        # Test '0'
        with patch.dict(os.environ, {'CALCULATOR_AUTO_SAVE': '0'}, clear=True):
            self.assertFalse(CalculatorConfig().auto_save)
            
        # Test explicit override
        with patch.dict(os.environ, {'CALCULATOR_AUTO_SAVE': 'true'}, clear=True):
            self.assertFalse(CalculatorConfig(auto_save=False).auto_save)

if __name__ == '__main__':
    unittest.main()