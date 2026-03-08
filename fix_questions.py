import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

data = json.load(open(r'D:\Documents\dp-100\questions.json', encoding='utf-8'))
flags = ['correct answer', 'explanation:', 'reference:', '**correct', '**explanation']
fixed = 0

for q in data:
    for o in q.get('options', []):
        txt = o.get('text', '')
        lower = txt.lower()
        if any(f in lower for f in flags):
            clean = txt.split('\n')[0].strip()
            clean = re.sub(r'\*+$', '', clean).strip()
            o['text'] = clean
            fixed += 1

print('Total fixed:', fixed)
json.dump(data, open(r'D:\Documents\dp-100\questions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('Saved.')
