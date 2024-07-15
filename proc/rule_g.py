from conllu.models import TokenList
import json

from proc.func_conllu import *

def rule_g_1(sentence: TokenList):
    for head_token in sentence:
        bool_new_group = False
        if (head_token['xpos'] != 'Г1' or sentence[head_token['head'] - 1]['xpos'] != 'Г1' and head_token['deprel'] == '_') and head_token['id'] != 1:

            lemma = head_token['lemma']
            if lemma == '_':
                group_component_sg = get_group_component_sg(head_token, sentence)
                if len(group_component_sg) == 2:
                    for token in group_component_sg:
                        if token['head'] == head_token['id'] and token['deprel'] == '_' and token['upos'] != 'ADP':
                            lemma = token['lemma']
                            break
                else:
                    root_component = get_root_component_sg(head_token, sentence)
                    if root_component != None:
                        lemma = get_root_component_sg(head_token, sentence)['lemma']
                    else:
                        continue

            group_child_token = get_group_one_step_child_token(head_token, sentence)
            if len(group_child_token) > 0:
                with open("wordbook.json", "r", encoding="utf-8") as json_file:
                    wordbook = json.load(json_file)
                for word in wordbook['words']:
                    if word['lemma'] == lemma.lower():
                        for child_token in group_child_token:
                            for magn in word['magn']:
                                if magn == child_token['lemma'].lower():
                                    bool_new_group = True
                                    break

            if bool_new_group:
                group_token = [head_token]
                for token in get_group_one_step_child_token(head_token, sentence):
                    group_token.extend(get_token_for_group(token, sentence))

                buf_group_token = group_token.copy()
                for token in buf_group_token:
                    if token['lemma'] == '_':
                        group_token.remove(token)
                        group_token.extend(get_group_component_sg(token, sentence))
                group_token.sort(key=lambda token: token['id'])
                phrase = ''
                for token in group_token:
                    phrase += token['form'] + ' '
                phrase = phrase[:-1]
                group_token = buf_group_token.copy()

                list_one_step_children_token = []
                for token in group_token:
                    list_one_step_children_token.extend(get_group_one_step_child_token(token, sentence))

                # Добавить новую группу и изменить связи между элементами ССГ
                for token in list_one_step_children_token:
                    if token not in group_token:
                        token['head'] = len(sentence) + 1
                sentence.append(create_sg(len(sentence) + 1, phrase, 'Г1', head_token['head'], head_token['deprel']))
                head_token['deprel'] = '_'
                head_token['head'] = len(sentence)

    return bool_new_group

# ==========================================================

def rule_g_3(sentence: TokenList):
    bool_new_group = False
    for token in sentence:
        # поиск ГЛ, который не является ИНФ
        if token['upos'] == 'VERB' and not check_feat(token, 'ИНФ'):
            head_token = token
            while head_token['deprel'] == '_' and head_token['head'] != 1 and sentence[head_token['head'] - 1]['xpos'] not in ['Г15', 'Г16']:
                head_token = sentence[head_token['head'] - 1]

            if head_token['xpos'] != 'Г3' or sentence[token['head'] - 1]['xpos'] != 'Г3' and head_token['deprel'] == '_':
                # поиск ИНФ, который зависит от найденного слова
                for token in get_group_one_step_child_token(head_token, sentence):
                    buf_token = token
                    if buf_token['lemma'] == '_' and buf_token['form'] == '_' and buf_token['xpos'] not in ['Г3', 'Г4', 'Г5', 'Г6', 'Г7', 'Г8', 'Г15', 'Г16']:
                        buf_token = get_root_component_sg(buf_token, sentence)
                    if  check_feat(buf_token, 'ИНФ'):
                        inf_token = token

                        # Поиск двух наборов пар связей (в первой все связи, в которых отсуствует найденный СУЩ, а во второй - присуствует)
                        pairs = get_sorted_pairs(sentence)
                        inf_pairs = []
                        buf_pairs = pairs.copy()
                        if inf_token['lemma'] == '_' and inf_token['form'] == '_':
                            id_inf_token = get_root_component_sg(inf_token, sentence)['id']
                            id_child_token = None
                            for token in sentence:
                                if token['head'] == id_inf_token:
                                    id_child_token = token['id']
                                    break
                            for pair in buf_pairs:
                                if id_child_token != None:
                                    if id_inf_token in pair and get_id_head_token(inf_token, sentence) not in pair and id_child_token not in pair:
                                        inf_pairs.append(pair)
                                        pairs.remove(pair)
                        else:
                            id_inf_token = inf_token['id']
                            for pair in buf_pairs:
                                if id_inf_token in pair and get_id_head_token(inf_token, sentence) not in pair:
                                    inf_pairs.append(pair)
                                    pairs.remove(pair)

                        # Проверить, что существуют пары с ИНФ
                        qnt_inf_pairs = len(inf_pairs)
                        if qnt_inf_pairs > 0:

                            # Удалить все пары с ИНФ, которые нарушают проективность
                            buf_inf_pairs = inf_pairs.copy()
                            for inf_pair in buf_inf_pairs:
                                if get_id_head_token(inf_token, sentence) > inf_pair[0] and get_id_head_token(inf_token, sentence) < inf_pair[1]:
                                    inf_pairs.remove(inf_pair)
                                    continue
                                for pair in pairs:
                                    if (inf_pair[0] > pair[0] and inf_pair[0] < pair[1] and (inf_pair[1] < pair[0] or inf_pair[1] > pair[1])) or (inf_pair[1] > pair[0] and inf_pair[1] < pair[1] and (inf_pair[0] < pair[0] or inf_pair[0] > pair[1])):
                                        inf_pairs.remove(inf_pair)
                                        break

                            # Проверка, что нужно добавлять новую группу
                            if qnt_inf_pairs > len(inf_pairs):
                                bool_new_group = True

                                # Получить набор слов, которые образуют новую группу
                                group_token = [head_token, inf_token]
                                # for pair in inf_pairs:
                                #     if pair[0] != inf_token['id']:
                                #         token = sentence[pair[0] - 1]
                                #     else:
                                #         token = sentence[pair[1] - 1]
                                #     group_token.extend(get_token_for_group(token, sentence))

                                # Получить словосочетание
                                buf_group_token = group_token.copy()
                                for token in buf_group_token:
                                    if token['lemma'] == '_' and token['form'] == '_':
                                        group_token.remove(token)
                                        group_token.extend(get_group_component_sg(token, sentence))
                                group_token.sort(key=lambda token: token['id'])
                                phrase = ''
                                for token in group_token:
                                    phrase += token['form'] + ' '
                                phrase = phrase[:-1]
                                group_token = buf_group_token.copy()

                                # Получить все слова, которые связаны со словами из группы
                                group_one_step_child_token = []
                                for token in group_token:
                                    for child_token in get_group_one_step_child_token(token, sentence):
                                        if child_token not in group_token:
                                            group_one_step_child_token.extend(get_group_one_step_child_token(token, sentence))

                                # Добавить новую группу и изменить связи между элементами ССГ
                                for token in group_one_step_child_token:
                                    if token not in group_token:
                                        token['head'] = len(sentence) + 1
                                sentence.append(create_sg(len(sentence) + 1, phrase, 'Г3', head_token['head'], head_token['deprel']))
                                head_token['deprel'] = '_'
                                head_token['head'] = len(sentence)
    return bool_new_group

# ===========================================================================

def rule_g_4(sentence: TokenList):
    bool_new_group = False
    for token in sentence:
        # поиск ГЛ, который не является ИНФ
        if token['upos'] in ['NOUN', 'ADJ', 'ADV']:
            head_token = token
            while head_token['deprel'] == '_' and head_token['head'] != 1 and sentence[head_token['head'] - 1]['xpos'] not in ['Г15', 'Г16']:
                head_token = sentence[head_token['head'] - 1]

            if head_token['xpos'] != 'Г4' or sentence[token['head'] - 1]['xpos'] != 'Г4' and head_token['deprel'] == '_':
                # поиск ИНФ, который зависит от найденного слова
                for token in get_group_one_step_child_token(head_token, sentence):
                    buf_token = token
                    if buf_token['lemma'] == '_' and buf_token['form'] == '_' and buf_token['xpos'] not in ['Г3', 'Г4', 'Г5', 'Г6', 'Г7', 'Г8', 'Г15', 'Г16']:
                        buf_token = get_root_component_sg(buf_token, sentence)
                    if  check_feat(buf_token, 'ИНФ'):
                        inf_token = token

                        # Поиск двух наборов пар связей (в первой все связи, в которых отсуствует найденный СУЩ, а во второй - присуствует)
                        pairs = get_sorted_pairs(sentence)
                        inf_pairs = []
                        buf_pairs = pairs.copy()
                        if inf_token['lemma'] == '_' and inf_token['form'] == '_':
                            id_inf_token = get_root_component_sg(inf_token, sentence)['id']
                            id_child_token = None
                            for token in sentence:
                                if token['head'] == id_inf_token:
                                    id_child_token = token['id']
                                    break
                            for pair in buf_pairs:
                                if id_child_token != None:
                                    if id_inf_token in pair and get_id_head_token(inf_token, sentence) not in pair and id_child_token not in pair:
                                        inf_pairs.append(pair)
                                        pairs.remove(pair)
                        else:
                            id_inf_token = inf_token['id']
                            for pair in buf_pairs:
                                if id_inf_token in pair and get_id_head_token(inf_token, sentence) not in pair:
                                    inf_pairs.append(pair)
                                    pairs.remove(pair)

                        # Проверить, что существуют пары с ИНФ
                        qnt_inf_pairs = len(inf_pairs)
                        if qnt_inf_pairs > 0:

                            # Удалить все пары с ИНФ, которые нарушают проективность
                            buf_inf_pairs = inf_pairs.copy()
                            for inf_pair in buf_inf_pairs:
                                if get_id_head_token(inf_token, sentence) > inf_pair[0] and get_id_head_token(inf_token, sentence) < inf_pair[1]:
                                    inf_pairs.remove(inf_pair)
                                    continue
                                for pair in pairs:
                                    if (inf_pair[0] > pair[0] and inf_pair[0] < pair[1] and (inf_pair[1] < pair[0] or inf_pair[1] > pair[1])) or (inf_pair[1] > pair[0] and inf_pair[1] < pair[1] and (inf_pair[0] < pair[0] or inf_pair[0] > pair[1])):
                                        inf_pairs.remove(inf_pair)
                                        break

                            # Проверка, что нужно добавлять новую группу
                            if qnt_inf_pairs > len(inf_pairs):
                                bool_new_group = True

                                # Получить набор слов, которые образуют новую группу
                                group_token = [head_token, inf_token]
                                # for pair in inf_pairs:
                                #     if pair[0] != inf_token['id']:
                                #         token = sentence[pair[0] - 1]
                                #     else:
                                #         token = sentence[pair[1] - 1]
                                #     group_token.extend(get_token_for_group(token, sentence))

                                # Получить словосочетание
                                buf_group_token = group_token.copy()
                                for token in buf_group_token:
                                    if token['lemma'] == '_' and token['form'] == '_':
                                        group_token.remove(token)
                                        group_token.extend(get_group_component_sg(token, sentence))
                                group_token.sort(key=lambda token: token['id'])
                                phrase = ''
                                for token in group_token:
                                    phrase += token['form'] + ' '
                                phrase = phrase[:-1]
                                group_token = buf_group_token.copy()

                                # Получить все слова, которые связаны со словами из группы
                                group_one_step_child_token = []
                                for token in group_token:
                                    for child_token in get_group_one_step_child_token(token, sentence):
                                        if child_token not in group_token:
                                            group_one_step_child_token.extend(get_group_one_step_child_token(token, sentence))

                                # Добавить новую группу и изменить связи между элементами ССГ
                                for token in group_one_step_child_token:
                                    if token not in group_token:
                                        token['head'] = len(sentence) + 1
                                sentence.append(create_sg(len(sentence) + 1, phrase, 'Г4', head_token['head'], head_token['deprel']))
                                head_token['deprel'] = '_'
                                head_token['head'] = len(sentence)
    return bool_new_group

# ===========================================================================

def rule_g_5(sentence: TokenList):
    bool_new_group = False
    for token in sentence:
        # Поиск ИНФ, который не завист от другого ИНФ
        if check_feat(token, 'ИНФ') and not check_feat(sentence[token['head'] - 1], 'ИНФ'):
            head_token = token
            last_inf_token = token
            while head_token['deprel'] == '_' and head_token['head'] != 1:
                head_token = sentence[head_token['head'] - 1]

            group_token = [head_token]
            inf_group_token = [head_token]
            bool_N = False
            while True:
                if head_token['head'] == 1:
                    break

                buf_head_token = sentence[head_token['head'] - 1]

                if buf_head_token['xpos'] in ['Г3', 'Г4', 'Г5', 'Г6', 'Г7', 'Г8', 'Г15', 'Г16']:
                    break

                if buf_head_token['deprel'] in ['сент-соч', 'кратн', 'релят', 'разъяснит', 'примыкат', 'подч-союзн', 'инф-союзн', 'сравн-союзн', 'сравнит', 'эксплет']:
                    break

                if buf_head_token['lemma'] == '_' and buf_head_token['form'] == '_':
                    buf_head_token = get_root_component_sg(buf_head_token, sentence)
                    if buf_head_token == None:
                        break

                if buf_head_token['id'] > head_token['id']:
                    break

                if buf_head_token['upos'] in ['VERB', 'NOUN', 'ADJ', 'ADV']:
                    if buf_head_token['upos'] in ['NOUN', 'ADJ', 'ADV']:
                        if bool_N:
                            break
                        bool_N = True
                    head_token = sentence[head_token['head'] - 1]
                    group_token.append(head_token)
                else:
                    break

            if head_token['xpos'] != 'Г5' or sentence[token['head'] - 1]['xpos'] != 'Г5' and head_token['deprel'] == '_':
                # Поиск всех зависимых ИНФ от найденного ИНФ
                bool_inf_child = True
                while bool_inf_child:
                    bool_inf_child = False
                    for token in sentence:
                        if token['head'] == last_inf_token['id']:
                            if check_feat(token, 'ИНФ'):
                                group_token.append(token)
                                inf_group_token.append(token)
                                last_inf_token = token
                                bool_inf_child = True
                                break

                bool_check_g5 = True
                if len(group_token) == 2:
                    for token in group_token:
                        if not check_feat(token, 'ИНФ'):
                            bool_check_g5 = False
                if len(group_token) < 2:
                    bool_check_g5 = False

                if bool_check_g5:
                    # Поиск двух наборов пар связей (в первой все связи, в которых отсуствует последний ИНФ, а во второй - присуствует)
                    pairs = get_sorted_pairs(sentence)
                    buf_pairs = pairs.copy()
                    inf_pairs = []
                    for pair in buf_pairs:
                        if last_inf_token['id'] in pair and last_inf_token['head'] not in pair:
                            inf_pairs.append(pair)
                            pairs.remove(pair)

                    # Удалить все пары с последним ИНФ, которые нарушают проективность
                    qnt_inf_pairs = len(inf_pairs)
                    buf_inf_pairs = inf_pairs.copy()
                    for inf_pair in buf_inf_pairs:
                        if last_inf_token['head'] > inf_pair[0] and last_inf_token['head'] < inf_pair[1]:
                            inf_pairs.remove(inf_pair)
                            continue
                        for pair in pairs:
                            if (inf_pair[0] > pair[0] and inf_pair[0] < pair[1] and (inf_pair[1] < pair[0] or inf_pair[1] > pair[1])) or (inf_pair[1] > pair[0] and inf_pair[1] < pair[1] and (inf_pair[0] < pair[0] or inf_pair[0] > pair[1])):
                                inf_pairs.remove(inf_pair)
                                break

                    # Проверка, что нужно добавлять новую группу
                    if qnt_inf_pairs > len(inf_pairs):
                        bool_new_group = True

                        # Дополнить набор слов, которые образуют новую группу
                        # for pair in inf_pairs:
                        #     if pair[0] != last_inf_token['id']:
                        #         token = sentence[pair[0] - 1]
                        #     else:
                        #         token = sentence[pair[1] - 1]
                        #     group_token.extend(get_token_for_group(token, sentence))

                        # Получить текст группы
                        buf_group_token = group_token.copy()
                        for token in buf_group_token:
                            if token['lemma'] == '_' and token['form'] == '_':
                                group_token.remove(token)
                                group_token.extend(get_group_component_sg(token, sentence))
                        group_token.sort(key=lambda token: token['id'])
                        phrase = ''
                        for token in group_token:
                            phrase += token['form'] + ' '
                        phrase = phrase[:-1]
                        group_token = buf_group_token.copy()

                        # Получить все слова, которые связаны со словами из группы
                        list_one_step_children_token = []
                        for token in group_token:
                            list_one_step_children_token.extend(get_group_one_step_child_token(token, sentence))

                        # Добавить новую группу и изменить связи между элементами ССГ
                        for token in list_one_step_children_token:
                            if token not in group_token:
                                token['head'] = len(sentence) + 1
                        sentence.append(create_sg(len(sentence) + 1, phrase, 'Г5', head_token['head'], head_token['deprel']))
                        head_token['deprel'] = '_'
                        head_token['head'] = len(sentence)
    return bool_new_group

# ===========================================================================

def rule_g_6(sentence: TokenList):
    bool_new_group = False
    for token in sentence:
        # поиск ГЛ, который не является ИНФ
        if token['upos'] == 'VERB' and not check_feat(token, 'ИНФ'):
            head_token = token
            while head_token['deprel'] == '_' and head_token['head'] != 1:
                head_token = sentence[head_token['head'] - 1]

            if head_token['xpos'] != 'Г6' or sentence[token['head'] - 1]['xpos'] != 'Г6' and head_token['deprel'] == '_':
                # поиск N, который зависит от найденного слова
                for token in get_group_one_step_child_token(head_token, sentence):
                    buf_token = token
                    if buf_token['lemma'] == '_' and buf_token['form'] == '_':
                        root_component = get_root_component_sg(buf_token, sentence)
                        if root_component != None:
                            buf_token = get_root_component_sg(buf_token, sentence)
                    if buf_token['upos'] in ['PRON', 'NOUN', 'ADJ', 'ADV']:
                        noun_token = token

                        # Поиск двух наборов пар связей (в первой все связи, в которых отсуствует найденный СУЩ, а во второй - присуствует)
                        pairs = get_sorted_pairs(sentence)
                        noun_pairs = []
                        buf_pairs = pairs.copy()
                        if noun_token['lemma'] == '_' and noun_token['form'] == '_':
                            id_noun_token = get_root_component_sg(noun_token, sentence)['id']
                            for token in sentence:
                                if token['head'] == id_noun_token:
                                    id_child_token = token['id']
                                    break
                            for pair in buf_pairs:
                                if id_noun_token in pair and get_id_head_token(noun_token, sentence) not in pair and id_child_token not in pair:
                                    noun_pairs.append(pair)
                                    pairs.remove(pair)
                        else:
                            id_noun_token = noun_token['id']
                            for pair in buf_pairs:
                                if id_noun_token in pair and get_id_head_token(noun_token, sentence) not in pair:
                                    noun_pairs.append(pair)
                                    pairs.remove(pair)

                        # Проверить, что существуют пары с ИНФ
                        qnt_noun_pairs = len(noun_pairs)
                        if qnt_noun_pairs > 0:
                            # Удалить все пары с ИНФ, которые нарушают проективность
                            buf_noun_pairs = noun_pairs.copy()
                            for noun_pair in buf_noun_pairs:
                                if get_id_head_token(noun_token, sentence) > noun_pair[0] and get_id_head_token(noun_token, sentence) < noun_pair[1]:
                                    noun_pairs.remove(noun_pair)
                                    continue
                                for pair in pairs:
                                    if (noun_pair[0] > pair[0] and noun_pair[0] < pair[1] and (noun_pair[1] < pair[0] or noun_pair[1] > pair[1])) or (noun_pair[1] > pair[0] and noun_pair[1] < pair[1] and (noun_pair[0] < pair[0] or noun_pair[0] > pair[1])):
                                        noun_pairs.remove(noun_pair)
                                        break

                            # Проверка, что нужно добавлять новую группу
                            if qnt_noun_pairs > len(noun_pairs):
                                bool_new_group = True

                                # Получить набор слов, которые образуют новую группу
                                group_token = [head_token, noun_token]
                                # for pair in noun_pairs:
                                #     if pair[0] != noun_token['id']:
                                #         token = sentence[pair[0] - 1]
                                #     else:
                                #         token = sentence[pair[1] - 1]
                                #     group_token.extend(get_token_for_group(token, sentence))

                                # Получить словосочетание
                                buf_group_token = group_token.copy()
                                for token in buf_group_token:
                                    if token['lemma'] == '_' and token['form'] == '_':
                                        group_token.remove(token)
                                        group_token.extend(get_group_component_sg(token, sentence))
                                group_token.sort(key=lambda token: token['id'])
                                phrase = ''
                                for token in group_token:
                                    phrase += token['form'] + ' '
                                phrase = phrase[:-1]
                                group_token = buf_group_token.copy()

                                # Получить все слова, которые связаны со словами из группы
                                group_one_step_child_token = []
                                for token in group_token:
                                    group_one_step_child_token.extend(get_group_one_step_child_token(token, sentence))

                                # Добавить новую группу и изменить связи между элементами ССГ
                                for token in group_one_step_child_token:
                                    if token not in group_token:
                                        token['head'] = len(sentence) + 1
                                sentence.append(create_sg(len(sentence) + 1, phrase, 'Г6', head_token['head'], head_token['deprel']))
                                head_token['deprel'] = '_'
                                head_token['head'] = len(sentence)

        # Поиск ИНФ, который не завист от другого ИНФ
        if check_feat(token, 'ИНФ') and not check_feat(sentence[token['head'] - 1], 'ИНФ'):
            head_token = token
            last_inf_token = token
            while head_token['deprel'] == '_' and head_token['head'] != 1:
                head_token = sentence[head_token['head'] - 1]

            group_token = [head_token]
            inf_group_token = [head_token]
            bool_N = False
            while True:
                if head_token['head'] == 1:
                    break

                buf_head_token = sentence[head_token['head'] - 1]

                if buf_head_token['xpos'] in ['Г3', 'Г4', 'Г5', 'Г6', 'Г7', 'Г8', 'Г15', 'Г16']:
                    break

                if buf_head_token['deprel'] in ['сент-соч', 'кратн', 'релят', 'разъяснит', 'примыкат', 'подч-союзн', 'инф-союзн', 'сравн-союзн', 'сравнит', 'эксплет']:
                    break

                if buf_head_token['lemma'] == '_' and buf_head_token['form'] == '_':
                    buf_head_token = get_root_component_sg(buf_head_token, sentence)

                if buf_head_token['id'] > head_token['id']:
                    break

                if buf_head_token['upos'] in ['VERB', 'NOUN', 'ADJ', 'ADV']:
                    if buf_head_token['upos'] in ['NOUN', 'ADJ', 'ADV']:
                        if bool_N:
                            break
                        bool_N = True
                    head_token = sentence[head_token['head'] - 1]
                    group_token.append(head_token)
                else:
                    break

            if head_token['xpos'] != 'Г6' or sentence[token['head'] - 1]['xpos'] != 'Г6' and head_token['deprel'] == '_':
                # Поиск всех зависимых ИНФ от найденного ИНФ
                bool_inf_child = True
                while bool_inf_child:
                    bool_inf_child = False
                    for token in sentence:
                        if token['head'] == last_inf_token['id']:
                            if check_feat(token, 'ИНФ'):
                                group_token.append(token)
                                inf_group_token.append(token)
                                last_inf_token = token
                                bool_inf_child = True
                                break

                bool_noun = False
                for noun_token in get_group_child_token(last_inf_token, sentence):
                    bool_noun = False
                    if noun_token['lemma'] == '_' and noun_token['form'] == '_':
                        if get_root_component_sg(noun_token, sentence)['upos'] in ['NOUN', 'ADJ', 'ADV']:
                            bool_noun = True
                    else:
                        if noun_token['upos'] in ['NOUN', 'ADJ', 'ADV']:
                            bool_noun = True

                if bool_noun:
                    group_token.append(noun_token)

                    # Поиск двух наборов пар связей (в первой все связи, в которых отсуствует найденный СУЩ, а во второй - присуствует)
                    pairs = get_sorted_pairs(sentence)
                    buf_pairs = pairs.copy()
                    noun_pairs = []
                    for pair in buf_pairs:
                        if noun_token['id'] in pair and noun_token['head'] not in pair:
                            noun_pairs.append(pair)
                            pairs.remove(pair)

                    # Удалить все пары с СУЩ, которые нарушают проективность
                    qnt_noun_pairs = len(noun_pairs)
                    buf_noun_pairs = noun_pairs.copy()
                    for noun_pair in buf_noun_pairs:
                        if noun_token['head'] > noun_pair[0] and noun_token['head'] < noun_pair[1]:
                            noun_pairs.remove(noun_pair)
                            continue
                        for pair in pairs:
                            if (noun_pair[0] > pair[0] and noun_pair[0] < pair[1] and (noun_pair[1] < pair[0] or noun_pair[1] > pair[1])) or (noun_pair[1] > pair[0] and noun_pair[1] < pair[1] and (noun_pair[0] < pair[0] or noun_pair[0] > pair[1])):
                                noun_pairs.remove(noun_pair)
                                break

                    # Проверка, что нужно добавлять новую группу
                    if qnt_noun_pairs > len(noun_pairs):
                        bool_new_group = True

                        # Дополнить набор слов, которые образуют новую группу
                        # for pair in noun_pairs:
                        #     if pair[0] != noun_token['id']:
                        #         token = sentence[pair[0] - 1]
                        #     else:
                        #         token = sentence[pair[1] - 1]
                        #     group_token.extend(get_token_for_group(token, sentence))

                        # Получить текст группы
                        buf_group_token = group_token.copy()
                        for token in buf_group_token:
                            if token['lemma'] == '_' and token['form'] == '_':
                                group_token.remove(token)
                                group_token.extend(get_group_component_sg(token, sentence))
                        group_token.sort(key=lambda token: token['id'])
                        phrase = ''
                        for token in group_token:
                            phrase += token['form'] + ' '
                        phrase = phrase[:-1]
                        group_token = buf_group_token.copy()

                        # Получить все слова, которые связаны со словами из группы
                        list_one_step_children_token = []
                        for token in group_token:
                            list_one_step_children_token.extend(get_group_one_step_child_token(token, sentence))

                        # Добавить новую группу и изменить связи между элементами ССГ
                        for token in list_one_step_children_token:
                            if token not in group_token:
                                token['head'] = len(sentence) + 1
                        sentence.append(create_sg(len(sentence) + 1, phrase, 'Г6', head_token['head'], head_token['deprel']))
                        head_token['deprel'] = '_'
                        head_token['head'] = len(sentence)
    return bool_new_group

# ===========================================================================

def rule_g_15_16(sentence: TokenList):
    # Поиск всех потенциальные групп слов (в том числе и единичные группы), которые связаны с остальным предложением отношением ВВОДН
    introductory_groups = []
    for token in sentence:
        bool_new_group = False
        group = []
        if token['deprel'] == 'вводн' and token['lemma'] != '_':
            if sentence[token['head'] - 1]['xpos'] not in ['Г15', 'Г16']:
                group = [token]
                group.extend(get_group_child_token(token, sentence))
                introductory_groups.append(group)

    # Разделить группы на две части, которые выполняют условие Г15 и которые выполняют условие Г16
    introductory_groups_15 = []
    introductory_groups_16 = []
    for group in introductory_groups:
        bool_15 = True
        bool_16 = True
        cnt_imen_padej = 0
        cnt_live = 0
        for token in group:
            if check_feat(token, 'ОД'):
                cnt_live += 1
            if check_feat(token, 'ИМ'):
                cnt_imen_padej += 1
            if token['deprel'] in ['предик']:
                bool_15 = False
                bool_16 = False
                continue
            if token['deprel'] in ['аппоз', 'об-аппоз']:
                bool_15 = False
            if not check_feat(token, 'ИМ') or check_feat(token, 'ЗВ'):
                bool_16 = False
            if token['upos'] in ['VERB', 'ADV']:
                bool_16 = False
            if token['upos'] in ['ADJ'] and len(group) == 1:
                bool_15 = False
        if cnt_imen_padej == len(group) and cnt_live > 1:
            bool_15 = False

        if bool_15:
            bool_new_group = True
            introductory_groups_15.append(group)
        elif bool_16:
            bool_new_group = True
            introductory_groups_16.append(group)

    # Создание новых групп
    if bool_new_group:
        id_new_group = len(sentence) + 1

        check_group_15 = []
        for group in introductory_groups_15:
            for token in group:
                check_group_15.append(token)
        check_group_16 = []
        for group in introductory_groups_16:
            for token in group:
                check_group_16.append(token)

        # Выделение групп Г15
        group = []
        if introductory_groups_15 != []:
            for token in sentence:
                if token['head'] == 1:
                    token['head'] = id_new_group
                if token not in check_group_15 and token['form'] != '_':
                    group.append(token)

            phrase = ''
            group.sort(key=lambda token: token['id'])
            for token in group:
                phrase += token['form'] + ' '
            phrase = phrase[:-1]
            sentence.append(create_sg(id_new_group, phrase, 'Г15', 1, '_'))
            id_15_group = len(sentence)

            for introductory_group in introductory_groups_15:
                if len(introductory_group) > 1:
                    head_token = None
                    for token in introductory_group:
                        if token['deprel'] == 'вводн':
                            head_token = token
                    introductory_group.sort(key=lambda token: token['id'])
                    head_token['deprel'] = '_'
                    head_token['head'] = len(sentence) + 1
                    phrase = ""
                    for token in introductory_group:
                        phrase += token['form'] + ' '
                    phrase = phrase[:-1]
                    sentence.append(create_sg(len(sentence) + 1, phrase, 'Г15', id_new_group, 'вводн'))
                    head_token['head'] = len(sentence)
                else:
                    introductory_group[0]['head'] = id_new_group

        # Выделение групп Г16
        group = []
        if introductory_groups_16 != []:
            if introductory_groups_15 != []:
                for token in sentence:
                    if token['head'] == id_new_group and token['deprel'] == '_':
                        token['head'] = len(sentence) + 1
                    if token not in check_group_16 and token not in check_group_15 and token['form'] != '_':
                        group.append(token)
                id_new_group = len(sentence) + 1
            else:
                for token in sentence:
                    if token['head'] == 1:
                            token['head'] = id_new_group
                    if token not in check_group_16 and token not in check_group_15 and token['form'] != '_':
                        group.append(token)

            phrase = ''
            group.sort(key=lambda token: token['id'])
            for token in group:
                phrase += token['form'] + ' '
            phrase = phrase[:-1]
            if introductory_groups_15 != []:
                sentence.append(create_sg(id_new_group, phrase, 'Г16', id_15_group, '_'))
            else:
                sentence.append(create_sg(id_new_group, phrase, 'Г16', 1, '_'))

            for introductory_group in introductory_groups_16:
                if len(introductory_group) > 1:
                    head_token = None
                    for token in introductory_group:
                        if token['deprel'] == 'вводн':
                            head_token = token
                    introductory_group.sort(key=lambda token: token['id'])
                    head_token['deprel'] = '_'
                    head_token['head'] = len(sentence) + 1
                    phrase = ""
                    for token in introductory_group:
                        phrase += token['form'] + ' '
                    phrase = phrase[:-1]
                    sentence.append(create_sg(len(sentence) + 1, phrase, 'Г16', id_new_group, 'вводн'))
                    head_token['head'] = len(sentence)
                else:
                    introductory_group[0]['head'] = id_new_group

    return bool_new_group