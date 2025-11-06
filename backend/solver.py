from typing import List, Dict, Literal
from backend.make_database import IdiomDatabase

Feedback = Literal["correct", "present", "absent"]


class IdiomWordleSolver:
    def __init__(self, db: "IdiomDatabase"):
        self.db = db
        self.history: List = []  # 存储多轮反馈
        self.candidates: List[str] = self._load_all_words()

    def _load_all_words(self) -> List[str]:
        """载入所有成语"""
        self.db.cursor.execute("SELECT word FROM idioms")
        return [row["word"] for row in self.db.cursor.fetchall()]

    def add_feedback(
        self,
        guess_word: List[str],
        guess_pinyin: List[Dict[str, int]],
        char_fb: List[Feedback],
        pinyin_fb: List[Dict[str, Feedback]],
    ):
        """添加一轮反馈并更新候选成语列表"""
        self.history.append((guess_word, guess_pinyin, char_fb, pinyin_fb))
        self._update_candidates()

    def cancel_feedback(self, index: int) -> bool:
        """
        撤销第 index 次反馈，并重新计算候选集。
        :param index: 从 0 开始的反馈索引
        :return: 是否撤销成功
        """
        if 0 <= index < len(self.history):
            removed = self.history.pop(index)
            print(f"✅ 已撤销第 {index + 1} 次反馈: {removed}")
            self._update_candidates()
            return True
        else:
            print(f"⚠️ 无效的反馈索引 {index}")
            return False

    def _update_candidates(self):
        """根据所有历史反馈生成 SQL 条件筛选成语"""
        all_conditions = []
        all_params = []

        for guess_word, guess_pinyin, char_fb, pinyin_fb in self.history:
            # --- 字反馈 ---
            for i in range(4):
                pos = i + 1
                fb = char_fb[i]
                ch = guess_word[i]
                if fb == "correct":
                    all_conditions.append(f"substr(word,{pos},1)=?")
                    all_params.append(ch)
                elif fb == "present":
                    all_conditions.append(
                        f"word LIKE ? AND substr(word,{pos},1) != ?"
                    )
                    all_params.extend([f"%{ch}%", ch])
                elif fb == "absent":
                    all_conditions.append("word NOT LIKE ?")
                    all_params.append(f"%{ch}%")

            # --- 拼音反馈 ---
            for i in range(4):
                for key in ["initial", "final", "tone"]:
                    fb = pinyin_fb[i][key]
                    val = guess_pinyin[i][key]
                    col = f"{key}{i + 1}"

                    if fb == "correct":
                        all_conditions.append(f"{col}=?")
                        all_params.append(val)

                    elif fb == "present":
                        # 当前列不能等于该值，但该值必须存在于其他列
                        if key == "initial":
                            col_list = "initial1,initial2,initial3,initial4"
                        elif key == "final":
                            col_list = "final1,final2,final3,final4"
                        else:
                            col_list = "tone1,tone2,tone3,tone4"

                        # ✅ 用两个占位符，一个用于 !=，一个用于 IN (...)
                        all_conditions.append(f"{col}!=? AND ? IN ({col_list})")
                        all_params.extend([val, val])

                    elif fb == "absent":
                        all_conditions.append(f"{col}!=?")
                        all_params.append(val)

        # 拼接 SQL
        where_clause = " AND ".join(all_conditions) if all_conditions else "1"
        sql = f"SELECT word FROM idioms WHERE {where_clause}"

        # 调试输出
        print("========== SQL DEBUG ==========")
        print(sql)
        print("Params:", all_params)
        print("================================")

        # 执行查询
        self.db.cursor.execute(sql, all_params)
        self.candidates = [row["word"] for row in self.db.cursor.fetchall()]

    def get_candidates(self) -> List[str]:
        """返回当前候选成语"""
        return self.candidates

    def next_guess(self) -> str:
        """简单策略：返回第一个候选"""
        return self.candidates[0] if self.candidates else ""
