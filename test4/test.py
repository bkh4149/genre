syukei_dic={'雑学': {'総数': 10, 'ids': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}, '日時': {'総数': 1, 'ids': [0]}, '動物': {'総数': 1, 'ids': [1]}, '天体': {'総数': 2, 'ids': [2, 8]}, '地理': {'総数': 2, 'ids': [3, 6]}, '食物': {'総数': 1, 'ids': [4]}, '言語': {'総数': 1, 'ids': [5]}, 'スペイン語': {'総数': 1, 'ids': [5]}, '美術': {'総数': 1, 'ids': [7]}, '通貨': {'総数': 1, 'ids': [9]}, '経済': {'総数': 1, 'ids': [9]}}

import random
j=input("ジャンル")
print(syukei_dic[j] )
n=syukei_dic[j]["総数"]
ids=syukei_dic[j]["ids"]

print(n,ids)
random.shuffle(ids)
print(f"{ids=}")

# import random

# # 元のリスト
# original_list = [2, 3, 4, 5]

# # リストをシャッフル
# random.shuffle(original_list)

# # 結果を表示
# print(original_list)