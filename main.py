import argparse
import random
import uuid
from typing import TextIO


# Символы, которые БУДУТ зашифрованы
encrypt_characters = [
    'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и',
    'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т',
    'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь',
    'э', 'ю', 'я',
]

# Допустимые символы, которые НЕ БУДУТ зашифрованы
allowed_characters = [
    " ", "\n", "-", "—", "?", "!", ",", ".", ":", "«", "»",
]


def square_size(count: int = len(encrypt_characters)) -> int:
    """
    Рассчитывает минимальную сторону квадрата, способного вместить заданное количество букв

    :param count: количество букв
    :return: сторона квадрата
    """
    for i in range(10):
        if i * i >= count:
            return i
    raise Exception("Too many characters, square can not be calculated")


def generate_square(seed: str = "42") -> list[list[str | None]]:
    """
    Генерирует квадрат Полибия, заполняя его буквами в случайном порядке

    :param seed: seed для использования Random
    :return: случайно заполненный квадрат Полибия
    """
    size = square_size()
    indexes = []
    for row in range(size):
        for col in range(size):
            indexes.append((row, col))
    random.Random(seed).shuffle(indexes)
    square = [[None] * size for _ in range(size)]
    for i, c in enumerate(encrypt_characters):
        index = indexes[i]
        square[index[0]][index[1]] = c
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


def encrypt(text: str, square: list[list[str | None]]) -> str:
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
    """
    Выполнение процесса дешифрации с использованием квадрата Полибия

    :param text: текст для дешифрации
    :param square: квадрат Полибия для дешифрации
    :return: дешифрованный текст
    """
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


def main(src: TextIO, dst: TextIO, mode: str, seed_file: TextIO) -> None:
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
