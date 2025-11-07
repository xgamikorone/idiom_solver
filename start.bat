@echo on
REM 1. 激活 conda 环境
call conda activate live_stream

REM 2. 启动后端（FastAPI）
start "" cmd /c "uvicorn main:app --reload"

REM 3. 进入前端目录并启动前端
cd /d "%~dp0idiom-wordle"
start "" cmd /c "npm run dev"

REM 4. 打开浏览器访问前端
start "" http://localhost:5173
