from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict
class Operation(ABC):

    @abstractmethod
    def exectue(self, a: Decimal, b : Decimal) -> str:

        pass

    def validate_operands(self, a :Decimal , b:Decimal) -> None:

        pass

    def __str__(self):
        return self.__class__.__name__
    

class Addition(Operation):
    
    def exectue(self, a, b):
        self.validate_operands(a,b)
        return str(a+b)
    

class Subtraction(Operation):

    def exectue(self, a, b):
        self.validate_operands(a,b)
        return str(a-b)
    

class OperationFactory:

    _operations: Dict[str, type]= {
        '+' : Addition,
        '-' : Subtraction
    }


    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        operation_class = cls._operations.get(operation_type)
        if not operation_class:
            raise ValueError(f"Unknown operation: {operation_class}")
        return operation_class()