#程序主循环，在循环开始之初初始化calculator类
from app.opeartions import OperationFactory

def main_loop():

    op = OperationFactory.create_operation('-')
    print(op.exectue(1,2))