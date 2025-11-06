<template>
  <div class="solver-container">
    <h1 class="title">成语 Wordle Solver</h1>

    <!-- 当前猜测输入 -->
    <div class="input-row">
      <label>猜测成语：</label>
      <input
        v-model="guessWord"
        maxlength="4"
        placeholder="请输入4个字成语"
        class="idiom-input"
      />
    </div>

    <!-- 每个字的行式编辑区 -->
    <div class="char-card">
      <div class="char-row-header">
        <span>字</span>
        <span>字反馈</span>
        <span>声母</span>
        <span>韵母</span>
        <span>声调</span>
        <span>声母反馈</span>
        <span>韵母反馈</span>
        <span>声调反馈</span>
      </div>
      <div v-for="(ch, i) in guessChars" :key="i" class="char-row">
        <span class="char-box">{{ ch || '-' }}</span>

        <select v-model="charFeedback[i]">
          <option value="correct">正确</option>
          <option value="present">存在</option>
          <option value="absent">不存在</option>
        </select>

        <input v-model="pinyins[i].initial" size="2" />
        <input v-model="pinyins[i].final" size="3" />
        <input
          v-model.number="pinyins[i].tone"
          type="number"
          min="0"
          max="4"
        />

        <select v-model="pinyinFeedback[i].initial">
          <option value="correct">正确</option>
          <option value="present">存在</option>
          <option value="absent">不存在</option>
        </select>
        <select v-model="pinyinFeedback[i].final">
          <option value="correct">正确</option>
          <option value="present">存在</option>
          <option value="absent">不存在</option>
        </select>
        <select v-model="pinyinFeedback[i].tone">
          <option value="correct">正确</option>
          <option value="present">存在</option>
          <option value="absent">不存在</option>
        </select>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="buttons">
      <button class="primary-btn" @click="submitFeedback">提交反馈</button>
      <button class="secondary-btn" @click="resetGame">重置游戏</button>
    </div>

    <!-- 候选结果 -->
    <div v-if="candidates.length" class="candidates card">
      <h2>候选成语（{{ candidates.length }}个）</h2>
      <ul>
        <li v-for="word in candidates" :key="word">{{ word }}</li>
      </ul>
      <h3>推荐下一次猜测：<span class="highlight">{{ nextGuess }}</span></h3>
    </div>

    <!-- 历史记录 -->
    <div v-if="history.length" class="history card">
      <h2>历史记录</h2>
      <div v-for="(h, index) in history" :key="index" class="history-item">
        <div class="history-header">
          <strong>第 {{ index + 1 }} 次猜测：</strong>
          <span class="guess-word">{{ h.word }}</span>
          <button class="cancel-btn" @click="cancelFeedback(index)">撤销</button>
        </div>
        <div class="history-candidates">
          <p>
            候选数：{{ h.candidates.length }}，
            推荐：<span class="highlight">{{ h.nextGuess }}</span>
          </p>
        </div>
      </div>
    </div>
  </div>

  <footer class="footer">Made by 炫神沁音_official</footer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import axios from 'axios'
import { getInitialAndFinal, getNumOfTone, pinyin } from 'pinyin-pro'

const guessWord = ref('')
const guessChars = computed(() => guessWord.value.split(''))
const charFeedback = ref(['absent', 'absent', 'absent', 'absent'])
const pinyins = ref(
  Array.from({ length: 4 }, () => ({ initial: '', final: '', tone: 0 }))
)
const pinyinFeedback = ref(
  Array.from({ length: 4 }, () => ({
    initial: 'absent',
    final: 'absent',
    tone: 'absent',
  }))
)

const candidates = ref<string[]>([])
const nextGuess = ref('')
const history = ref<{ word: string; candidates: string[]; nextGuess: string }[]>(
  []
)

watch(guessWord, (newVal) => {
  const chars = newVal.split('')
  pinyins.value = chars.map((ch) => {
    const py = pinyin(ch, { toneType: 'none' })
    const tone = Number(getNumOfTone(pinyin(ch)))
    const { initial, final } = getInitialAndFinal(py)
    return { initial, final, tone }
  })
  while (pinyins.value.length < 4)
    pinyins.value.push({ initial: '', final: '', tone: 0 })
})

async function submitFeedback() {
  if (guessWord.value.length !== 4) {
    alert('请输入4个字成语！')
    return
  }

  const payload = {
    guess_word: guessChars.value,
    char_feedback: charFeedback.value,
    guess_pinyin: pinyins.value,
    pinyin_feedback: pinyinFeedback.value,
  }

  try {
    const res = await axios.post('/api/feedback', payload)
    candidates.value = res.data.candidates
    nextGuess.value = res.data.next_guess
    history.value.push({
      word: guessWord.value,
      candidates: [...res.data.candidates],
      nextGuess: res.data.next_guess,
    })
  } catch (err) {
    console.error(err)
    alert('提交失败')
  }
}

async function cancelFeedback(index: number) {
  try {
    const res = await axios.post(`/api/cancel_feedback/${index}`)
    if (res.data.status === 'ok') {
      history.value.splice(index, 1)
      candidates.value = res.data.candidates
      nextGuess.value = res.data.candidates[0] || ''
    } else {
      alert(res.data.message)
    }
  } catch (err) {
    console.error(err)
    alert('撤销失败')
  }
}

async function resetGame() {
  try {
    await axios.post('/api/reset')
    guessWord.value = ''
    charFeedback.value = ['absent', 'absent', 'absent', 'absent']
    pinyins.value = Array.from({ length: 4 }, () => ({
      initial: '',
      final: '',
      tone: 0,
    }))
    pinyinFeedback.value = Array.from({ length: 4 }, () => ({
      initial: 'absent',
      final: 'absent',
      tone: 'absent',
    }))
    candidates.value = []
    nextGuess.value = ''
    history.value = []
  } catch (err) {
    console.error(err)
    alert('重置失败')
  }
}
</script>

<style scoped>
body {
  background-color: #f6f7fb;
}

.solver-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 1.5rem 2rem;
  font-family: "Segoe UI", sans-serif;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.title {
  text-align: center;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.input-row {
  margin-bottom: 1rem;
  text-align: center;
  font-size: 1.1rem;
}

.idiom-input {
  width: 220px;
  font-size: 1.2rem;
  text-align: center;
  padding: 0.4rem;
  border-radius: 6px;
  border: 1px solid #ccc;
}

.char-card {
  background-color: #f9fafc;
  border-radius: 8px;
  padding: 0.8rem;
  border: 1px solid #ddd;
}

.char-row-header,
.char-row {
  display: grid;
  grid-template-columns: 40px 80px 60px 60px 50px 80px 80px 80px;
  gap: 6px;
  align-items: center;
}

.char-row-header {
  font-weight: bold;
  color: #333;
  border-bottom: 1px solid #ccc;
  padding-bottom: 0.3rem;
  margin-bottom: 0.4rem;
}

.char-box {
  text-align: center;
  font-weight: bold;
  color: #2c3e50;
}

select,
input {
  padding: 4px;
  border-radius: 4px;
  border: 1px solid #ccc;
  font-size: 0.9rem;
}

.buttons {
  margin-top: 1.5rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

button {
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  transition: 0.25s;
}

.primary-btn {
  background-color: #409eff;
  color: white;
}

.primary-btn:hover {
  background-color: #66b1ff;
}

.secondary-btn {
  background-color: #f0f0f0;
  color: #333;
}

.secondary-btn:hover {
  background-color: #e0e0e0;
}

.cancel-btn {
  margin-left: auto;
  background-color: #fbeaea;
  color: #c0392b;
  border: 1px solid #f5c6c6;
  font-size: 0.8rem;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
}

.cancel-btn:hover {
  background-color: #f8d7da;
}

.card {
  background-color: #f9fafc;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1.5rem;
}

.highlight {
  color: #409eff;
  font-weight: bold;
}

.footer {
  text-align: center;
  margin-top: 2rem;
  padding: 1rem;
  color: #888;
  font-size: 0.9rem;
}
</style>
