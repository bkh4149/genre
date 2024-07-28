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

#最初に動くところ グローバル変数になっている
with open('quiz_questions.txt', 'r', encoding='utf-8') as file:
    content = file.read().strip()
questions = content.split('\n\n')
#print(f"app@44 {questions=}")
Qrecords = []#Qrecordを集めたもの
#Qrecords=[['1', '雑学:日時', '問題1 今月は何月ですか？', '4月:5月:6月:7月:8月:9月:10月:11月:12月:1月:2月:3月', '6月', '説明1'], ['2',,,,,], ['3',,,,,], ['4',,,,,]]
genreBasedQDic={}
for i,question in enumerate(questions):
    Qrecord = question.split('\n')
    #print(f"app@50 {Qrecord=}")
    # Qrecord=['4', '雑学:地理', '問題4 日本の首都は？', '大阪:東京:福岡:仙台:青森:広島:盛岡', '東京', '日本の首都は東京です。']
    if len(Qrecord) == 6:
        Qrecords.append(Qrecord)
        #print(f"app@54 {Qrecords=}")
        genreList = Qrecord[1].split(":")#１行目のジャンルの要素を取り出し、分解,配列化
        for genre in genreList:#ジャンルの集計
            if genre in genreBasedQDic:
                genreBasedQDic[genre]["総数"]+=1
                genreBasedQDic[genre]["ids"].append(i)
            else:
                genreBasedQDic[genre]={"総数":1,"ids":[i]}

#print(f"@59 {Qrecords=}")
#print(f"app@61 {genreBasedQDic=}")
#genreBasedQDic={'雑学': {'総数': 7, 'ids': [0, 1, 2, 3, 4, 5, 6]}, '日時': {'総数': 1, 'ids': [0]}, '動物': {'総数': 1, 'ids': [1]},,,,}

def makeQMap(genreX):
    tmp=genreBasedQDic[genreX]["ids"]
    #print(f"@71 {tmp=}")
    n=min(3,genreBasedQDic[genreX]["総数"])
    genreBasedQMap= random.sample(tmp, n)
    print(f"@71 {genreBasedQMap=}")
    return genreBasedQMap

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
    return render_template('admin.html',genreBasedQDic=genreBasedQDic)

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


#最初の１問目だけここを通る
@app.route('/first_question', methods=[ 'POST']) 
def first_question():
    genreX = request.form.get('category',"none")
    print(f"@172 { genreX=}")
    genreBasedQMap = makeQMap(genreX)
    session["genreBasedQMap"] = genreBasedQMap
    session["Q_no"]=0
    return redirect(url_for('question'))


@app.route('/question') #questionが飛んできたらプログラムが実行
def question():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        #print(f"@140= {session=}")
        Q_no = session["Q_no"]
        genreBasedQMap = session["genreBasedQMap"]
        id_no = genreBasedQMap[Q_no]
        #print(f"@188 {Q_no=}  {genreBasedQMap=} {id_no=}")#@188 Q_no=0  genreBasedQMap=[5, 2, 4] id_no=5
        q1 = Qrecords[id_no]
        print(f"@190 {q1=}")#

        # q1= ["問題1 今月は何月ですか？", "6月:7月:8月:9月:10月:11月:12月", "10月", "説明1"]
        print(q1[2])  # 質問文の表示

        arr = q1[3].split(":")  # 解答群の作成　多数の中から４つをランダムで選択
        print("arr=",arr)
        if len(arr) < 4:
            crs = len(arr)
        else:
            crs = 4    
        result = random.sample(arr, crs)
        
        for i, choice in enumerate(result, 1):
            print(i, choice)
        
        cs_temp = set(q1[4].split(":")) #正解をここで作っておく　["ペンギン","カモメ","スズメ"]
        correct_choices = set(result) & cs_temp #setは集合体　
        session["correct_ans"] = correct_choices #sessionの中にキーとバリューを入れる
        print(f"@165: correct_choices={correct_choices}")  # デバッグ用ログ出力
        start_datetime = datetime.now() #今現在の日付型を取得する
        formatted_date_string = start_datetime.strftime('%Y-%m-%d %H:%M:%S') #日付型を文字列に変換する
        session["start_datetime"] = formatted_date_string #文字列にしたことでセッションに保存できる
        print(f"開始時刻: {start_datetime}")
        return render_template('question.html', question=q1[2], choices=result)

@app.route('/answer', methods=['GET']) #answerが飛んできたら下のプログラムが実行
def check_answer():
    correct_ans = session.get("correct_ans", set())
    # correct_ans=session["correct_ans"]
    print("correct_ans=",correct_ans)
    user_choice = request.args.getlist('choice[]')
    print("user_choice=",user_choice)
    print(f"{correct_ans=} {correct_ans=}")  # デバッグ用ログ出力


    # end_datetime = datetime.now()
    # print(f"終了時刻: {end_datetime}")
    # print(f"@200:{session = } ")
    # date_string = session["start_datetime"]
    # start_datetime = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    # elapsed_time = end_datetime - start_datetime
    # print(f"{elapsed_time=}")
    # elapsed_time_str = str(elapsed_time)
    # print(f"@209{elapsed_time_str=}")
    # print(f"経過時間: {elapsed_time}")
    elapsed_time_str="0"#test debug用　後で消す


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
