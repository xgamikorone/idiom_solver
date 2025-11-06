# -*- coding: utf-8 -*-
# File: make_database.py
# Author: qzz
# Date: 2025/11/06
# Desc: Convert idiom.json into database
import json
import sqlite3
from typing import List, TypedDict

from tqdm import tqdm
from backend.utils import split_syllable, split_pinyin_word

IDIOM_JSON_FILE_PATH = "./chinese-xinhua/data/idiom.json"
DEFAULT_DB_PATH = "./backend/idiom_database.db"


class IdiomData(TypedDict):
    derivation: str  # 出处
    example: str  # 例句
    explanation: str  # 释义
    pinyin: str  # 拼音
    word: str  # 成语
    abbreviation: str  # 缩写


class IdiomDatabase:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.create_table()

    def create_table(self):

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS idioms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT,
                initial1 TEXT, final1 TEXT, tone1 INTEGER,
                initial2 TEXT, final2 TEXT, tone2 INTEGER,
                initial3 TEXT, final3 TEXT, tone3 INTEGER,
                initial4 TEXT, final4 TEXT, tone4 INTEGER,
                pinyin TEXT,
                explanation TEXT,
                example TEXT,
                derivation TEXT,
                abbreviation TEXT
            )
        """
        )
        self.conn.commit()

    def insert_idiom(self, idiom: IdiomData):
        word = idiom.get("word", "")
        pinyin_str = idiom.get("pinyin", "")
        detailed = split_pinyin_word(pinyin_str)

        self.cursor.execute(
            """
            INSERT OR REPLACE INTO idioms (
            word, 
            initial1, final1, tone1,
            initial2, final2, tone2,
            initial3, final3, tone3,
            initial4, final4, tone4,
            pinyin, 
            explanation, example, 
            derivation, abbreviation)
            VALUES (?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?)
        """,
            (
                word,
                detailed[0]["initial"],
                detailed[0]["final"],
                detailed[0]["tone"],
                detailed[1]["initial"],
                detailed[1]["final"],
                detailed[1]["tone"],
                detailed[2]["initial"],
                detailed[2]["final"],
                detailed[2]["tone"],
                detailed[3]["initial"],
                detailed[3]["final"],
                detailed[3]["tone"],
                idiom["pinyin"],
                idiom["explanation"],
                idiom["example"],
                idiom["derivation"],
                idiom["abbreviation"],
            ),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_num_idioms(self) -> int:
        self.cursor.execute("SELECT COUNT(*) as count FROM idioms")
        row = self.cursor.fetchone()
        return row["count"] if row else 0
    
    def get_random_idiom(self) -> str:
        self.cursor.execute("SELECT word FROM idioms ORDER BY RANDOM() LIMIT 1")
        row = self.cursor.fetchone()
        return row["word"] if row else ""

    def close(self):
        self.conn.close()


def make_database(
    json_file_path: str = IDIOM_JSON_FILE_PATH, db_path: str = DEFAULT_DB_PATH
):
    with open(json_file_path, "r", encoding="utf-8") as f:
        idioms: List[IdiomData] = json.load(f)

    db = IdiomDatabase(db_path)
    for idiom in tqdm(idioms):
        if len(idiom["word"]) != 4:
            continue  # 只处理四字成语

        db.insert_idiom(idiom)
    # db.close()

    return db.get_num_idioms()


if __name__ == "__main__":
    make_database()
    db = IdiomDatabase()
    print(db.get_num_idioms())
    db.close()
