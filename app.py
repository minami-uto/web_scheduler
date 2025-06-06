from flask import Flask, render_template, request, redirect, Response
import json
import os
import io
import csv

app = Flask(__name__)
CANDIDATES_FILE = 'candidates.json'
TEMPLATE_FILE = 'datetime_templates.json'
RESPONSES_FILE = 'responses.json'

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}
    
def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_responses():
    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_responses(data):
    with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@app.route('/')
def index():
    return redirect('/add_candidates')


@app.route('/add_candidates', methods=['GET', 'POST'])
def add_candidates():
    templates = load_json(TEMPLATE_FILE)

    if request.method == 'POST':
        selected = {}
        for session, days in templates.items():
            for day in days:
                key = f"{session}__{day}"
                times = request.form.getlist(key)
                if times:
                    if session not in selected:
                        selected[session] = {}
                    selected[session][day] = times

        if selected:
            save_json(selected, CANDIDATES_FILE)
            return render_template('add_candidates.html', templates=templates, message="保存しました！")
        else:
            return render_template('add_candidates.html', templates=templates, message="時間を選択してください")
        
    return render_template('add_candidates.html', templates=templates)


@app.route('/student_select', methods=['GET', 'POST'])
def student_select():
    # JSONからアクティブな候補日を読み込む
    templates = load_json(TEMPLATE_FILE)     #例: templatesに全ての候補日時
    
    #active_candidates = {}      #アクティブな日時だけを抽出
    active_candidates = templates #仮に全部表示

    if request.method == 'POST':
        selected = request.form.getlist('selected_dates')
    return render_template('student_select.html', candidates=active_candidates)    

@app.route('/choose', methods=['GET', 'POST'])
def choose():
    candidates = load_json(CANDIDATES_FILE)
    if request.method == 'POST':
        name = request.form.get('name')
        choices = request.form.getlist('choice') #希望日時のキーを複数受け取る想定

        if not name or not choices:
            return render_template('choose.html', candidates=candidates, message="名前と希望日時を選択してください")
        
        responses = load_responses()
        responses[name] = choices
        save_responses(responses)

        return render_template('choose.html', candidates=candidates, message="希望を送信しました。ありがとうございます！")
    return render_template('choose.html', candidates=candidates)

@app.route('/submit_availability', methods=['GET', 'POST'])
def submit_availability():
    candidates = load_json(CANDIDATES_FILE)
    if request.method == 'POST':
        name = request.form.get('name')
        responses = {}
        for session, days in candidates.items():
            for day, times in days.items():
                key = f"{session}__{day}"
                selected_times = request.form.getlist(key)
                if selected_times:
                    if session not in responses:
                        responses[session] = {}
                    responses[session][day] = selected_times
        if name and responses: #保存処理
            filename = f"responses_{name}.json"
            save_json(responses, filename)
            return render_template('submit_availability.html', candidates=candidates, message="送信しました！")
        else:
            return render_template('submit_availability.html', candidates=candidates, message="名前と時間を選んでください")
    return render_template('submit_availability.html', candidates=candidates) 

@app.route('/view_responses')
def view_responses():
    candidates = load_json(CANDIDATES_FILE)
    responses = load_responses()

    summary = {} #各日時に対して希望者の数をカウントする辞書

    for name, choices in responses.items():
        if isinstance(choices, dict): #submit_availability形式のデータ
            for session, days in choices.items():
                for day, times in days.items():
                    for time in times:
                        key = f"{session}__{day}__{time}"
                        if key not in summary:
                            summary[key] = []
                        summary[key].append(name)
        elif isinstance(choices, list): #choose形式のデータ
            for key in choices:
                if key not in summary:
                    summary[key] = []
                summary[key].append(name)

    return render_template('view_responses.html', summary=summary, responses=responses, candidates=candidates)

@app.route('/export_csv')
def export_csv():
    responses = load_responses() #受講生ごとの希望日時の辞書
    candidates = load_json(CANDIDATES_FILE)

    #日時ごとの希望者数と名前のリストを作成
    date_counts = {}
    for name, choices in responses.items():
        for choice in choices:
            if choice not in date_counts:
                date_counts[choice] = []
            date_counts[choice].append(name)
    
    # csvをメモリ上で作成
    output = io.StringIO()
    writer = csv.writer(output)

    #ヘッダー行
    writer.writerow(['日時','希望者数','希望者リスト'])
    for date, names in date_counts.items():
        writer.writerow([date, len(names), ', '.join(names)])

    writer.writerow([]) #空行

    writer.writerow(['受講生名', '希望日時'])
    for name, choices in responses.items():
        writer.writerow([name, ', '.join(choices)])

    #CSVデータ取得
    csv_data = output.getvalue()
    output.close()

    #レスポンスとしてCSVファイルを返す
    return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=availability_sammary.csv'})

@app.route('/download_csv')
def download_csv():
    responses = load_responses()
    candidates = load_json(CANDIDATES_FILE)

    count_dict = {} #集計辞書を作成
    for name, choices in responses.items():
        for choice in choices:
            if choice not in count_dict:
                count_dict[choice] = []
            count_dict[choice].append(name)
    
    def generate():
        yield '日時,希望者数,名前一覧\n'
        for datetime, names in count_dict.items():
            line = f'{datetime},{len(names)},"{"、".join(names)}"\n'
            yield line

    return Response(generate(), mimetype='text/csv', headers={"Content-Diposition": "attachment;filename=希望日時集計.csv"})

if __name__ == '__main__':
    app.run(debug=True)