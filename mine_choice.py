from accessability import pwint as print, line_pwint as line_print, inpwut as input, check_type as types, print_dic_list as list_dic, go_back as parent_func
import sys
def mine_choice(inventory, mine_list, mine_speeds):
    print('\n\n\n\n\n\n\n\n\n-----------------    Mining menu    -----------------\n\n\n\n\n\n\n\n\n')
    while True:
        try:
            print('\n')
            list_dic(mine_list)
            choice = input("Choose which block to mine, or type 0 to go back to the previous menu:\n")
            choice = types(choice, int, "Choose which block to mine, or type 0 to go back to the previous menu:\n")
            if choice == 0:
                parent_func()
                break
            elif choice in mine_list:
                quantity = input(f"How many {mine_list[choice]}(s) do you want to mine? (max 64)\n")
                quantity = types(quantity, int, f"How many {mine_list[choice]}(s) do you want to mine? (max 64)\n")
                if quantity > 64:
                    print("You can't mine more than 64 blocks at a time!")
                elif quantity <= 0:
                    print("You must mine at least 1 block!")
                else:
                    # Make a mining screen with moving dots
                    dots = ['.', '..', '...']
                    total_time = mine_speeds[mine_list[choice]]['default'] * quantity
                    delay = total_time / len(dots)
                    length_of_mining_line = len(f"\rMining {mine_list[choice]} {dots[0]}")
                    delay = delay / length_of_mining_line
                    for dot in dots:
                        print(f"\rMining {mine_list[choice]} {dot}", delay)
                    print(f"\nYou have mined {quantity} {mine_list[choice]}!")
                    # Add the blocks to the inventory
                    inventory[choice] += quantity
            else:
                print("Invalid input!")
        except Exception as e:
            print(f"Invalid input, {e}! at line {sys.exc_info()[-1].tb_lineno}")