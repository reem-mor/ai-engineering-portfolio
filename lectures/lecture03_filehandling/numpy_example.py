import numpy as np

# Create a 1D array
a = np.array([1, 2, 3, 4, 5])
print("1D array:", a)


# Create a 3x3 matrix with random integers ranging from 2 to 10
b = np.random.randint(2, 10, (3, 3))
print("3x3 matrix with random integers from 2 to 10:\n", b)


# Create new 3x3 matrix with boolean values where each element is True if the corresponding element in b
# is greater than 3, and False otherwise
c = np.zeros((3, 3), dtype=bool)
c = b > 3
print("Boolean matrix where elements are True if corresponding element in b is greater than 3:\n", c)
