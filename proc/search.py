import psycopg2

from proc.func import is_int

def search():
        print("=======================================")
        print("1. Поиск точных форм")
        print("2. Поиск по подкритерию")
        print("3. Поиск по характеристикам")

        menu = input("Введите номер пункта: ")

        match menu:
                case "1":
                    try:
                        conn = psycopg2.connect(
                            host="localhost",
                            database="ssg_conllu",
                            user="postgres",
                            password="postgres"
                        )

                        print("=======================================")
                        text = input("Введите слово/словосочетание: ")
                        #form = "ОдНой по"

                        cur = conn.cursor()

                        cur.execute(f"SELECT DISTINCT id_sentence FROM token WHERE REGEXP_REPLACE(concat(' ', LOWER(upos)), '[[:punct:]]', '', 'g') LIKE LOWER('% {text} %')")

                        conn.commit()

                        db_res = cur.fetchall()

                        if db_res == []:
                            print('Ничего не найдено')
                            cur.close()
                            conn.close()
                        else:
                            print(f"Кол-во найденных предложений: {len(db_res)}")
                            file_name = input("Введите имя файла (без формата и без пути): ")
                            with open(f"conllu/ssg/{file_name}.conllu", mode="w", encoding="utf-8") as file:
                                cur = conn.cursor()
                                for row in db_res:
                                    cur.execute(f"SELECT sent_id FROM sentence WHERE id_sentence = {row[0]}")
                                    conn.commit()
                                    db_res_w = cur.fetchall()
                                    file.writelines(f"# sent_id = {db_res_w[0][0]}\n")

                                    cur.execute(f"SELECT id, form, lemma, upos, xpos, feats, head, deprel, deps, misc FROM token WHERE id_sentence = {row[0]} ORDER BY id")
                                    conn.commit()
                                    db_res_w = cur.fetchall()
                                    for row_w in db_res_w:
                                        str = ""
                                        for attr in row_w:
                                            if attr == None:
                                                attr = '_'
                                            str += f"{attr}	"
                                        str = str[:-1]
                                        file.writelines(f'{str}\n')
                                    file.writelines('\n')

                                cur.close()
                                conn.close()
                    except Exception as e:
                        print(str(e))

                case "2":
                    try:
                        conn = psycopg2.connect(
                            host="localhost",
                            database="ssg_conllu",
                            user="postgres",
                            password="postgres"
                        )

                        print("=======================================")
                        xpos = input("Введите критерий: ")

                        cur = conn.cursor()

                        cur.execute(f"SELECT DISTINCT id_sentence FROM token WHERE LOWER(xpos) = LOWER('{xpos}')")

                        conn.commit()

                        db_res = cur.fetchall()

                        if db_res == []:
                            print('Ничего не найдено')
                            cur.close()
                            conn.close()
                        else:
                            print(f"Кол-во найденных предложений: {len(db_res)}")
                            file_name = input("Введите имя файла (без формата и без пути): ")
                            with open(f"conllu/ssg/{file_name}.conllu", mode="w", encoding="utf-8") as file:
                                cur = conn.cursor()
                                for row in db_res:
                                    cur.execute(f"SELECT sent_id FROM sentence WHERE id_sentence = {row[0]}")
                                    conn.commit()
                                    db_res_w = cur.fetchall()
                                    file.writelines(f"# sent_id = {db_res_w[0][0]}\n")

                                    cur.execute(f"SELECT id, form, lemma, upos, xpos, feats, head, deprel, deps, misc FROM token WHERE id_sentence = {row[0]} ORDER BY id")
                                    conn.commit()
                                    db_res_w = cur.fetchall()
                                    for row_w in db_res_w:
                                        str = ""
                                        for attr in row_w:
                                            if attr == None:
                                                attr = '_'
                                            str += f"{attr}	"
                                        str = str[:-1]
                                        file.writelines(f'{str}\n')
                                    file.writelines('\n')

                                cur.close()
                                conn.close()
                    except Exception as e:
                        print(str(e))

                case "3":
                    try:
                        conn = psycopg2.connect(
                            host="localhost",
                            database="ssg_conllu",
                            user="postgres",
                            password="postgres"
                        )

                        qnt = input("Введите количество слов или словосочетаний, по которым будет вестись поиск: ")
                        print("=======================================")
                        if is_int(qnt):
                            int_qnt = int(qnt)
                            if int_qnt > 0:
                                #os.system('cls')
                                for i in range(int_qnt):
                                    if i == 0:
                                        str_select = f"WITH t{i+1} AS("
                                    else:
                                        str_select += f", t{i+1} AS("
                                    lemma = None
                                    form = None
                                    feats = None
                                    xpos = None
                                    upos = None
                                    head = None
                                    deprel = None
                                    menu = 0
                                    bool_where = False
                                    bool_join = False
                                    print("1. Слово")
                                    print("2. Словосочетание")
                                    menu = input(f"Введите номер пункта для {i+1}-ого слова/словосочетания: ")
                                    print("=======================================")
                                    match menu:
                                        case "1":
                                            while menu != "7":
                                                print("1. Лемма")
                                                print("2. Словоформа")
                                                print("3. Морфологические признаки")
                                                print("4. Синтаксическое отношение")
                                                print("5. Подчинение к прошлым словам/словосочетаниям")
                                                print("6. Посмотреть текущие ограничения")
                                                print("7. Перейти к следующему слову/словосочетанию")
                                                menu = input(f"Введите номер пункта для {i+1}-ого слова: ")

                                                match menu:
                                                    case "1":
                                                        lemma = input(f"Введите лемму (лемму и логический оператор \"|\" писать через пробел): ")
                                                        bool_where = True

                                                    case "2":
                                                        form = input(f"Введите словоформу: ")
                                                        bool_where = True

                                                    case "3":
                                                        feats = input(f"Введите морфологический признак (морфологические признаки, логические операторы \"|\", \"&\" и скобки писать через пробел): ")
                                                        bool_where = True

                                                    case "4":
                                                        deprel = input(f"Введите синтаксическое отношение (синтаксические отношения и логический оператор \"|\" писать через пробел):  ")
                                                        bool_where = True

                                                    case "5":
                                                        if i == 0:
                                                            print(f"Ошибка: первое слово/словосочетание не может зависить от других")
                                                        else:
                                                            head = input(f"Введите номер слова/словосочетаниния: ")
                                                            if is_int(head):
                                                                head = int(head)
                                                                if head <= 0 or head == i+1:
                                                                    print(f"Ошибка: введено не натуральное число или введено число данного слова/словосочетания")
                                                                    head = None
                                                                else:
                                                                    bool_join = True
                                                            else:
                                                                print(f"Ошибка: введено не натуральное число")
                                                                head = None

                                                    case "6":
                                                        print(f"Лемма: {lemma}")
                                                        print(f"Словоформа: {form}")
                                                        print(f"Морфологические признаки: {feats}")
                                                        print(f"Синтаксическое отношение: {deprel}")
                                                        print(f"Зависит от {head}-ого слова/словосочетания")

                                                    case "7":
                                                        if not bool_where and not bool_join:
                                                            print("Ошибка: нет ограничений")
                                                            menu = 0
                                                        else:
                                                            if bool_join:
                                                                if head != None:
                                                                    str_select += f"SELECT t{i+1}.* FROM token t{i+1} JOIN t{head} ON t{i+1}.head = t{head}.id "
                                                            else:
                                                                str_select += f"SELECT t{i+1}.* FROM token t{i+1} "

                                                            if bool_where:
                                                                str_select += f"WHERE "

                                                                if lemma != None:
                                                                    lemma = lemma.split()
                                                                    str_select += "( "
                                                                    for i_lemma in lemma:
                                                                        if i_lemma == "|":
                                                                            str_select += "OR "
                                                                        else:
                                                                            str_select += f"LOWER(t{i+1}.lemma) = LOWER('{i_lemma}') "
                                                                    str_select += ") AND "

                                                                if form != None:
                                                                    str_select += f"REGEXP_REPLACE(concat(' ', LOWER(t{i+1}.form)), '[[:punct:]]', '', 'g') LIKE LOWER('% {form} %') AND "

                                                                if feats != None:
                                                                    feats = feats.split()
                                                                    str_select += "( "
                                                                    for i_feat in feats:
                                                                        match i_feat:
                                                                            case "(":
                                                                                str_select += "( "
                                                                            case ")":
                                                                                str_select += ") "
                                                                            case "&":
                                                                                str_select += "AND "
                                                                            case "|":
                                                                                str_select += "OR "
                                                                            case "ОД":
                                                                                str_select += f"LOWER(t{i+1}.feats) LIKE LOWER('%{i_feat}%') AND LOWER(t{i+1}.feats) NOT LIKE LOWER('%НЕОД%') "
                                                                            case "ПРОШ":
                                                                                str_select += f"LOWER(t{i+1}.feats) LIKE LOWER('%{i_feat}%') AND LOWER(t{i+1}.feats) NOT LIKE LOWER('%НЕПРОШ%') "
                                                                            case "СОВ":
                                                                                str_select += f"LOWER(t{i+1}.feats) LIKE LOWER('%{i_feat}%') AND LOWER(t{i+1}.feats) NOT LIKE LOWER('%НЕСОВ%') "
                                                                            case _:
                                                                                str_select += f"LOWER(t{i+1}.feats) LIKE LOWER('%{i_feat}%') "
                                                                    str_select += ") AND "

                                                                if deprel != None:
                                                                    deprel = deprel.split()
                                                                    str_select += "( "
                                                                    for i_deprel in deprel:
                                                                        if i_deprel == "|":
                                                                            str_select += "OR "
                                                                        else:
                                                                            str_select += f"LOWER(t{i+1}.deprel) = LOWER('{i_deprel}') "
                                                                    str_select += ") AND "

                                                                if str_select[-5:] == " AND ":
                                                                    str_select = str_select[:-5]

                                                            str_select += ")"
                                                            #print(str_select)

                                        case "2":
                                            while menu != "6":
                                                print("1. Точная форма")
                                                print("2. Критерий")
                                                print("3. Синтаксическое отношение")
                                                print("4. Подчинение к прошлым словам/словосочетаниям")
                                                print("5. Посмотреть текущие ограничения")
                                                print("6. Перейти к следующему слову")
                                                menu = input(f"Введите номер пункта для {i+1}-ого словосочетания: ")

                                                match menu:
                                                    case "1":
                                                        upos = input(f"Введите точную форму: ")
                                                        bool_where = True

                                                    case "2":
                                                        xpos = input(f"Введите критерий (критерии и логический оператор \"|\" писать через пробел): ")
                                                        bool_where = True

                                                    case "3":
                                                        deprel = input(f"Введите синтаксическое отношение (синтаксические отношения и логический оператор \"|\" писать через пробел):  ")
                                                        bool_where = True

                                                    case "4":
                                                        if i == 0:
                                                            print(f"Ошибка: первое слово/словосочетание не может зависить от других")
                                                        else:
                                                            head = input(f"Введите номер слова/словосочетаниния: ")
                                                            if is_int(head):
                                                                head = int(head)
                                                                if head <= 0 or head == i+1:
                                                                    print(f"Ошибка: введено не натуральное число или введено число данного слова/словосочетания")
                                                                    head = None
                                                                else:
                                                                    bool_join = True
                                                            else:
                                                                print(f"Ошибка: введено не натуральное число")
                                                                head = None

                                                    case "5":
                                                        print(f"Точная форма: {upos}")
                                                        print(f"Критерий: {xpos}")
                                                        print(f"Синтаксическое отношение: {deprel}")
                                                        print(f"Зависит от {head}-ого слова/словосочетания")

                                                    case "6":
                                                        if not bool_where and not bool_join:
                                                            print("Ошибка: нет ограничений")
                                                            menu = 0
                                                        else:
                                                            if bool_join:
                                                                if head != None:
                                                                    str_select += f"SELECT t{i+1}.* FROM token t{i+1} JOIN t{head} ON t{i+1}.head = t{head}.id "
                                                            else:
                                                                str_select += f"SELECT t{i+1}.* FROM token t{i+1} "

                                                            if bool_where:
                                                                str_select += f"WHERE "

                                                                if upos != None:
                                                                    str_select += f"REGEXP_REPLACE(concat(' ', LOWER(t{i+1}.upos)), '[[:punct:]]', '', 'g') LIKE LOWER('% {upos} %') AND "

                                                                if xpos != None:
                                                                    xpos = xpos.split()
                                                                    str_select += "( "
                                                                    for i_xpos in xpos:
                                                                        if i_xpos == "|":
                                                                            str_select += "OR "
                                                                        else:
                                                                            str_select += f"LOWER(t{i+1}.xpos) = LOWER('{i_xpos}') "
                                                                    str_select += ") AND "

                                                                if deprel != None:
                                                                    deprel = deprel.split()
                                                                    str_select += "( "
                                                                    for i_deprel in deprel:
                                                                        if i_deprel == "|":
                                                                            str_select += "OR "
                                                                        else:
                                                                            str_select += f"LOWER(t{i+1}.deprel) = LOWER('{i_deprel}') "
                                                                    str_select += ") AND "

                                                                if str_select[-5:] == " AND ":
                                                                    str_select = str_select[:-5]

                                                            str_select += ")"
                                                            #print(str_select)

                                        case _:
                                            print("Ошибка: нет данного пункта")

                            str_select += f" SELECT DISTINCT s.sent_id, s.id_sentence FROM sentence s "
                            for i in range(int_qnt):
                                str_select += f"JOIN t{i+1} ON s.id_sentence = t{i+1}.id_sentence "
                            #print(str_select)
                        else:
                            print('Ошибка: введено не натуральное число')

                        cur = conn.cursor()

                        cur.execute(str_select)

                        conn.commit()

                        db_res = cur.fetchall()
                        #print(str_select)
                        if db_res == []:
                            print('Ничего не найдено')
                            cur.close()
                            conn.close()
                        else:
                            print(f"Кол-во найденных предложений: {len(db_res)}")
                            file_name = input("Введите имя файла (без формата и без пути): ")
                            with open(f"conllu/ssg/{file_name}.conllu", mode="w", encoding="utf-8") as file:
                                cur = conn.cursor()
                                for row in db_res:
                                    file.writelines(f"# sent_id = {row[0]}\n")

                                    cur.execute(f"SELECT id, form, lemma, upos, xpos, feats, head, deprel, deps, misc FROM token WHERE id_sentence = {row[1]} ORDER BY id")
                                    conn.commit()
                                    db_res_w = cur.fetchall()
                                    for row_w in db_res_w:
                                        str = ""
                                        for attr in row_w:
                                            if attr == None:
                                                attr = '_'
                                            str += f"{attr}	"
                                        str = str[:-1]
                                        file.writelines(f'{str}\n')
                                    file.writelines('\n')

                                cur.close()
                                conn.close()
                    except Exception as e:
                        print(str(e))

                case _:
                    print("Такого пунтка нет")