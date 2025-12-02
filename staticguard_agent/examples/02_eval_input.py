def run_expression():
    # Dangerous use of eval on user input
    expr = input("Enter a Python expression: ")
    eval(expr)
