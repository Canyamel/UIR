from conllu import parse

from proc.func_file import *
from proc.rule_g import *
from proc.func_conllu import add_root_token

def transformation():
    name_file = input("Введите имя файла в папке tree (без формата): ")
    # name_file = "Arc_106103_1"
    # name_file = "test"

    data = read_file(f"conllu/tree/{name_file}.conllu")
    if data != None:
        sentences = parse(data.read())
        for i in range(len(sentences)):
            sentence = sentences[i]
            print(sentence.metadata)
            # add_root_token(sentence)
            bool_new_group = True
            # j = 0
            while bool_new_group:
                bool_new_group = False

                bool_new_group += rule_g_15_16(sentence)

                bool_new_group += rule_g_1(sentence)

                bool_new_group += rule_g_3(sentence)

                bool_new_group += rule_g_4(sentence)

                bool_new_group += rule_g_5(sentence)

                bool_new_group += rule_g_6(sentence)

                # j += 1
                # if j == 3:
                # bool_new_group = False

            # for token in sentence:
                # if token['deprel'] == '_' or token['deprel'] == None:
                #     if len(token['deps'][0][0]) > 2:
                #         token['deprel'] = token['deps'][0][0]
                # token['deps'] = None
                # token['deps'] = f"{token['head']}:{token['deprel']}"

    write_file(f"conllu/ssg/{name_file}.conllu", sentences)