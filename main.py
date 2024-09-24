import argparse
import random
import uuid
from io import BufferedReader
from typing import TextIO


def square_size(count: int = 256) -> int:
    """
    Рассчитывает минимальную сторону квадрата, способного вместить заданное количество букв

    :param count: количество символов
    :return: сторона квадрата
    """
    for i in range(20):
        if i * i >= count:
            return i
    raise Exception("Too many characters, square can not be calculated")


def generate_square(seed: str = "42", count: int = 256) -> list[list[int | None]]:
    """
    Генерирует квадрат Полибия, заполняя его буквами в случайном порядке

    :param seed: seed для использования Random
    :param count: количество буквами
    :return: случайно заполненный квадрат Полибия
    """
    size = square_size(count)
    indexes = []
    for row in range(size):
        for col in range(size):
            indexes.append((row, col))
    random.Random(seed).shuffle(indexes)
    square = [[None] * size for _ in range(size)]
    for i in range(count):
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


def bytes_to_str(val: bytes) -> str:
    """
    Перевод байт в строку с кодировкой Win-1251

    :param val: массив байт
    :return: строка
    """
    return val.decode('cp1251')


def decrypt(text: bytes, square: list[list[int | None]]) -> str:
    """
    Выполнение процесса дешифрации с использованием квадрата Полибия

    :param text: текст для дешифрации
    :param square: квадрат Полибия для дешифрации
    :return: дешифрованный текст
    """
    if len(text) % 4 != 0:
        raise Exception(f"Number of symbols must be divisible by 4")
    decrypted = []
    i = 0
    while i < len(text):
        row = bytes_to_str(text[i:i+2])
        col = bytes_to_str(text[i+2:i+4])
        if not row[0].isdigit() or not row[1].isdigit() or not col[0].isdigit() or not col[1].isdigit():
            raise Exception(f"Unexpected character {row} {col}")
        row = int(row)
        col = int(col)
        c = square[row][col]
        if c is None:
            raise Exception(f"Square cell ({row}, {col}) contains empty value")
        decrypted.append(bytes_to_str(c.to_bytes(1, 'big')))
        i += 4
    return "".join(decrypted)


def main(src: BufferedReader, dst: TextIO, mode: str, seed_file: TextIO) -> None:
    """
    Точка входа программы

    :param src: файл с исходным текстом
    :param dst: файл для записи результата программы
    :param mode: профиль действия программы (шифрация или дешифрация)
    :param seed_file: файл с seed для случайной генерации
    """
    source_text = src.read()
    src.close()

    seed = read_seed_file(seed_file)
    seed_file.close()

    square = generate_square(seed)

    if mode == "encrypt":
        result_text = encrypt(source_text, square)
    elif mode == "decrypt":
        result_text = decrypt(source_text, square)
    else:
        raise Exception(f"Unknown mode {mode}")

    dst.write(result_text)
    dst.close()


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
        "src", type=argparse.FileType("rb"), metavar="source_file", help="source file"
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="dst",
        type=argparse.FileType("w", encoding="cp1251"),
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
