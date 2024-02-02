import bs4
import time
import pandas as pd
from PIL import Image,ImageFont,ImageDraw
import os
import requests  
import bs4
import time
import pandas as pd
import datetime
import urllib.parse
import datetime
from dotenv import load_dotenv
load_dotenv(".env")

def post_line_image_and_text(message,image_path,line_token):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization" : "Bearer "+ line_token}
    payload = {"message" :  message}
    #imagesフォルダの中のgazo.jpg
    print('image_path',image_path)
    files = {"imageFile":open(image_path,'rb')}
    post = requests.post(url ,headers = headers ,params=payload,files=files)

def post_line_text(message,line_token):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization" : "Bearer "+ line_token}
    payload = {"message" :  message}
    post = requests.post(url ,headers = headers ,params=payload)

def scraping_yesterday_groupby_prefecture_tenpo_data(prefecture:str) -> str:
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    date = yesterday.strftime('%Y-%m-%d')
    print(date)
    quote_prefecture = urllib.parse.quote(prefecture)
    url = f'https://ana-slo.com/{date}-{quote_prefecture}-hallpickup/'
    #print(url)    res = requests.get(url_1)
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    dfs = pd.read_html(res.text)
    concat_df = pd.DataFrame(columns=[],index=[])
    main_content = soup.find(True, class_='entry-content')
    div_list = main_content.find_all(True, class_='')
    for i,div in enumerate(div_list):
        #print(i,str(div))
        if '<div>' in str(div):
            try:
                #print(div.find('a').text)
                concat_df
                tenpo_name = div.find('a').text
                _df = pd.read_html(str(div))[0]
                _df['店舗名'] = tenpo_name
                concat_df = pd.concat([concat_df,_df],axis=0) 
            except:
                pass
    emoji_list = ['🥇','🥈','🥉','🎖','🎖']
    #文字列 昨日を曜日も加えてstr型に変換
    week = ['月','火','水','木','金','土','日']
    date = yesterday.strftime('%m').lstrip('0') + '月' + yesterday.strftime('%d').lstrip('0') + '日' \
    + '(' + week[yesterday.weekday()] + ')'
    #print(date)

    data_text =''
    for emoji ,(i,row) in zip(emoji_list,concat_df.iterrows()):
        #print(i,row)
        tenpo_name = row['店舗名']
        sum_medal = '{:,}'.format(round(int(row['総差枚']), -2))
        if int(row['総差枚']) > 0:
            sum_medal = '+' + sum_medal + '枚'

        ave_medal = str(row['平均差枚']) 
        if int(row['平均差枚']) > 0:
            ave_medal = '+' + ave_medal + '枚'
        daisuu = row['勝率'].split('(')[1].replace(')','')+ '台'
        data_text += f'{emoji}{tenpo_name}\n 総差{sum_medal} 平均{ave_medal} {daisuu}\n'
    #print(data_text)

    output_text = f'''\n\n\n〈{date}速報〉\n【{prefecture.replace('都','').replace('県','')} 平均差枚ランキングTOP5】\n\n'''
    #print(output_text)
    output_text += data_text
    #print(output_text)
    return output_text



import time         # タイマー用
import traceback    # 例外検知用
for _ in range(5):  # 最大3回実行
    try:
        for prefecture in ['神奈川県','埼玉県','千葉県','東京都']:
            output_text = scraping_yesterday_groupby_prefecture_tenpo_data(prefecture)
            post_line_text(output_text,os.getenv('SLOCHAN_LINE_TOKEN'))
            time.sleep(3)

    except Exception as e:
        post_line_text(f"{e} 失敗しました。もう一度繰り返します",os.getenv('SLOCHAN_LINE_TOKEN'))
        print(traceback.format_exc()) # 例外の内容を表示
        time.sleep(3600) # 適当に待つ
    else:
        print("成功しました。ループを終了します。")
        break
else:
    post_line_text("最大試行回数に達しました。処理を中断します",os.getenv('SLOCHAN_LINE_TOKEN'))
    