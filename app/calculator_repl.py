#程序主循环，在循环开始之初初始化calculator类
from app.opeartions import OperationFactory
from app.calculator import Calculator
from app.history import AutoSaveObserver, LoggingObserver
from app.exceptions import UnknownOperationError, ValidationError
import logging
import os
import re
import colorama
from colorama import Fore, Back, Style

COMMANDS = ["history", "help", "undo","redo","save","load","exit","clear"]

def clear_console():
    # 检测操作系统类型
    if os.name == 'nt':
        # 'nt' 表示 Windows 系统，使用 'cls' 命令清屏
        _ = os.system('cls')
    else:
        # 其他系统 (如 macOS 和 Linux)，使用 'clear' 命令清屏
        # os.name == 'posix' 适用于这些系统
        _ = os.system('clear')

def split_input(input_str: str) -> list[str]:
    """
    解析计算器输入字符串，并将其拆分为一个操作符和操作数的列表。
    
    合法格式包括：
    1. 二元运算: <数字> <操作符> <数字> [=]
    2. 命令: history, help, undo,save
    
    操作符: +, -, *, /, %, div, root, pow, abs, per (全部作为二元操作符处理)
    数字: 整数、小数、负数。
    
    Args:
        input_str: 用户输入的字符串。
        
    Returns:
        拆分后的字符串数组，例如 ['10', '+', '5'] 或 ['history']。
        
    Raises:
        ValueError: 如果输入不合法，则抛出此错误。
    """
    
    # 预处理：移除首尾空格，将输入转换为小写
    processed_input = input_str.strip().lower()

    # --- 1. 匹配命令 ---

    if processed_input in COMMANDS:
        return [processed_input]

    # 预处理：移除末尾的等号（如果存在）
    if processed_input.endswith('='):
        processed_input = processed_input[:-1].strip()

    # --- 正则表达式定义 ---
    
    # 定义数字（包括负数、小数、科学计数法）：
    # (-?\d*\.?\d+(?:[eE][-+]?\d+)?)
    NUM_PATTERN = r"(-?\d*\.?\d+)"

    # 定义所有二元操作符：
    # + - * / % mod root pow abs per
    # 注意：+ - * / % 必须转义或在字符集中
    OPERATOR_PATTERN = r"(\+|-|\*|\/|%|div|root|pow|abs|per)"

    # --- 2. 匹配二元运算 (数字 操作符 数字) ---
    # 模式: <数字> <操作符> <数字>
    # 使用 \s* 匹配任意数量的空格
    binary_pattern = re.compile(
        # 字符串开头 ^
        fr"^\s*" 
        # 数字 1
        fr"{NUM_PATTERN}\s*"
        # 操作符
        fr"{OPERATOR_PATTERN}\s*"
        # 数字 2
        fr"{NUM_PATTERN}\s*"
        # 字符串结尾 $
        fr"$"
    )
    
    match_binary = binary_pattern.match(processed_input)
    
    if match_binary:
        # 匹配组依次是：数字1, 操作符, 数字2
        result = [
            # group(1): 第一个数字
            match_binary.group(1), 
            # group(2): 操作符
            match_binary.group(2), 
            # group(3): 第二个数字
            match_binary.group(3)
        ]
        return result

    # --- 3. 其他情况：输入不合法 ---
    raise ValueError(f"输入格式不合法: '{input_str}'。合法格式为 '数字 操作符 数字 [=]' 或 '命令'。")


def main_loop():

    
    try:
        calc = Calculator()
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))
        print(Fore.GREEN + "Welcome to my calculator, input help for help" + Style.RESET_ALL)
        while True:
            try:
                inputstr = input()
                arr = split_input(inputstr)
                clear_console()
                print('\n')
                if(arr[0] == 'help'):
                    logging.info('Show help')
                    continue
                if(arr[0] == 'exit'):
                    # Attempt to save history before exiting
                    try:
                        calc.save_history()
                        print(Fore.GREEN+"History saved successfully."+Style.RESET_ALL)
                    except Exception as e:
                        print(f"Warning: Could not save history: {e}")
                    print(Back.GREEN+"Goodbye!"+Style.RESET_ALL)
                    break
                if(arr[0] == 'clear'):
                    # Clear calculation history
                    calc.clear_history()
                    print(Fore.GREEN+"History cleared"+Style.RESET_ALL)
                    logging.info('Clear History')
                    continue
                if(arr[0] == 'undo'):
                    # Undo the last calculation
                    if calc.undo():
                        print(Fore.GREEN+"Operation undone"+Style.RESET_ALL)
                        logging.info('Undo Operation')
                    else:
                        print(Fore.RED+"Nothing to undo"+Style.RESET_ALL)
                    continue
                if(arr[0] == 'redo'):
                    # Redo the last undone calculation
                    if calc.redo():
                        print(Fore.GREEN+"Operation redone"+Style.RESET_ALL)
                        logging.info('Redo operation')
                    else:
                        print(Fore.RED+"Nothing to redo"+Style.RESET_ALL)
                    continue
                if(arr[0] == 'load'):
                    # Load calculation history from file
                    try:
                        calc.load_history()
                        print(Fore.GREEN+"History loaded successfully"+Style.RESET_ALL)
                        logging.info('Load Histtory')
                    except Exception as e:
                        logging.error(f"Error loading history: {e}")
                        print(Fore.RED+ f"Error loading history: {e}"+Style.RESET_ALL)
                    continue
                if(arr[0] == 'save'):
                    # Save calculation history to file
                    try:
                        calc.save_history()
                        print(Fore.GREEN+"History saved successfully"+Style.RESET_ALL)
                    except Exception as e:
                        logging.error(f"Error saving history: {e}")
                        print(Fore.RED+ f"Error saving history: {e}"+Style.RESET_ALL)
                    continue
                if(arr[0] == 'history'):
                    history = calc.show_history()
                    if not history:
                        print(Fore.RED+ "No calculations in history"+Style.RESET_ALL)
                    else:
                        print(Fore.BLUE+ "\nCalculation History:"+Style.RESET_ALL)
                        logging.info(f'Show History {len(history)} lines in total')
                        for i, entry in enumerate(history, 1):
                            print(Back.BLUE+f"{entry}"+Style.RESET_ALL)
                    continue
#---------------create operation
                if len(arr) == 3:
                    try:
                        operation = OperationFactory.create_operation(arr[1])
                        calc.set_operation(operation)
                        result = calc.perform_op(arr[0],arr[2])
                        print(Back.YELLOW + arr[0],arr[1],arr[2],'=',result,'\n' +Style.RESET_ALL)
                    except (UnknownOperationError, ValidationError) as e:
                        print(Fore.RED+f"{e}"+Style.RESET_ALL)
                        logging.error(f'UnknownOperationError {e}')
                        continue
                    except Exception as e:
                        print(Fore.RED+f"{e}"+Style.RESET_ALL)
                        logging.error(f'Error {e}')
                        continue

                
#-----------------
            except ValueError:
                print(Fore.RED+ "Imput Error"+Style.RESET_ALL)
                logging.info('User input error')
                continue
    except Exception as e:
        print(Fore.RED+ f"error:{e}" +Style.RESET_ALL)
        logging.error(f'Error {e}')
        pass