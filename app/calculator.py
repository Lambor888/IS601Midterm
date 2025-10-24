#记录操作历史，每一个元素都是calculation实例
from app.history import HistoryObserver
import logging
import os
from app.calculation import Calculation
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.opeartions import Operation



Number = Union[int, float, Decimal]
CalculationResult = Union[Number, str]

class Calculator:

    def __init__(self, config: Optional[CalculatorConfig] = None):
        """
        Initialize calculator with configuration.

        Args:
            config (Optional[CalculatorConfig], optional): Configuration settings for the calculator.
                If not provided, default settings are loaded based on environment variables.
        """
        if config is None:
            # Determine the project root directory if no configuration is provided
            current_file = Path(__file__)
            project_root = current_file.parent.parent
            config = CalculatorConfig(base_dir=project_root)

        # Assign the configuration and validate its parameters
        self.config = config
        self.config.validate()

        # Ensure that the log directory exists
        os.makedirs(self.config.log_dir, exist_ok=True)

        # Set up the logging system
        self._setup_logging()

        # Initialize calculation history and operation strategy
        self.history: List[Calculation] = []
        self.operation_strategy: Optional[Operation] = None

        # Initialize observer list for the Observer pattern
        self.observers: List[HistoryObserver] = []

        # Initialize stacks for undo and redo functionality using the Memento pattern
        self.undo_stack: List[CalculatorMemento] = []
        self.redo_stack: List[CalculatorMemento] = []

        # Create required directories for history management
        self._setup_directories()
        




    def add_observer(self, observer: HistoryObserver) -> None:
        """
        Register a new observer.

        Adds an observer to the list, allowing it to receive updates when new
        calculations are performed.

        Args:
            observer (HistoryObserver): The observer to be added.
        """
        self.observers.append(observer)
        logging.info(f"Added observer: {observer.__class__.__name__}")

    def remove_observer(self, observer: HistoryObserver) -> None:
        """
        Remove an existing observer.

        Removes an observer from the list, preventing it from receiving further updates.

        Args:
            observer (HistoryObserver): The observer to be removed.
        """
        self.observers.remove(observer)
        logging.info(f"Removed observer: {observer.__class__.__name__}")

    def notify_observers(self, calculation: Calculation) -> None:
        """
        Notify all observers of a new calculation.

        Iterates through the list of observers and calls their update method,
        passing the new calculation as an argument.

        Args:
            calculation (Calculation): The latest calculation performed.
        """
        for observer in self.observers:
            observer.update(calculation)