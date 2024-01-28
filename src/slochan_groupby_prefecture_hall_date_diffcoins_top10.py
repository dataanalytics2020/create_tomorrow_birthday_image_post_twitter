# Purpose: 都道府県別のホール別の日別の差枚数の平均値のTOP10をLINEに送信する
#12:35分にタスクスケジューラーをセット中
import requests  
import requests
import bs4
import time
import pandas as pd
import datetime
import urllib.parse
from bs4 import BeautifulSoup


from bs4 import BeautifulSoup
import urllib.parse
import os
import traceback
import mysql
import mysql.connector
from dotenv import load_dotenv
load_dotenv(".env")

SLOCHAN_LINE_TOKEN = os.environ.get("SLOCHAN_LINE_TOKEN")
print(SLOCHAN_LINE_TOKEN)
print('読み込み完了')
time.sleep(4)
def get_cursor():
    # MySQLに接続
    conn = mysql.connector.connect(
        host=os.environ.get("AWS_SLOMAP_RDS_HOST"),
        user=os.environ.get("AWS_SLOMAP_RDS_USER"),
        password=os.environ.get("AWS_SLOMAP_RDS_PASSWORD"),
        database=os.environ.get("AWS_SLOMAP_RDS_DATABASE"),
    )
    return conn


def post_line_text(message,SLOCHAN_LINE_TOKEN):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization" : "Bearer "+ SLOCHAN_LINE_TOKEN}
    payload = {"message" :  message}
    post = requests.post(url ,headers = headers ,params=payload)

# MySQLに接続
conn = get_cursor()
# カーソルを取得
#昨日のデータを取得
target_day_num = 1
cursor = conn.cursor()
sql = f'''SELECT *
            FROM groupby_date_hall_diffcoins 
            WHERE date = DATE_SUB(CURDATE(), INTERVAL {target_day_num} DAY)
            '''
print(sql)
cursor.execute(sql)
result = cursor.fetchall()
hall_status_df = pd.DataFrame(result, columns=[col for col in cursor.column_names])
#display(hall_status_df)
hall_status_df['hall_name'] = hall_status_df['hall_name'].map(lambda x:x.replace('　','').replace(' ','').replace('日拓','').replace('駅前','').replace('TOYO','TOYOHALL'))
for prefecture_name in ['埼玉県', '千葉県', '神奈川県','東京都']:#
    try:
        extract_prefecture_df = hall_status_df[hall_status_df['prefecture'] == prefecture_name]
        #display(extract_prefecture_df)
        extract_prefecture_df.sort_values('ave_diffcoins', ascending=False, inplace=True)
        if prefecture_name == '東京都':
            compare_diffcoins = 50
        else:
            compare_diffcoins = 0
        extract_prefecture_df_1 = extract_prefecture_df[extract_prefecture_df['ave_diffcoins'] > compare_diffcoins]
        extract_prefecture_df_1
        yesterday = datetime.date.today() - datetime.timedelta(days=target_day_num)
        date = yesterday.strftime('%Y-%m-%d')
        emoji_list = ['🥇','🥈','🥉','⭐️','⭐️']
        for _ in range(len(extract_prefecture_df_1)-5):
            emoji_list.append("⭐️")
        #文字列 昨日を曜日も加えてstr型に変換
        week = ['月','火','水','木','金','土','日']
        date = yesterday.strftime('%m').lstrip('0') + '月' + yesterday.strftime('%d').lstrip('0') + '日' \
        + '(' + week[yesterday.weekday()] + ')'
        #print(date)

        data_text =''
        for emoji ,(i,row) in zip(emoji_list,extract_prefecture_df_1.iterrows()):
            #print(i,row)
            tenpo_name = row['hall_name']
            
            if '本店' in tenpo_name:
                tenpo_name = tenpo_name.replace('本店','')
            elif '店' in tenpo_name:
                tenpo_name = tenpo_name.replace('店','')
            else:
                pass
            sum_medal = '{:,}'.format(round(int(row['sum_diffcoins']), -2))
            if int(row['sum_diffcoins']) > 0:
                sum_medal = '+' + sum_medal + '枚'

            ave_medal = str(row['ave_diffcoins']) 
            if int(row['ave_diffcoins']) > 0:
                ave_medal = '+' + ave_medal + '枚'
            daisuu = row['win_rate'].split(')')[0].replace('台','\n').replace('(','')
            data_text += f'{emoji}{tenpo_name}\n 総差{sum_medal} 平均{ave_medal} {daisuu}\n\n'
        #print(data_text)

        output_text = f'''〈{date}速報〉\n【{prefecture_name} 平均差枚ランキング】※{compare_diffcoins}枚以上抜粋\n\n'''
        #print(output_text)
        output_text += data_text
        print(output_text)

        #文字が900文字を超えたら送信
        if len(output_text) < 900:
            post_line_text(output_text,SLOCHAN_LINE_TOKEN)
            #time.sleep(10)
        else:
            concat_text = ''
            for text_line in output_text.split('\n\n'):
                concat_text += text_line + '\n'
                if len(concat_text) > 900:
                    post_line_text(concat_text,SLOCHAN_LINE_TOKEN)
                    concat_text = ''
                    #time.sleep(10)
            post_line_text(concat_text,SLOCHAN_LINE_TOKEN)
        #break
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        time.sleep(10)
        error_text = traceback.format_exc()
        post_line_text(f'{prefecture_name} {error_text}',SLOCHAN_LINE_TOKEN)