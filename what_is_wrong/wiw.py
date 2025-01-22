# -------------PRINT FunctinoS ------------
def print_o(message):
    # ANSI escape code for orange text
    orange_text = "\033[38;5;214m" + message + "\033[0m"
    print(orange_text)

def print_rg(message, condition,err_msg=None):
    if condition:
        #green text
        colored_text = "\033[32m" + message + "\033[0m"
    else:
        #red text
        colored_text = "\033[31m" + message + "\033[0m"
        if err_msg:
            colored_text += "\033[31m - " + err_msg + "\033[0m"
    print(colored_text)