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


def parity_index(bits):
    bit_index = 2
    parity_location = [0]

    while bit_index < len(bits):
        parity_location.append(bit_index - 1)
        bit_index = bit_index * 2
    return parity_location


def parity_range(bits, interator):
    result = []
    next_bit = interator - 1
    cicle = interator

    for index, bit in enumerate(bits):
        if index == next_bit:

            if index not in parity_index(bits):
                result.append(index)
            cicle -= 1

            if cicle == 0:
                next_bit += interator + 1
                cicle = interator
            else:
                next_bit += 1
    return result


def parity(bits, interator):
    result = 0
    for index in parity_range(bits, interator):
        result += bits[index]
    return 0 if result % 2 == 0 else 1


def insert_parity(bits):
    for bit_index in parity_index(bits):
        bits.insert(bit_index, 0)
    return bits


def remove_parity(bits):
    result = []
    for index, bit in enumerate(bits):
        if index not in parity_index(bits):
            result.append(bit)
    return result


def calculate_parity(bits):
    for bit_index in parity_index(bits):
        bits[bit_index] = parity(bits, bit_index + 1)
    return bits
