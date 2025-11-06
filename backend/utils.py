# 声调映射：带声调字符 -> (对应字母, 声调)
from typing import Dict, List, Union


TONE_MAP: Dict[str, tuple[str, int]] = {
    'ā': ('a', 1), 'á': ('a', 2), 'ǎ': ('a', 3), 'à': ('a', 4),
    'ē': ('e', 1), 'é': ('e', 2), 'ě': ('e', 3), 'è': ('e', 4),
    'ī': ('i', 1), 'í': ('i', 2), 'ǐ': ('i', 3), 'ì': ('i', 4),
    'ō': ('o', 1), 'ó': ('o', 2), 'ǒ': ('o', 3), 'ò': ('o', 4),
    'ū': ('u', 1), 'ú': ('u', 2), 'ǔ': ('u', 3), 'ù': ('u', 4),
    'ǖ': ('ü', 1), 'ǘ': ('ü', 2), 'ǚ': ('ü', 3), 'ǜ': ('ü', 4),
}

# 汉语拼音声母表
INITIALS: List[str] = [
    "zh","ch","sh","b","p","m","f","d","t","n","l",
    "g","k","h","j","q","x","r","z","c","s","y","w"
]

def split_syllable(syllable: str) -> Dict[str, Union[str, int]]:
    """
    拆分单个拼音音节为声母、韵母、声调
    轻声（无声调符号）声调为 0
    """
    tone: int = 0
    base: str = ""
    for ch in syllable:
        if ch in TONE_MAP:
            base += TONE_MAP[ch][0]
            tone = TONE_MAP[ch][1]
        else:
            base += ch
    if tone == 0:  # 轻声
        tone = 0

    # 拆声母
    initial: str = ''
    for ini in INITIALS:
        if base.startswith(ini):
            initial = ini
            break
    final: str = base[len(initial):]

    return {'initial': initial, 'final': final, 'tone': tone}

def split_pinyin_word(pinyin_str: str) -> List[Dict[str, Union[str, int]]]:
    """
    拆分四字成语的拼音，每个字返回 {initial, final, tone}
    如果不足四个字，用空字符串/0补齐
    """
    syllables = pinyin_str.split()
    result: List[Dict[str, Union[str, int]]] = [split_syllable(s) for s in syllables]
    while len(result) < 4:
        result.append({'initial': '', 'final': '', 'tone': 0})
    return result[:4]