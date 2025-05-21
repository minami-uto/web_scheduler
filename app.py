from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)
CANDIDATES_FILE = 'candidates.json'
TEMPLATE_FILE = 'datetime_templates.json'

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
        return {}
    
def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    return redirect('/add_candidates')


@app.route('/add_candidates', methods=['GET', 'POST'])
def add_candidates():
    templates = load_json(TEMPLATE_FILE)

    if request.method == 'POST':
        selected = {}
        for week, days in templates.items():
            for day in days:
                key = f"{week}__{day}"
                times = request.form.getlist(key)
                if times:
                    if week not in selected:
                        selected[week] = {}
                    selected[week][day] = times

        if selected:
            save_json(selected, CANDIDATES_FILE)
            return render_template('add_candidates.html', templates=templates, message="保存しました！")
        else:
            return render_template('add_candidates.html', templates=templates, message="時間を選択してください")
        
    return render_template('add_candidates.html', templates=templates)

if __name__ == '__main__':
    app.run(debug=True)