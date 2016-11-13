import re


def find_pattern(pattern, text):
    for k in range(len(text) // len(pattern)):
        for n in range(k):
            if pattern in text[n::k]:
                print("Found {pattern} with n={n}, k={k}.".format(pattern=pattern, n=n, k=k))
                return


def main():
    text_file = input("Enter file name:\n")
    with open(text_file, "r", encoding="utf-8") as f:
        text = f.read()

    stripped = (''.join(re.findall(r"[а-я]+", text.lower())))
    patterns = [
        "Абрам", "Александр", "Алексей", "Альберт", "Анатолий", "Андрей", "Антон", "Аркадий", "Арсений", "Артур",
        "Богдан", "Борис",
        "Никита", "Николай",
        "Павел", "Пётр"
    ]
    patterns = map(lambda x: x.lower(), patterns)
    for pattern in patterns:
        find_pattern(pattern, stripped)


if __name__ == '__main__':
    main()
