def read_file(name_file):
    try:
        data = open(name_file, mode="r", encoding="utf-8")
    except FileNotFoundError:
        data = None
        print("Файл не существует")

    return data

def write_file(name_file, sentences):
    with open(name_file, mode="w", encoding="utf-8") as file:
        file.writelines([sentence.serialize() + "\n" for sentence in sentences])