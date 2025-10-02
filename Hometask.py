# Import the random module to generate random numbers
import random

# Step 1: Create a list of 100 random integers between 0 and 1000
numbers = [random.randint(0, 1000) for _ in range(100)]

# Step 2: Sort the list from min to max without using sort()
# We'll implement Bubble Sort for simplicity
def bubble_sort(lst):
    n = len(lst)
    # Outer loop runs for each element
    for i in range(n):
        # Inner loop compares adjacent elements
        for j in range(0, n - i - 1):
            if lst[j] > lst[j + 1]:
                # Swap if current element is greater than next
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
    return lst

sorted_numbers = bubble_sort(numbers)

# Step 3: Separate even and odd numbers
even_numbers = [num for num in sorted_numbers if num % 2 == 0]
odd_numbers = [num for num in sorted_numbers if num % 2 != 0]

# Step 4: Calculate average of even numbers
# Use sum() / len(), but check if list is not empty
even_avg = sum(even_numbers) / len(even_numbers) if even_numbers else 0

# Step 5: Calculate average of odd numbers
odd_avg = sum(odd_numbers) / len(odd_numbers) if odd_numbers else 0

# Step 6: Print the results
print("Average of even numbers:", even_avg)
print("Average of odd numbers:", odd_avg)
