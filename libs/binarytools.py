 
    
def print_bitarray(binary_list, end="\n"):
    current_bit = 0
    bits_per_line = 60
    for bit in binary_list:
        current_bit += 1
        print("%i" % (1 if bit else 0), end="")
        if current_bit % 60 == 0:
            print()
        elif current_bit % 4 == 0:
            print("", end=" ")
    print("", end=end)
