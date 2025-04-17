import time
def pwint(text, times=0.01):
    #Check if the variable time is a float
    if isinstance(times, float):
        pass
    else:
        return ('no - error, isinstance(times, float) is false')
    for char in text:
        print(char, end='', flush=True)
        time.sleep(float(times))
def line_pwint(text, times=0.1):
    if isinstance(times, float):
        pass
    else:
        return 'no'
    if text is None:
        return
    for line in text.split('\n'):
        print(line)
        time.sleep(times)
def inpwut(prompt, times=0.01):
    if isinstance(times, float):
        pass
    else:
        return 'no'
    user_input = ''
    print('\n', end='', flush=True)
    for char in prompt:
        print(char, end='', flush=True)
        time.sleep(times)
    user_input = input()
    return user_input
def check_type(result, type_checked, question, question_delay = 0.01):
    reask_needed = False
    while True:
        try:
            if reask_needed:
                result = inpwut(question, question_delay)
            result = type_checked(result)
            break
        except Exception:
            pwint("Invalid input!")
            reask_needed = True
    return result
def print_dic_list(dic_list):
    for key, value in dic_list.items():
        print(f"{key}:\t{value}")

def go_back(parent=None):
    if parent is not None:
        parent()
    else:
        print("No previous menu to go back to.")