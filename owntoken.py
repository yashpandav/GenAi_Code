generatedToken = []

def generate_token(char):
    ascii_val = ord(char)
    hex_val = format(ascii_val, 'X') 
    token = f"{ascii_val}{hex_val}"
    generatedToken.append(token)

input_text = "Hello everyone, My name is Yash Pandav"

for char in input_text:
    generate_token(char)

print(' '.join(generatedToken))