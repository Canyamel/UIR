from typing import Any


class Word:
    def __init__(self, word, initial_form_word=None, part_speech=None, time=None, genus=None, number=None, case=None, animacy=None,
                comparison=None, brevity=None, representation=None, inclination=None, aspect=None, face=None, voice=None, additional_feature=None) -> None:
        self.word = word #слово
        self.initial_form_word = initial_form_word #начальная форма слова
        self.part_speech = part_speech #часть речи
        self.time = time #время
        self.genus = genus #род
        self.number = number #число
        self.case = case #падеж
        self.animacy = animacy #одушевлённость
        self.comparison = comparison #сравнение
        self.brevity = brevity #краткость
        self.representation = representation #репрезентация
        self.inclination = inclination #наклонение
        self.aspect = aspect #вид
        self.face = face #лицо
        self.voice = voice #залог
        self.additional_feature = additional_feature #дополнительные характеристики

    def __repr__(self):
        return f"{self.word}"

class NodeWord:
    def __init__(self, word: Word, index: int) -> None:
        self.word = word
        self.index = index

    def __repr__(self):
        return f"{self.word}"

class Edge:
    def __init__(self, start, end, mark=None) -> None:
        self.start = start
        self.end = end
        self.mark = mark

    def __repr__(self):
        return f"({self.start}, {self.end})"

class SyntacticTree:
    def __init__(self, list_NodeWord, list_Edge, root: int, sentence: str) -> None:
        self.list_NodeWord = list_NodeWord
        self.list_Edge = list_Edge
        self.root = root
        self.sentence = sentence

class SyntacticGroup:
    def __init__(self, list_Word, criteria, index: int) -> None:
        self.list_Word = list_Word
        self.criteria = criteria
        self.index = index

class SystemSyntacticGroup:
    def __init__(self, list_SyntacticGroup, list_Edge, root: int, sentence: str) -> None:
        self.list_SyntacticGroup = list_SyntacticGroup
        self.list_Edge = list_Edge
        self.root = root
        self.sentence = sentence