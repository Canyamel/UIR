import random
import psycopg2

def fill_feedback(connect, cursor, num_feedbacks, num_users):
    for _ in range(num_feedbacks):
        score = random.randint(1, 5)

        text = random.choice(texts)

        year = random.randint(2023, 2024)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        if month <= 9:
            if day <= 9:
                date_sending = str(year) + '-0' + str(month) + '-0' + str(day)
            else:
                date_sending = str(year) + '-0' + str(month) + '-' + str(day)
        else:
            if month <= 9:
                date_sending = str(year) + '-' + str(month) + '-0' + str(day)
            else:
                date_sending = str(year) + '-' + str(month) + '-' + str(day)

        id_user_writer = random.randint(1, num_users)
        id_user_seller = random.randint(1, num_users)
        while id_user_writer == id_user_seller:
            id_user_seller = random.randint(1, num_users)

        query = "INSERT INTO public.feedback (score, text, date_sending, id_user_writer, id_user_seller) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (score, text, date_sending, id_user_writer, id_user_seller))

    connect.commit()
    print(f"Таблица 'feedback' успешно заполнена {num_feedbacks} записями.")

def fill_feedback(connect, cursor, num_feedbacks, num_users):
    for _ in range(num_feedbacks):
        score = random.randint(1, 5)
        text = random.choice(texts)

        year = 2023
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        date_sending = datetime.date(year, month, day).strftime("%Y-%m-%d")

        id_user_writer = random.randint(1, num_users)
        id_user_seller = random.randint(1, num_users)

        while id_user_writer == id_user_seller:
            id_user_seller = random.randint(1, num_users)

        query = "INSERT INTO public.feedback (score, text, date_sending, id_user_writer, id_user_seller) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (score, text, date_sending, id_user_writer, id_user_seller))

    connect.commit()
    print(f"Таблица 'feedback' успешно заполнена {num_feedbacks} записями.")




host = "localhost"
dbname = "your_database_name"
user = "your_database_user"
password = "your_database_password"

conn = psycopg2.connect(host=host, database=dbname, user=user, password=password)
cursor = conn.cursor()

fill_user(conn, cursor, 50)  # Заполнить таблицу 'user' 50 записями
fill_feedback(conn, cursor, 100)  # Заполнить таблицу 'feedback' 100 записями
texts = ['312', 'fsdfds']
cursor.close()
conn.close()