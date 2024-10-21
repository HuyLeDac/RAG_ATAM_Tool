import os

file_path = os.path.join("inputs", "architecture_description.txt")
architecture_description = open(file_path, "r")

print(architecture_description.read())