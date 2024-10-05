import argparse
import random
import uuid
from typing import TextIO


def generate_square(seed: str = "42") -> list[list[int | None]]:
    """
    Генерирует квадрат Полибия, заполняя его буквами в случайном порядке

    :param seed: seed для использования Random
    :return: случайно заполненный квадрат Полибия
    """
    size = 16
    indexes = []
    for row in range(size):
        for col in range(size):
            indexes.append((row, col))
    random.Random(seed).shuffle(indexes)
    square = [[None] * size for _ in range(size)]
    for i in range(size * size):
        index = indexes[i]
        square[index[0]][index[1]] = i
    return square


def read_seed_file(seed_file: TextIO) -> str:
    """
    Читает seed из файла (создает новый если файла нет или он пустой)

    :param seed_file: файл, содержащий seed
    :return: прочитанный seed (или сгенерированный, если файл пустой или отсутствует)
    """
    seed_file.seek(0)
    seed = seed_file.read()
    if len(seed) == 0:
        seed = uuid.uuid4().hex
        seed_file.write(seed)
    return seed


def int_to_str(val: int, digits: int = 2) -> str:
    """
    Перевод числа в строку с добавлением ведущих нулей

    :param val: число для перевода
    :param digits: количество символов в итоговой строке
    :return: число в виде строки
    """
    res = ""
    while digits > 0:
        res += str(val % 10)
        val //= 10
        digits -= 1
    return res[::-1]


def encrypt(text: bytes, square: list[list[int | None]]) -> str:
    """
    Выполнение процесса шифрования с использованием квадрата Полибия

    :param text: текст для шифрования
    :param square: квадрат Полибия для шифрования
    :return: зашифрованный текст
    """
    coords = {}
    for row in range(len(square)):
        for col in range(len(square[0])):
            c = square[row][col]
            if c is not None:
                coords[c] = (row, col)
    encrypted = []
    for c in text:
        if c not in coords:
            raise Exception(f"Unexpected character {c}")
        coord = coords[c]
        encrypted.append(int_to_str(coord[0]) + int_to_str(coord[1]))
    return "".join(encrypted)


def str_to_int(text: str) -> int:
    """
    Перевод строки с ведущими нулями в число

    :param text: строка для перевода
    :return: число
    """
    for c in text:
        if not c.isdigit():
            raise Exception(f"Expect digit but found {c}")
    return int(text)


def decrypt(text: str, square: list[list[int | None]], digit_width: int = 2) -> bytes:
    """
    Выполнение процесса дешифрации с использованием квадрата Полибия

    :param text: текст для дешифрации
    :param square: квадрат Полибия для дешифрации
    :param digit_width: длина числа в символах (с ведущими нулями)
    :return: дешифрованный текст
    """
    if len(text) % (digit_width * 2) != 0:
        raise Exception(f"Number of symbols must be divisible by {digit_width * 2}")
    decrypted = []
    i = 0
    while i < len(text):
        row = str_to_int(text[i:i+digit_width])
        i += digit_width
        col = str_to_int(text[i:i+digit_width])
        i += digit_width
        c = square[row][col]
        if c is None:
            raise Exception(f"Square cell ({row}, {col}) contains empty value")
        decrypted.append(c.to_bytes(1, 'big'))
    return b"".join(decrypted)


def main(src: str, dst: str, mode: str, seed_file: TextIO) -> None:
    """
    Точка входа программы

    :param src: файл с исходным текстом
    :param dst: файл для записи результата программы
    :param mode: профиль действия программы (шифрация или дешифрация)
    :param seed_file: файл с seed для случайной генерации
    """
    seed = read_seed_file(seed_file)
    seed_file.close()

    square = generate_square(seed)

    if mode == "encrypt":
        with open(src, "rb") as f:
            src_bytes = f.read()
        result_text = encrypt(src_bytes, square)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(result_text)
    elif mode == "decrypt":
        with open(src, "r", encoding="utf-8") as f:
            src_text = f.read()
        result_bytes = decrypt(src_text, square)
        with open(dst, "wb") as f:
            f.write(result_bytes)
    else:
        raise Exception(f"Unknown mode {mode}")


if __name__ == "__main__":
    """
    Считывание параметров командной строки, их валидация и передача в main-метод
    """
    parser = argparse.ArgumentParser(description="Encrypt or decrypt file with Polybius square algorythm.")
    parser.add_argument(
        "--mode",
        default="encrypt",
        metavar="prog_mode",
        help="set working mode to encrypt or decrypt (default: encrypt)",
    )
    parser.add_argument(
        "--encrypt",
        "-e",
        dest="mode",
        action="store_const",
        const="encrypt",
        help="manually set mode to encrypt",
    )
    parser.add_argument(
        "--decrypt",
        "-d",
        dest="mode",
        action="store_const",
        const="decrypt",
        help="manually set mode to decrypt",
    )
    parser.add_argument(
        "src", metavar="source_file", help="source file"
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="dst",
        default="output.txt",
        metavar="output_file",
        help="file for storing result",
    )
    parser.add_argument(
        "--seed-file",
        "-s",
        dest="seed_file",
        type=argparse.FileType("a+", encoding="utf-8"),
        default="seed.txt",
        metavar="seed_file",
        help="file with seed to be used with random",
    )
    ns = parser.parse_args()
    main(ns.src, ns.dst, ns.mode, ns.seed_file)
