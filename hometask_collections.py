import random
import string

# Step 1: Generate a random number of dictionaries (between 2 and 10)
num_dicts = random.randint(2, 10)

# Step 2: Create a list to store our dictionaries
list_of_dicts = []

for i in range(num_dicts):
    # For each dictionary, generate a random number of keys (1 to 5)
    num_keys = random.randint(1, 5)

    # Randomly pick 'num_keys' letters (keys for dict)
    keys = random.sample(string.ascii_lowercase, num_keys)

    # Assign random values (0–100) to each key
    current_dict = {k: random.randint(0, 100) for k in keys}

    # Add dictionary to list
    list_of_dicts.append(current_dict)

# Print generated list of dicts
print("Generated list of dictionaries:")
print(list_of_dicts)

# Step 3: Merge into one common dictionary according to rules
final_dict = {}

# Keep track of which dict had the max value for a given key
key_owner = {}

# Iterate through list of dicts with their index (starting from 1 for readability)
for idx, d in enumerate(list_of_dicts, start=1):
    for key, value in d.items():
        # If key already exists in final_dict, check if new value is greater
        if key in key_owner:
            if value > final_dict[key_owner[key]]:
                # Remove old entry
                del final_dict[key_owner[key]]
                # Add new entry with suffix _dictNumber
                new_key = f"{key}_{idx}"
                final_dict[new_key] = value
                key_owner[key] = new_key
        else:
            # If key is new, add it without suffix first
            final_dict[key] = value
            key_owner[key] = key

# Step 4: Print the final merged dictionary
print("\nFinal merged dictionary:")
print(final_dict)
