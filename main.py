import argparse
import random
import uuid
from typing import TextIO


encrypt_characters = [
    'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и',
    'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т',
    'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь',
    'э', 'ю', 'я'
]

allowed_characters = [
    " ", "\n", "-", "—", "?", "!", ",", ".", ":", "«", "»"
]


def square_size() -> int:
    for i in range(10):
        if i * i >= len(encrypt_characters):
            return i
    raise Exception("Too many allowed characters, square can not be calculated")


def generate_square(key: str = "42") -> list[list[str | None]]:
    size = square_size()
    indexes = []
    for row in range(size):
        for col in range(size):
            indexes.append((row, col))
    random.Random(key).shuffle(indexes)
    square = [[None] * size for _ in range(size)]
    for i, c in enumerate(encrypt_characters):
        index = indexes[i]
        square[index[0]][index[1]] = c
    return square


def read_key_file(key_file: TextIO) -> str:
    key_file.seek(0)
    key = key_file.read()
    if len(key) == 0:
        key = uuid.uuid4().hex
        key_file.write(key)
    return key


def encrypt(text: str, square: list[list[str | None]]) -> str:
    coords = {}
    for row in range(len(square)):
        for col in range(len(square[0])):
            c = square[row][col]
            if c is not None:
                coords[c] = (row, col)
    text = text.lower()
    encrypted = []
    for c in text:
        if c in coords:
            coord = coords[c]
            encrypted.append(str(coord[0]) + str(coord[1]))
        elif c in allowed_characters:
            encrypted.append(c)
        else:
            raise Exception(f"Unexpected character {c}")
    return "".join(encrypted)


def decrypt(text: str, square: list[list[str | None]]) -> str:
    decrypted = []
    i = 0
    while i < len(text):
        c = text[i]
        if c.isdigit():
            row = int(c)
            col = int(text[i + 1])
            c = square[row][col]
            if c is None:
                raise Exception(f"Square cell ({row}, {col}) contains empty value")
            decrypted.append(c)
            i += 1
        elif c in allowed_characters:
            decrypted.append(c)
        else:
            raise Exception(f"Unexpected character {c}")
        i += 1
    return "".join(decrypted)


def main(src: TextIO, dst: TextIO, mode: str, key_file: TextIO):
    source_text = src.read()
    src.close()

    key = read_key_file(key_file)
    key_file.close()

    square = generate_square(key)

    if mode == "encrypt":
        result_text = encrypt(source_text, square)
    elif mode == "decrypt":
        result_text = decrypt(source_text, square)
    else:
        raise Exception(f"Unknown mode {mode}")

    dst.write(result_text)
    dst.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encrypt or decrypt file with Polybius square algorythm.")
    parser.add_argument(
        "--mode",
        default="encrypt",
        metavar="prog_mode",
        help="set working mode to encrypt or decrypt (default: encrypt)",
    )
    parser.add_argument(
        "--encrypt",
        dest="mode",
        action="store_const",
        const="encrypt",
        help="manually set mode to encrypt",
    )
    parser.add_argument(
        "--decrypt",
        dest="mode",
        action="store_const",
        const="decrypt",
        help="manually set mode to decrypt",
    )
    parser.add_argument(
        "src", type=argparse.FileType(encoding="utf-8"), metavar="source_file", help="source file"
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="dst",
        type=argparse.FileType("w", encoding="utf-8"),
        default="output.txt",
        metavar="output_file",
        help="file for storing result",
    )
    parser.add_argument(
        "--key-file",
        "-k",
        dest="key_file",
        type=argparse.FileType("a+", encoding="utf-8"),
        default="key.txt",
        metavar="key_file",
        help="file with key to be used in process",
    )
    ns = parser.parse_args()
    main(ns.src, ns.dst, ns.mode, ns.key_file)
