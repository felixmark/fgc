import hamming_codec

def encode_data(data):
    bytes_data = data.encode("utf-8")

    # split the bytes into chunks of 8 bits (1 byte)
    #chunks = [bytes_data[i:i+1] for i in range(0, len(bytes_data), 1)]
    chunks = [bytes_data[i:i+1] for i in range(0, len(bytes_data),1)]

    # encode each chunk separately
    encoded_chunks = []
    for chunk in chunks:
        int_data = int.from_bytes(chunk, byteorder='big')
        binary = hamming_codec.encode(int_data, 8)
        encoded_chunks.append(binary)

    encoded_message = ''.join(encoded_chunks)
    return encoded_message

def encode_version(version):
    binary = hamming_codec.encode(version, 4)
    encoded_message = ''.join(binary)
    return encoded_message

def decode_data(encoded_data):
    chunks = [encoded_data[i:i+12] for i in range(0, len(encoded_data), 12)]

    # Decode each chunk separately
    decoded_chunks = []
    for chunk in chunks:
        decoded_chunk = int(hamming_codec.decode(int(chunk, 2), 12), 2)
        decoded_chunks.append(decoded_chunk)

    # Convert the decoded chunks back to bytes
    decoded_bytes = bytes(decoded_chunks)

    # Decode the bytes to string
    decoded_message = decoded_bytes.decode("utf-8")
    return decoded_message

def decode_version(encoded_data):
    version = int(hamming_codec.decode(int(encoded_data, 2), 7), 2)
    return version

if __name__ == '__main__':
    data = "A croissant: 🥐"
    encoded_data = encode_data(data)
    decoded_data = decode_data(encoded_data)
    print("Original data:", data)
    print("Encoded data: ", encoded_data)
    print("Decoded data: ", decoded_data)
