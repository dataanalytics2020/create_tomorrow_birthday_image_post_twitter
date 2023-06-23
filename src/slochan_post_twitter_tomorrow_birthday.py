import requests  
import requests
import bs4
import time
import pandas as pd
from PIL import Image,ImageFont,ImageDraw
import os

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


today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
url = f'https://sulocale.sulopachinews.com/archives/%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88/{tomorrow.strftime("%m%d")}'
print(url)
birthday_dfs = pd.read_html(url)
birthday_dfs
#pd.DataFrame(columns=['month', 'day', 'name','affiliation'])
# for df in birthday_dfs:
#     Zprint(df)

charactor_birthday_df = pd.DataFrame(columns=[ 'キャラクター名','登場作品'])
for text in birthday_dfs[0][0][1:]:
    text = text.replace(')','）').replace('？','')
    charactor_name = text.split('（')[0].replace(' ','').replace(' ','')
    charactor_affiliation = text.split('（')[1].replace('(仮','(仮)').replace('）','')
    print(charactor_name,charactor_affiliation)
    charactor_birthday_df = pd.concat([charactor_birthday_df,pd.DataFrame({'キャラクター名':[charactor_name],'登場作品':[charactor_affiliation]})],axis=0)
    
cv_birthday_df = pd.DataFrame(columns=[ '声優','キャラクター名','登場作品'])
for i in range(1,len(birthday_dfs)):
    temp__birthday_df = birthday_dfs[i]
    #print(temp__birthday_df)
    try:
        vc_name = temp__birthday_df.loc[0][0].lstrip('？').split(' ')[1].replace('（型）','').rstrip('さん')
        vc_name = vc_name.replace(' ','').replace(' ','')

        for n in range(1,len(temp__birthday_df)):
            text = temp__birthday_df.loc[n][0].replace(')','）').replace('？','')
            charactor_name = text.split('（')[0].replace(' ','').replace(' ','')
            charactor_affiliation = text.split('（')[1].replace('(仮','(仮)').replace('）','')
            cv_birthday_df = pd.concat([cv_birthday_df,pd.DataFrame({'声優':[vc_name],'キャラクター名':[charactor_name],'登場作品':[charactor_affiliation]})],axis=0)
        #break
    except Exception as e:
        print(e)
        continue
cv_birthday_df

url = 'https://netwadai.com/blog/post-2363'
universary_df  = pd.read_html(url)[0]
universary_df = universary_df.rename(columns={0:'日付',1:'何の日？'})
universary_df = universary_df[~universary_df['日付'].str.contains('記念日一覧')]
universary_df = universary_df[~universary_df['日付'].str.contains('2月29日')]
#pd.DataFrame(columns=['month', 'day', 'name','affiliation'])
print(universary_df)
tomorrow_str:str = tomorrow.strftime("%m月").lstrip('0') + tomorrow.strftime("%d日").lstrip('0') 
extract_universary_df = universary_df[universary_df['日付'].str.contains(tomorrow_str)]
extract_universary_df




def get_concat_h_multi_resize(im_list, resample=Image.BICUBIC):
    min_height = min(im.height for im in im_list)
    im_list_resize = [im.resize((int(im.width * min_height / im.height), min_height),resample=resample)
                    for im in im_list]
    total_width = sum(im.width for im in im_list_resize)
    dst = Image.new('RGB', (total_width, min_height))
    pos_x = 0
    for im in im_list_resize:
        dst.paste(im, (pos_x, 0))
        pos_x += im.width
    return dst

def get_concat_v_multi_resize(im_list, resample=Image.BICUBIC):
    min_width = min(im.width for im in im_list)
    im_list_resize = [im.resize((min_width, int(im.height * min_width / im.width)),resample=resample)
                    for im in im_list]
    total_height = sum(im.height for im in im_list_resize)
    dst = Image.new('RGB', (min_width, total_height))
    pos_y = 0
    for im in im_list_resize:
        dst.paste(im, (0, pos_y))
        pos_y += im.height
    return dst

def create_charactor_anime_cell_image(_df,image_name):
    global create_df_cell_image_path
    width_concat_lists = []
    font = ImageFont.truetype('font/NotoSansJP-Black.otf', 20)
    df_columns_list = list(_df.columns)
    cell_height = 40
    for column_number in range(len(_df.columns)):
        height_concat_lists = []
        #print(column_number)
        #print(df_columns_list[column_number])
        if df_columns_list[column_number] == 'キャラクター名':
            
            cell_width = 500
        elif df_columns_list[column_number] == '登場作品':
            cell_width = 500
        elif df_columns_list[column_number] == '声優':
            font = ImageFont.truetype('font/NotoSansJP-Black.otf', 38)
            cell_width = 500
            cell_height = 60
        elif df_columns_list[column_number] == '何の日？':
            font = ImageFont.truetype('font/NotoSansJP-Black.otf', 13)
            cell_width = 500
            cell_height = 25
        elif df_columns_list[column_number] == '日付':
            cell_width = 100
            cell_height = 25
        else:
            cell_width = 300
            font = ImageFont.truetype('font/NotoSansJP-Black.otf', 20)
            cell_height = 40
        #print(cell_width,cell_height)
        im = Image.new('RGB', (cell_width, cell_height), (0, 0, 200))  # イメージオブジェクトの生成(黒のベタ画像)
        draw = ImageDraw.Draw(im)  # Drawオブジェクトを生成  
        # フォントの指定(メイリオ48pt)
        w, h = im.size
        draw.multiline_text((cell_width/2,cell_height/2), df_columns_list[column_number], fill=(255,255,255), font=font, align ="center",anchor="mm") # 文字の描画
        w, h = im.size
        draw.rectangle((0, 0, w-1, h-1), outline = (255,255,255))
        height_concat_lists.append(im)
        name = '' #cv_birthday_df['声優'].iloc[0]
        count = 1
        for index_number ,(i,record) in enumerate(_df.iterrows()):
            #print('df_columns_list[column_number]',df_columns_list[column_number])
            if index_number == 0 and df_columns_list[column_number] == '声優':
                name = f'{record[column_number]}'
                continue
            if df_columns_list[column_number] == '声優':
                print('name',name)
                print('record[column_number',record[column_number])
                font = ImageFont.truetype('font/NotoSansJP-Black.otf', 32)
                if name == f'{record[column_number]}':
                    print('同じ名前',count)
                    count += 1
                else:
                    print('違う名前',count)
                    print((count*cell_height))
                    im = Image.new('RGB', (cell_width, (count*cell_height)), (255, 255, 255))
                    draw = ImageDraw.Draw(im) 
                    w, h = im.size
                    draw.multiline_text(((cell_width)/2,(count*cell_height)/2), f'{name}', fill=(0,0,0), font=font,anchor="mm",align ="center")
                    draw.rectangle((0, 0, w-1, h-1), outline = (0,0,0))
                    height_concat_lists.append(im)
                    count = 1
                name = f'{record[column_number]}'
                if index_number+1 == len(cv_birthday_df):
                    im = Image.new('RGB', (cell_width, (count*cell_height)), (255, 255, 255))
                    draw = ImageDraw.Draw(im) 
                    w, h = im.size
                    draw.multiline_text(((cell_width)/2,(count*cell_height)/2), f'{name}', fill=(0,0,0), font=font,anchor="mm",align ="center")
                    draw.rectangle((0, 0, w-1, h-1), outline = (0,0,0))
                    height_concat_lists.append(im)
                    count = 1
            elif df_columns_list[column_number] == '何の日？':
                im = Image.new('RGB', (cell_width, cell_height), (221, 255, 255)) 
                draw = ImageDraw.Draw(im)  # Drawオブジェクトを生成  
                font = ImageFont.truetype('font/NotoSansJP-Black.otf', 13)
                draw.multiline_text((cell_width/2,cell_height/2), f'{record[column_number]}', fill=(0,0,0), font=font,anchor="mm",align ="center") 
                w, h = im.size
                draw.rectangle((0, 0, w-1, h-1), outline = (0,0,0))
                height_concat_lists.append(im)# イメージオブジェクトの生成(黒のベタ画像)

            else:
                if (index_number + 1 ) %  2 != 0:
                    im = Image.new('RGB', (cell_width, cell_height), (255, 255, 255))  # イメージオブジェクトの生成(黒のベタ画像)
                else:
                    im = Image.new('RGB', (cell_width, cell_height), (221, 255, 255))  # イメージオブジェクトの生成(黒のベタ画像)
                draw = ImageDraw.Draw(im)  # Drawオブジェクトを生成  
                
                draw.multiline_text((cell_width/2,cell_height/2), f'{record[column_number]}', fill=(0,0,0), font=font,anchor="mm",align ="center") 
                w, h = im.size
                draw.rectangle((0, 0, w-1, h-1), outline = (0,0,0))
                height_concat_lists.append(im)
            
        #break
        concat_image_path  = rf"image/temp_image/complted_cell_{column_number}.png"
        get_concat_v_multi_resize(height_concat_lists).save(concat_image_path)
        concat_im = Image.open(concat_image_path)
        width_concat_lists.append(concat_im)
    create_df_cell_image_path = rf"image/temp_image/temp_complted_df_image_cell_{image_name}.png"
    get_concat_h_multi_resize(width_concat_lists).save(create_df_cell_image_path)
    return create_df_cell_image_path

completed_height_concat_lists = []
concat_im = Image.open('image/header_image.png')
completed_height_concat_lists.append(concat_im)

concat_image_path = create_charactor_anime_cell_image(extract_universary_df,'テスト3')
concat_im = Image.open(concat_image_path)
completed_height_concat_lists.append(concat_im)

concat_image_path = create_charactor_anime_cell_image(charactor_birthday_df,'テスト1')
concat_im = Image.open(concat_image_path)
completed_height_concat_lists.append(concat_im)

concat_image_path = create_charactor_anime_cell_image(cv_birthday_df,'テスト2')
concat_im = Image.open(concat_image_path)
completed_height_concat_lists.append(concat_im)

concat_image_path  = rf"image/temp_image/complted_image_1.png"
get_concat_v_multi_resize(completed_height_concat_lists).save(concat_image_path)

img = Image.open(concat_image_path)  # イメージを開く
print("元の画像サイズ　width: {}, height: {}".format(img.size[0], img.size[1]))  # 元の画像のサイズ出力
# 画像を指定したサイズに変更
img_resize = img.resize((1500, 2000))  # 画像のリサイズ
print("指定サイズ　width: {}, height: {}".format(img_resize.size[0], img_resize.size[1]))  # 画像のサイズ出力
img_resize.save(concat_image_path) 


birthday = extract_universary_df['日付'].iloc[0]
text = f'\n\n{birthday} 今日は何の日？'
text += '\n◆キャラクターの誕生日一覧'
virtday_count_dict = dict(charactor_birthday_df['登場作品'].value_counts())
birthday_dict_tuple = sorted(virtday_count_dict.items(), key=lambda x:x[1], reverse=True)
for affitation in birthday_dict_tuple:
    print(affitation[0])
    extract_df = charactor_birthday_df[charactor_birthday_df['登場作品'] == affitation[0]]
    print(extract_df)
    text += f'\n{affitation[0]}'
    for index, row in extract_df.iterrows():
        text += f'\n・{row["キャラクター名"]}'
print(text) 

text += '\n\n◆声優の誕生日一覧'

for affitation in cv_birthday_df['声優'].unique():
    print(affitation[0])
    extract_df = cv_birthday_df[cv_birthday_df['声優'] == affitation]
    print(extract_df)
    text += f'\n{affitation}'
    for index, row in extract_df.iterrows():
        text += f'\n・{row["キャラクター名"]} {row["登場作品"]}'
print(text)

post_line_image_and_text(text,concat_image_path, os.getenv('LINE_TOKEN'))
