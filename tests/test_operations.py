import pytest
from decimal import Decimal
from app.opeartions import (
    OperationFactory, Addition, Subtraction, Multiplication, Division,
    Modulus, Int_Division, Power, Root, Percentage, AbsDiff
)
# 假设您的自定义异常在 app/exceptions.py 中定义
from app.exceptions import ValidationError, UnknownOperationError, OperationError

# 使用 Decimal('1.0') 来确保测试中的数值是 Decimal 类型
D = Decimal

# --------------------------------------------------------------------------
# 1. 测试基本的二元运算 (Basic Binary Operations)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("operation_class, a, b, expected_result", [
    # Addition
    (Addition, D('5'), D('3'), '8'),
    (Addition, D('-1'), D('1'), '0'),
    # Subtraction
    (Subtraction, D('10'), D('4'), '6'),
    (Subtraction, D('4'), D('10'), '-6'),
    # Multiplication
    (Multiplication, D('2.5'), D('2'), '5.0'),
    (Multiplication, D('-3'), D('3'), '-9'),
    # Division
    (Division, D('10'), D('3'), str(D('10')/D('3'))), # 确保结果与 Decimal 运算一致
    (Division, D('-9'), D('3'), '-3'),
    # Modulus
    (Modulus, D('10'), D('3'), '1'),
    (Modulus, D('10.5'), D('3'), '1.5'),
    # Int_Division
    (Int_Division, D('10'), D('3'), '3'),
    (Int_Division, D('10.5'), D('3'), '3'),
    # Power
    (Power, D('2'), D('3'), '8'),
    (Power, D('9'), D('0.5'), '3'), # 9的0.5次方 (平方根)
])
def test_basic_operations(operation_class, a, b, expected_result):
    """测试基本的加减乘除、模、整除和幂运算。"""
    op = operation_class()
    result = op.execute(a, b)
    # 确保结果是字符串，且数值正确
    assert isinstance(result, str)
    assert result == expected_result


# --------------------------------------------------------------------------
# 2. 测试除零错误 (Division by Zero Errors)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("operation_class", [
    Division, Modulus, Int_Division
])
def test_division_by_zero_raises_validation_error(operation_class):
    """测试除法、模和整除操作的除零验证。"""
    op = operation_class()
    with pytest.raises(ValidationError) as excinfo:
        op.execute(D('10'), D('0'))
    assert "Division by zero is not allowed" in str(excinfo.value)

# --------------------------------------------------------------------------
# 3. 测试特殊运算 (Special Operations)
# --------------------------------------------------------------------------

def test_abs_diff():
    """测试 AbsDiff (绝对差) 操作。"""
    op = AbsDiff()
    # a > b
    assert op.execute(D('10'), D('4')) == '6'
    # a < b
    assert op.execute(D('4'), D('10')) == '6'
    # a = b
    assert op.execute(D('5'), D('5')) == '0'

def test_percentage():
    """测试 Percentage (百分比) 操作。"""
    op = Percentage()
    # 10 / 50 * 100 = 20.00%
    assert op.execute(D('10'), D('50')) == '20.00%'
    # 1 / 3 * 100 = 33.333... -> 量化为 33.33%
    # 注意：这里依赖于 Decimal('1.00') 的量化行为
    assert op.execute(D('1'), D('3')) == '33.33%'
    # 除零
    with pytest.raises(ValidationError):
        op.execute(D('10'), D('0'))

# --------------------------------------------------------------------------
# 4. 测试 Root (开根号) 操作
# --------------------------------------------------------------------------

def test_root_valid_calculations():
    """测试有效的开根号计算。"""
    op = Root()
    # 平方根 (4 ** (1/2))
    assert op.execute(D('4'), D('2')) == '2.0'
    # 立方根 (8 ** (1/3))
    assert op.execute(D('8'), D('3')) == '2.0'
    # 负数的奇数根 (-8 ** (1/3) = -2)
    assert op.execute(D('-8'), D('3')) == '-2.0'

def test_root_validation_errors():
    """测试开根号的验证错误。"""
    op = Root()
    
    # 零根 (b=0)
    with pytest.raises(ValidationError) as excinfo:
        op.execute(D('4'), D('0'))
    assert "Zero root is undefined" in str(excinfo.value)

    # 负数的偶数根 (a < 0 且 b % 2 == 0)
    with pytest.raises(ValidationError) as excinfo:
        op.execute(D('-4'), D('2'))
    assert "Cannot calculate even root of a negative number" in str(excinfo.value)
    
    # 非整数根次
    with pytest.raises(ValidationError) as excinfo:
        op.execute(D('4'), D('2.5'))
    assert "Root degree must be an integer" in str(excinfo.value)

# --------------------------------------------------------------------------
# 5. 测试 OperationFactory
# --------------------------------------------------------------------------

def test_factory_create_valid_operation():
    """测试工厂创建有效的操作实例。"""
    # 测试加法
    op = OperationFactory.create_operation('+')
    assert isinstance(op, Addition)
    assert op.execute(D('1'), D('2')) == '3'
    
    # 测试乘法
    op = OperationFactory.create_operation('*')
    assert isinstance(op, Multiplication)

def test_factory_create_unknown_operation():
    """测试工厂创建未知操作时抛出 UnknownOperationError。"""
    with pytest.raises(UnknownOperationError) as excinfo:
        OperationFactory.create_operation('unknown_op')
    assert "Unknown operation" in str(excinfo.value)

def test_factory_register_new_operation():
    """测试工厂动态注册新操作。"""
    
    # 1. 定义一个简单的自定义操作
    class CustomOp(OperationFactory._operations['+']): # 继承自 Addition 以简化
        def execute(self, a, b):
            return str(a*10 + b*10) # 10a + 10b
            
    op_name = 'custom'
    # 确保注册前不存在
    assert op_name not in OperationFactory._operations
    
    # 2. 注册操作
    OperationFactory.register_operation(op_name, CustomOp)
    
    # 3. 验证注册成功
    assert op_name in OperationFactory._operations
    op = OperationFactory.create_operation(op_name)
    assert isinstance(op, CustomOp)
    
    # 4. 验证新操作的行为
    assert op.execute(D('1'), D('2')) == '30' # (1*10) + (2*10) = 30

def test_factory_register_invalid_class():
    """测试注册非 Operation 子类时抛出 TypeError。"""
    
    # 定义一个非 Operation 子类的类
    class NotAnOperation:
        pass
        
    with pytest.raises(TypeError) as excinfo:
        OperationFactory.register_operation('invalid', NotAnOperation)
    assert "Operation class must inherit from Operation" in str(excinfo.value)

# --------------------------------------------------------------------------
# 6. 其他辅助测试
# --------------------------------------------------------------------------

def test_operation_str_representation():
    """测试操作类的 __str__ 方法。"""
    op = Addition()
    assert str(op) == 'Addition'
    
    op = Root()
    assert str(op) == 'Root'