from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey

metadata = MetaData()

sentence = Table(
    "sentence",
    metadata,
    Column("id_sentence", Integer, primary_key=True),
    Column("sent_id", String, nullable=False)
)

id_sentence_fk = ForeignKey("sentence.id_sentence")

token = Table(
    "token",
    metadata,
    Column("id_token", Integer, primary_key=True),
    Column("id_sentence", Integer, id_sentence_fk, nullable=False),
    Column("id", Integer, nullable=False),
    Column("form", String),
    Column("lemma", String),
    Column("upos", String, nullable=False),
    Column("xpos", String),
    Column("feats", String),
    Column("head", Integer, nullable=False),
    Column("deprel", String),
    Column("deps", String),
    Column("misc", String)
)