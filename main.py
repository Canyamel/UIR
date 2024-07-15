from proc.transformation import transformation
from proc.search import search
from proc.upload import upload

def main():
    menu = ""
    while menu != "4":
        print("1. Трансформация ДП в ССГ")
        print("2. Поиск предложений")
        print("3. Загрузить предложение в банк")
        print("4. Выход")
        menu = input("Введите номер пункта: ")

        match menu:
            case "1":
                transformation()

            case "2":
                search()

            case "3":
                upload()

            case "4":
                pass

            case _:
                print("Данный пункт не существует")

if __name__ == '__main__':
    main()