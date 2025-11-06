from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Literal, Dict
from backend import IdiomWordleSolver, IdiomDatabase
from fastapi.middleware.cors import CORSMiddleware

# 类型定义
Feedback = Literal['correct', 'present', 'absent']

# FastAPI 实例
app = FastAPI()

# 允许跨域访问前端开发服务器（Vite 默认 5173）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库和 Solver
db = IdiomDatabase()
solver = IdiomWordleSolver(db)

# 请求模型
class FeedbackRequest(BaseModel):
    guess_word: List[str]                  # ['阿','鼻','恶','狱']
    guess_pinyin: List
    char_feedback: List[Feedback]          # ['correct', 'present', 'absent', 'correct']
    pinyin_feedback: List[Dict[str, Feedback]]  # [{'initial':..., 'final':..., 'tone':...}, ...]

# API 接口
@app.post("/api/feedback")
def add_feedback(req: FeedbackRequest):
    # 如果你没有前端提供拼音，这里可以从数据库获取拼音
    # guess_pinyin = []
    # for i, ch in enumerate(req.guess_word):
    #     # 简化：从数据库查询拼音
    #     row = db.cursor.execute("SELECT initial1, final1, tone1 FROM idioms WHERE substr(word,?,1)=?", (i+1, ch)).fetchone()
    #     if row:
    #         guess_pinyin.append({
    #             "initial": row["initial1"],
    #             "final": row["final1"],
    #             "tone": row["tone1"]
    #         })
    #     else:
    #         # 默认空值
    #         guess_pinyin.append({"initial":"", "final":"", "tone":0})

    # 调用 Solver 添加反馈
    solver.add_feedback(req.guess_word, req.guess_pinyin, req.char_feedback, req.pinyin_feedback)

    return {
        "candidates": solver.get_candidates(),
        "next_guess": solver.next_guess()
    }

# 可选：重置 Solver
@app.post("/api/reset")
def reset_solver():
    global solver
    solver = IdiomWordleSolver(db)
    return {"message": "Solver 已重置"}

@app.post("/api/cancel_feedback/{index}")
def cancel_feedback(index: int):
    success = solver.cancel_feedback(index)
    if success:
        return {
            "status": "ok",
            "message": f"已撤销第 {index + 1} 次反馈",
            "candidates": solver.get_candidates(),
        }
    else:
        return {"status": "error", "message": f"无效的索引 {index}"}
