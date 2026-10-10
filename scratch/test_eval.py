import sys
sys.path.insert(0, '.')
import re
from backend.data.question_bank import get_question_by_id
from backend.ai.evaluation_engine import local_rubric_evaluate

q = get_question_by_id('prog_med_1')
with open('tests/test_dynamic_questioning.py', 'r', encoding='utf-8') as f:
    text = f.read()

# find candidate_answer in test_hindi
matches = re.findall(r'candidate_answer["\']?:\s*["\']([^"\']+)["\']', text)
for i, ans in enumerate(matches):
    ev = local_rubric_evaluate(q, ans, 'hi')
    print(f"Match {i}: {ans[:40]}... -> Score: {ev['score']}")
