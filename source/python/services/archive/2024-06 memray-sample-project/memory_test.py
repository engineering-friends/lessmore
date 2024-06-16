"""NOTE: test is not very illustrative, just random sample from ChatGPT"""

import random
import time
import math
import os


def compute_squares(n):
    return [i**2 for i in range(n)]


def compute_cubes(n):
    return [i**3 for i in range(n)]


def random_sleep():
    time.sleep(random.uniform(0.01, 0.1))


def factorial(n):
    return math.factorial(n)


def string_manipulation(size):
    base_str = "abcdefghijklmnopqrstuvwxyz"
    result = ""
    for _ in range(size):
        result += random.choice(base_str)
    return result


def file_io_operations(file_name, size):
    with open(file_name, "w") as f:
        for _ in range(size):
            f.write(string_manipulation(100) + "\n")
    with open(file_name, "r") as f:
        data = f.readlines()
    os.remove(file_name)
    return data


def main():
    for _ in range(100):
        compute_squares(1000)
        compute_cubes(1000)
        random_sleep()
        factorial(500)
        string_manipulation(1000)
        file_io_operations("temp_file.txt", 100)


if __name__ == '__main__':
    main()