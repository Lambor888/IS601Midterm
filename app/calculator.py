#记录操作历史，每一个元素都是calculation实例
from app.history import HistoryObserver
import logging
from app.calculation import Calculation
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal

Number = Union[int, float, Decimal]
CalculationResult = Union[Number, str]

class Calculator:

    def __init__(self):
        pass




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