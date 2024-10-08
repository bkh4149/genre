#ジャンルを表示して選択、それがそのジャンルかをサーバーで認識して送り返す
#２回めのやり取りはjsonを使っている、クライアントはJavaScript　（fetch）
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    syukei_dic = {
        '雑学': 10, '動物': 6, '天体': 2, '地理': 2,
        '食物': 1, '言語': 1, 'スペイン語': 1,
        '美術': 1, '通貨': 1, '経済': 1
    }
    return render_template('index.html', syukei_dic=syukei_dic)

@app.route('/select', methods=['POST'])
def select():
    selected_category = request.json.get('category')
    return jsonify({'category': selected_category})

if __name__ == '__main__':
    app.run(debug=True)
