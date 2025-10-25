# Enhanced Calculator Software

## 1. Project Description

This is an enhanced command-line calculator application. In addition to providing the basic arithmetic operations—addition ($+$), subtraction ($-$), multiplication ($*$), and division ($/$), it introduces the following advanced mathematical functions:

* Square Root / Root (`root`)
* Exponentiation (`pow`)
* Integer Division (`div`)
* Modulo / Remainder (`%`)

Furthermore, the software includes features for managing calculation history, custom configuration, and data persistence.

## 2. Installation Instructions

Please follow these steps to install and run the software:

1.  **Install Python 3:**
    Ensure that **Python 3.x** is installed on your system.

2.  **Activate Virtual Environment:**
    It is highly recommended to create and activate a Python virtual environment to isolate project dependencies.
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # macOS/Linux
    .\venv\Scripts\activate   # Windows
    ```

3.  **Install Requirements:**
    Install all necessary libraries using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

## 3. Configuration Setup

The main configuration for the project is managed through the `.env` file. Please create or modify the `.env` file in the project's root directory and set the following variables:

| Variable Name | Description |
| :--- | :--- |
| `CALCULATOR_BASE_DIR` | The root directory for storing history files. |
| `CALCULATOR_MAX_HISTORY_SIZE` | The maximum number of calculation entries to keep in history. |
| `CALCULATOR_AUTO_SAVE` | A boolean value (`True` / `False`) to enable/disable automatic history saving. |
| `CALCULATOR_PRECISION` | The numerical precision used for floating-point calculations. |
| `CALCULATOR_MAX_INPUT_VALUE` | The maximum allowable numerical value for user input. |
| `CALCULATOR_DEFAULT_ENCODING` | The default character encoding (e.g., `utf-8`) for file operations. |

## 4. How to Use

### Calculation Format

**Format:** `Operand1 Operator Operand2`, followed by pressing Enter to execute the calculation.

**Examples:**
* `1 + 1`
* `6 - 9`

### Accepted Operators

| Symbol / Command | Description |
| :--- | :--- |
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `%` | Modulo / Remainder |
| `pow` | Exponentiation (e.g., `2 pow 3` calculates $2^3$) |
| `root` | Root calculation (e.g., `9 root 2` calculates $\sqrt[2]{9}$) |
| `div` | Integer Division |
| `abs` | Absolute Difference (e.g., `10 abs 5` calculates \|10-5\|) |
| `pre` | Percentage Calculation (e.g., `10 pre 100` calculates 10\% ) |

### Standalone Commands

The following commands can be entered alone to perform specific actions:

| Command | Description |
| :--- | :--- |
| `history` | Display the calculation history. |
| `clear` | Clear the current calculation history. |
| `undo` | Undo the last performed calculation. |
| `redo` | Redo the last undone calculation. |
| `save` | Manually save calculation history to a file using the `pandas` library. |
| `load` | Load calculation history from a file using the `pandas` library. |
| `help` | Display available commands and usage instructions. |
| `exit` | Exit the application gracefully. |

## 5. Testing Instructions

Unit testing is performed using the **pytest** framework.

### Pre-requisite
Ensure that `pytest` and any necessary dependencies (e.g., `coverage`) are installed. They should be included in `requirements.txt`.

### Running Tests
To execute the full test suite, navigate to the project root directory and run the following command:

```bash
pytest