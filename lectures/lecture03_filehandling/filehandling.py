# File Handling in Python.
#Write text file and search for the world "Hello" in the file, count the number of times it appears and print the count.
#print the count of "Hello" in the file. use "w+" mode to create the file if it doesn't exist and write some text to it.
with open("file.txt", "w+") as file:
    file.write("Hello world! hello everyone. HELLO Python.")
    file.seek(0)  # Move cursor to the beginning
    content = file.read()  # Read all text from start to end
    count = content.lower().count("hello")  # Case-insensitive count
    print(f"The word 'Hello' appears {count} times in the file.")
    