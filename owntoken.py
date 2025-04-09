generatedToken = []

# This is a token generation which takes a input and character by character converts character into a ascii value and hex value and by combining them, the special token is generated.

def generate_token(char):
    ascii_val = ord(char)
    hex_val = format(ascii_val, 'X') 
    token = f"{ascii_val}{hex_val}"
    generatedToken.append(token)

input_text = "Hello everyone, My name is Yash Pandav"

for char in input_text:
    generate_token(char)

print(' '.join(generatedToken))

# Example
# CHAR   ASCII   HEX TOKEN
# A       65     41   6541
# B       66     42   6642
# Y       89     59    8959
# Z       90     5A    905A
# a       97     61    9761
# b       98     62    9862
# y      121     79   12179
# z      122     7A   1227A
# (space) 32     20    3220
# 2       50     32    5032
# 7       55     37    5537
# @       64     40    6440