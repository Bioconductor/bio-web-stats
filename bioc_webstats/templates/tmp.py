from collections import defaultdict

# Sample list of tuples
lst = [("apple", 1), ("banana", 2), ("cherry", 3), ("AVACado", 4)]

# Initialize a defaultdict with a list as default value
result = defaultdict(list)

# Iterate through the list of tuples and append to the respective dictionary key
for item in sorted(lst, key=lambda x: x[0].upper()):
    first_char = item[0][0].upper()  # Extract the first character of the string
    result[first_char].append(item)

# Convert defaultdict to a regular dictionary
result = dict(result)

print(result)
