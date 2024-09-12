## Information security lab work 1

### Описание

Реализовать в программе шифрование и дешифрацию файла с использованием [квадрата Полибия](https://en.wikipedia.org/wiki/Polybius_square), обеспечив его случайное заполнение.

### Использование

```text
usage: main.py [-h] [--mode prog_mode] [--encrypt] [--decrypt] [--output output_file] [--seed-file seed_file] source_file

Encrypt or decrypt file with Polybius square algorythm.

positional arguments:
  source_file           source file

options:
  -h, --help            show this help message and exit
  --mode prog_mode      set working mode to encrypt or decrypt (default: encrypt)
  --encrypt             manually set mode to encrypt
  --decrypt             manually set mode to decrypt
  --output output_file, -o output_file
                        file for storing result
  --seed-file seed_file
                        file with seed to be used with random
```
