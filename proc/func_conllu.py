from conllu.models import TokenList, Token

#Возвращает группу зависимых токенов от данного токена (кроме тех, что входят в состав СГ)
def get_group_child_token(head_token: Token, sentence: TokenList) -> list:
    group_child_token = []
    for token in sentence:
        if token['head'] == head_token['id'] and token['deprel'] != '_':
            group_child_token.append(token)
            group_child_token.extend(get_group_child_token(token, sentence))
    return group_child_token

#Возвращает группу зависимых токенов от данного токена, что находятся на расстоянии равной единице (кроме тех, что входят в его состав, если такие есть)
def get_group_one_step_child_token(head_token: Token, sentence: TokenList) -> list:
    #print('111', head_token)
    #print('111', head_token['upos'])
    group_one_step_child_token = []
    for token in sentence:
        if token['id'] != 1 and token['head'] != 1 and token['id'] != head_token['id']:
            #print('222', token)
            #print('222', token['upos'])
            if token['head'] == head_token['id'] and token['deprel'] != '_':
                    group_one_step_child_token.append(token)
            #print('555', group_one_step_child_token)
    return group_one_step_child_token

#Возвращает первый компонент СГ
def get_group_component_sg(head_token: Token, sentence: TokenList) -> list:
    components = []
    for token in sentence:
        if head_token['id'] == token['head'] and token['deprel'] == '_':
            if token['lemma'] != '_':
                components.append(token)
            else:
                components.extend(get_group_component_sg(token, sentence))
            components.extend(get_group_child_token(token, sentence))
    return components

def get_root_component_sg(head_token: Token, sentence: TokenList) -> list:
    for token in sentence:
        if head_token['id'] == token['head'] and token['deprel'] == '_':
            head_token = token
            if head_token['lemma'] == '_':
                head_token = get_root_component_sg(head_token, sentence)
            return head_token
    return None

def get_id_head_token(token: Token, sentence: TokenList) -> Token:
    if token['head'] == 1 or token['id'] == 1:
        return 0

    elif token['deprel'] != '_':
        if sentence[token['head'] - 1]['lemma'] != '_':
            return token['head']
        else:
            return get_root_component_sg(sentence[token['head'] - 1], sentence)['id']

    elif token['deprel'] == '_':
        return get_id_head_token(sentence[token['head'] - 1], sentence)

#Возвращает все пары отношений в предложении (элементы пары упорядочны по возрастнию)
def get_sorted_pairs(sentence: TokenList) -> list:
    pairs = []
    id_head_token = 0
    for token in sentence:
        if token['lemma'] != '_' and token['head'] != 0 and token['head'] != 1:
            if token['deprel'] != '_' and sentence[token['head'] - 1]['lemma'] != '_':
                id_head_token = token['head']
            elif token['deprel'] != '_' and sentence[token['head'] - 1]['lemma'] == '_':
                id_head_token = get_root_component_sg(sentence[token['head'] - 1], sentence)['id']
            else:
                if get_root_component_sg(sentence[token['head'] - 1], sentence)['id'] == token['id']:
                    id_head_token = get_id_head_token(token, sentence)
                else:
                    continue
            if id_head_token == 0:
                continue
            pair = [token['id'], id_head_token]
            pair.sort()
            pairs.append(pair)
    return pairs

def get_token_for_group(token: Token, sentence: TokenList):
    if token['deprel'] not in ['сент-соч', 'кратн', 'релят', 'разъяснит', 'примыкат', 'подч-союзн', 'инф-союзн', 'сравн-союзн', 'сравнит', 'эксплет']:
        group_child_token = [token]
        for child_token in get_group_one_step_child_token(token, sentence):
            group_child_token.extend(get_token_for_group(child_token, sentence))
        return group_child_token
    else:
        return []

#Возвращает новый токен-СГ
def create_sg(id: int, upos: str, xpos: str, head: int, deprel: str) -> Token:
    return Token(
            id = id,
            form = '_',
            lemma = '_',
            upos = upos,
            xpos = xpos,
            feats = None,
            head = head,
            deprel = deprel,
            deps = None,
            misc = None
            )

#Добавляет токен-корень, представляющий всё предложение целиком
def add_root_token(sentence: TokenList):
    phrase = ""
    for token in sentence:
        if token['form'] != '_':
            phrase += token['form'] + ' '
        token['id'] += 1
        token['head'] += 1
    phrase = phrase[:-1]

    sentence.append(create_sg(1, phrase, '*', 0, '_'))
    sentence.sort(key=lambda token: token['id'])

#Проверяет наличие определённой морфологической характеристики у токена
def check_feat(token: Token, feat: str) -> bool:
    if token['feats'] != None:
        if feat in str(list(token['feats'].keys())[0]): ############## Нужен str()?
            return True
    return False
