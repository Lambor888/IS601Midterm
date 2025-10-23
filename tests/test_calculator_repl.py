
# --- 测试用例 ---
if __name__ == '__main__':
    test_cases = [
        "10 + 5",             # 整数相加
        "-3.14 * 2",          # 负数、小数、乘法
        "100 / -4.0 =",       # 包含等号
        "25 % 3",             # 取余
        "10 mod 3",           # mod 操作符 (二元)
        "5 pow 3",            # pow 操作符 (二元)
        "10 root 81",         # root 操作符 (二元: e.g., 10th root of 81)
        "3 abs -15",          # abs 操作符 (二元: e.g., 3rd abs of -15, 只是语法合法)
        "20 per 100",         # per 操作符 (二元: e.g., 20 percent of 100)
        "history",            # 命令
        " undo ",             # 命令带空格
        "  -1.23e-5 / 42.1  ", # 科学计数法
    ]
    
    print("--- 合法输入测试 (全部二元) ---")
    for tc in test_cases:
        try:
            result = parse_calculator_input_binary_only(tc)
            print(f"输入: '{tc}' -> 输出: {result}")
        except ValueError as e:
            print(f"输入: '{tc}' -> 错误: {e}")

    print("\n--- 不合法输入测试 ---")
    invalid_cases = [
        "10 plus 5",         # 非法操作符
        "10 5",              # 缺少操作符
        "log 100",           # 非法命令或操作符
        "root 81",           # 缺少第一个数字 (不再视为一元)
        "10 +",              # 缺少第二个数字
        "10 + 5 5",          # 多余的输入
    ]

    for tc in invalid_cases:
        try:
            result = parse_calculator_input_binary_only(tc)
            print(f"输入: '{tc}' -> **(ERROR: 错误地通过)** -> {result}")
        except ValueError as e:
            print(f"输入: '{tc}' -> 错误: {e}")