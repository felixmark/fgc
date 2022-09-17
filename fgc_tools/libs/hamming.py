"""Code from https://github.com/LeonardoBringel/HammingCode

MIT License

Copyright (c) 2022 Leonardo Bringel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from .parity import *


def find_error(bits):
    error_index = []
    check_bits = calculate_parity(bits.copy())

    for index in range(len(bits)):
        if bits[index] != check_bits[index]:
            error_index.append(index)
    return error_index


def correct_error(bits, error_index):
    error_position = 0

    for index in error_index:
        error_position += index + 1
    bits[error_position - 1] = 0 if bits[error_position - 1] == 1 else 1
    return bits


def hamming_code(bits):
    bits = bits.copy()

    bits = insert_parity(bits)
    bits = calculate_parity(bits)
    return bits


def hamming_decode(bits):
    bits = bits.copy()
    error_index = find_error(bits)

    if len(error_index) != 0:
        bits = correct_error(bits, error_index)

    bits = remove_parity(bits)
    return bits
