from conllu import parse
import psycopg2

from proc.func_file import read_file

def upload():
    print("=======================================")
    name_file = input("Введите имя файла в папке ssg (без формата): ")

    data = read_file(f"conllu/ssg/{name_file}.conllu")
    sentences = parse(data.read())

    try:
        conn = psycopg2.connect(
            host="localhost",
            database="ssg_conllu",
            user="postgres",
            password="postgres"
        )

        for i in range(len(sentences)):
            print(i)
            sentence = sentences[i]

            cur = conn.cursor()
            str_insert = f"INSERT INTO sentence (sent_id) VALUES ('{sentence.metadata['sent_id']}')"
            cur.execute(str_insert)

            str_select = f"SELECT DISTINCT id_sentence FROM sentence ORDER BY id_sentence DESC LIMIT(1)"
            cur.execute(str_select)

            db_res = cur.fetchall()

            for token in sentence:
                if token['form'] == None or token['form'] == '_':
                    token_form = None
                else:
                    token_form = token['form']

                if token['lemma'] == None or token['lemma'] == '_':
                    token_lemma = None
                else:
                    token_lemma = token['lemma']

                if token['xpos'] == None or token['xpos'] == '_':
                    token_xpos = None
                else:
                    token_xpos = token['xpos']

                if token['feats'] == None or token['feats'] == '_':
                    token_feats = None
                else:
                    token_feats = list(token['feats'].keys())[0]

                if token['deprel'] == None or token['deprel'] == '_':
                    token_deprel = None
                else:
                    token_deprel = token['deprel']

                if token['deps'] == None or token['deps'] == '_':
                    token_deps = None
                else:
                    token_deps = token['deps']

                if token['misc'] == None or token['misc'] == '_':
                    token_misc = None
                else:
                    token_misc = token['misc']

                str_insert = f"INSERT INTO token (id_sentence, id, form, lemma, upos, xpos, feats, head, deprel, deps, misc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cur.execute(str_insert, (db_res[0][0], token['id'], token_form, token_lemma, token['upos'], token_xpos, token_feats, token['head'], token_deprel, token_deps, token_misc))

        conn.commit()

        cur.close()
        conn.close()

    except Exception as e:
        print(str(e))