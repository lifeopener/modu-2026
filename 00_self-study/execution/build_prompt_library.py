"""
프롬프트 파일들을 읽어서 JS 라이브러리 파일로 변환하는 스크립트
"""
import os, json, re

PROMPT_DIR = os.path.join(os.path.dirname(__file__), '..', '02_solution', '주식투자 프롬프트')
OUTPUT_JS = os.path.join(os.path.dirname(__file__), '..', '02_solution', '02a_prompt_library.js')

# 카테고리 분류 규칙
def categorize(filename):
    if filename.startswith('★'):
        return 'stock'  # 종목 분석
    elif filename.startswith('Daily_수시'):
        return 'realtime'  # 수시/실시간
    elif filename.startswith('Daily_'):
        return 'daily'  # 일간
    elif filename.startswith('W_'):
        return 'weekly'  # 주간/월간
    elif '텐베거' in filename:
        return 'special'  # 특수
    else:
        return 'other'

# 제목 추출 (파일명에서)
def extract_title(filename):
    name = os.path.splitext(filename)[0]
    # 접두사 제거
    name = re.sub(r'^[★]+\s*', '', name)
    name = re.sub(r'^Daily_\d+_', '', name)
    name = re.sub(r'^Daily_수시\s*[①②③④⑤]_', '', name)
    name = re.sub(r'^W_[①②③④⑤⑥⑦]\s*', '', name)
    return name.strip()

# 카테고리 메타데이터
CAT_META = {
    'stock': {'name': '⭐ 종목 분석', 'desc': '개별 종목 심층 분석, 매수전 체크, 적정주가, 수급 분석 등', 'icon': '⭐'},
    'daily': {'name': '📅 일간 모니터링', 'desc': '매일 수행하는 거시경제, 장세, 수급, 레이더 분석', 'icon': '📅'},
    'realtime': {'name': '⚡ 실시간/수시', 'desc': '장중 실시간으로 수행하는 종목 선정, 트레일링, 흐름 모니터링', 'icon': '⚡'},
    'weekly': {'name': '📊 주간/월간', 'desc': '주간 시장 리뷰, 경제 사이클, 종목 선정, 포트폴리오 점검', 'icon': '📊'},
    'special': {'name': '🚀 특수 전략', 'desc': '텐배거 모니터링 등 특별 전략', 'icon': '🚀'},
}

# 프롬프트 파일 수집
prompts = {}
for cat in CAT_META:
    prompts[cat] = []

for filename in sorted(os.listdir(PROMPT_DIR)):
    if not filename.endswith('.txt'):
        continue
    filepath = os.path.join(PROMPT_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    cat = categorize(filename)
    title = extract_title(filename)
    
    prompts[cat].append({
        'id': re.sub(r'[^a-zA-Z0-9]', '_', os.path.splitext(filename)[0])[:40],
        'title': title,
        'filename': filename,
        'content': content,
    })

# JS 파일 생성
js_lines = ['// Stock Master AI - 실전 투자 프롬프트 라이브러리',
            '// 자동 생성됨 - 수정하지 마세요',
            f'// 총 {sum(len(v) for v in prompts.values())}개 프롬프트',
            '',
            'const PROMPT_CATEGORIES = ' + json.dumps(CAT_META, ensure_ascii=False, indent=2) + ';',
            '',
            'const PROMPT_LIBRARY = ' + json.dumps(prompts, ensure_ascii=False, indent=2) + ';',
            '',
            '// 프롬프트 검색 함수',
            'function searchPrompts(query) {',
            '  const results = [];',
            '  const q = query.toLowerCase();',
            '  for (const [cat, items] of Object.entries(PROMPT_LIBRARY)) {',
            '    for (const item of items) {',
            '      if (item.title.toLowerCase().includes(q) || item.content.toLowerCase().includes(q)) {',
            '        results.push({...item, category: cat});',
            '      }',
            '    }',
            '  }',
            '  return results;',
            '}',
            '',
            '// 특정 카테고리 프롬프트 가져오기',
            'function getPromptsByCategory(cat) {',
            '  return PROMPT_LIBRARY[cat] || [];',
            '}',
            '',
            '// 프롬프트 ID로 가져오기',
            'function getPromptById(id) {',
            '  for (const items of Object.values(PROMPT_LIBRARY)) {',
            '    const found = items.find(p => p.id === id);',
            '    if (found) return found;',
            '  }',
            '  return null;',
            '}',
]

with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
    f.write('\n'.join(js_lines))

total = sum(len(v) for v in prompts.values())
print(f'✅ 프롬프트 라이브러리 생성 완료!')
print(f'   총 {total}개 프롬프트 ({len(prompts)} 카테고리)')
print(f'   출력: {OUTPUT_JS}')
for cat, items in prompts.items():
    print(f'   - {CAT_META[cat]["name"]}: {len(items)}개')
