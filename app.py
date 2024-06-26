import random
from flask import Flask, redirect, url_for, render_template, request, session
from flask_session import Session
import sqlite3
import bcrypt
from datetime import timedelta
from createquiz import app
from datetime import datetime

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# SQLite3データベース接続設定
def create_db_connection():
    connection = sqlite3.connect('sugizaki.db')
    return connection


# ユーザーの認証を行う関数
def authenticate_user(username, password):
    connection = create_db_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            query = "SELECT password_hash FROM users WHERE username = ?"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result:
                hashed_password = result[0]
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    return True
        except sqlite3.Error as e:
            print(f"The error '{e}' occurred")
        finally:
            cursor.close()
            connection.close()
    return False

with open('quiz_questions.txt', 'r', encoding='utf-8') as file:
    content = file.read().strip()
questions = content.split('\n\n')
sets = []
for question in questions:
    parts = question.split('\n')
    if len(parts) == 4:
        sets.append(parts)


# SQLite3データベース接続設定
def create_db_connection():
    connection = sqlite3.connect('sugizaki.db')
    return connection

# ユーザーの認証を行う関数
def authenticate_user(username, password):
    connection = create_db_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            query = "SELECT password_hash FROM users WHERE username = ?"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result:
                hashed_password = result[0]
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    return True
        except sqlite3.Error as e:
            print(f"The error '{e}' occurred")
        finally:
            cursor.close()
            connection.close()
    return False


@app.route('/')
def login_form():
    # GETリクエストの処理: ログインフォームを表示
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # POSTリクエストの処理: ログインフォームからのデータを処理
    username = request.form['username']
    password = request.form['password']

    if authenticate_user(username, password):
        # ログイン成功
        session['username'] = username
        print("@91",session)

        # @91 <FileSystemSession {'_permanent': True, 'username': 'sugizaki555', 'Q_no': 1, 'correct_ans': {'ペンギン', 'スズメ', 'カモメ'}}>
        return redirect(url_for('loginok'))  # ログイン後のページにリダイレクト
    else:
        return render_template("error.html")



@app.route('/logout')
def logout():
    # セッションからユーザー名を削除してログアウト
    session.pop('username', None)
    session.clear()
    print("ログアウト終了")
    # return redirect(url_for('login_form'))
    return "終わったよ"

@app.route('/loginok')
def loginok():
    session["Q_no"] = 0
    # return redirect('/question', code=302)
    return redirect(url_for('admin'))

@app.route('/admin')
def admin():
    print("管理者画面に飛んできました")
    return render_template('admin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        connection = create_db_connection()
        if connection is not None:
            try:
                cursor = connection.cursor()
                query = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
                cursor.execute(query, (username, hashed_password))
                connection.commit()
                cursor.close()
                connection.close()
                return redirect(url_for('login_form'))  # 登録後にログイン画面にリダイレクト
            except sqlite3.Error as e:
                print(f"The error '{e}' occurred")
                return render_template("error.html")
    return render_template("signup.html")

@app.route('/question') #questionが飛んできたらプログラムが実行
def question():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        print(f"@140= {session=}")
        Q_no = session["Q_no"]
        print("Q_no=",Q_no)
        q1 = sets[Q_no]
        
        # q1= ["問題1 今月は何月ですか？", "6月:7月:8月:9月:10月:11月:12月", "10月", "説明1"]
        print(q1[0])  # 質問文の表示

        arr = q1[1].split(":")  # 解答群の作成　多数の中から４つをランダムで選択
        print("arr=",arr)
        if len(arr) < 4:
            crs = len(arr)
        else:
            crs = 4    
        result = random.sample(arr, crs)
        
        for i, choice in enumerate(result, 1):
            print(i, choice)
        
        cs_temp = set(q1[2].split(":")) #正解をここで作っておく　["ペンギン","カモメ","スズメ"]
        correct_choices = set(result) & cs_temp #setは集合体　
        session["correct_ans"] = correct_choices #sessionの中にキーとバリューを入れる
        print(f"@165: correct_choices={correct_choices}")  # デバッグ用ログ出力
        start_datetime = datetime.now() #今現在の日付型を取得する
        formatted_date_string = start_datetime.strftime('%Y-%m-%d %H:%M:%S') #日付型を文字列に変換する
        session["start_datetime"] = formatted_date_string #文字列にしたことでセッションに保存できる
        print(f"開始時刻: {start_datetime}")
        return render_template('question.html', question=q1[0], choices=result)

@app.route('/answer', methods=['GET']) #answerが飛んできたら下のプログラムが実行
def check_answer():
    correct_ans = session.get("correct_ans", set())
    print(f"correct_ans={correct_ans}")  # デバッグ用ログ出力
    # correct_ans=session["correct_ans"]
    print("correct_ans=",correct_ans)
    user_choice = request.args.getlist('choice[]')
    end_datetime = datetime.now()
    print(f"終了時刻: {end_datetime}")
    print(f"@200:{session = } ")
    date_string = session["start_datetime"]
    start_datetime = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    elapsed_time = end_datetime - start_datetime
    print(f"{elapsed_time=}")
    elapsed_time_str = str(elapsed_time)
    print(f"@209{elapsed_time_str=}")
    print("user_choice=",user_choice)
    # print(f"経過時間: {elapsed_time}")

    correct_set = correct_ans 
    user_set = set(user_choice) #右がbefore、左はafter


    if user_set == correct_set:
        print("正解")
        answer = "正解"
    else:
        if correct_ans:
            print(f"不正解。正しい答えは: {correct_ans}")
            answer = f"不正解。正しい答えは: {', '.join(correct_ans)}"
        else:
            answer = "不正解"

    #Qをプラス
    Q = session["Q_no"]
    Q = Q + 1
    session["Q_no"]=Q
    return render_template('kekka.html',et=elapsed_time_str, kekka=answer,Q_no=Q)

# 以下、質問ページなどのルートは省略

if __name__ == "__main__":
    app.run(debug=True, port=8888)
