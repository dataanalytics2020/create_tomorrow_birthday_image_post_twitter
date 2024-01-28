import requests  
import requests
import bs4
import time
import re
import pandas as pd
from PIL import Image,ImageFont,ImageDraw
import os
import traceback
import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv(".env")

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
    #font = ImageFont.truetype('font/NotoSansJP-Black.otf', 20)
    df_columns_list = list(_df.columns)
    cell_height = 40
    for column_number in range(len(_df.columns)):
        height_concat_lists = []
        #print(column_number)
        #print(df_columns_list[column_number])
        if df_columns_list[column_number] == 'キャラクター名':
            font = ImageFont.truetype('font/NotoSansJP-Black.otf', 26)
            cell_width = 600
            cell_height = 40
        elif df_columns_list[column_number] == '登場作品':
            font = ImageFont.truetype('font/NotoSansJP-Black.otf', 26)
            cell_width = 600
            cell_height = 40

        elif df_columns_list[column_number] == '声優':
            font = ImageFont.truetype('font/NotoSansJP-Black.otf', 38)
            cell_width = 600
            cell_height = 50
        elif df_columns_list[column_number] == '何の日？':
            font = ImageFont.truetype('font/NotoSansJP-Black.otf', 20)
            cell_width = 500
            cell_height = 60
        elif df_columns_list[column_number] == '日付':
            cell_width = 120
            cell_height = 60
            font = ImageFont.truetype('font/NotoSansJP-Black.otf', 20)
        else:
            cell_width = 300
            font = ImageFont.truetype('font/NotoSansJP-Black.otf', 20)
            cell_height = 60
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
        seiyuu_count = 1
        for index_number ,(i,record) in enumerate(_df.iterrows()):
            #print('df_columns_list[column_number]',df_columns_list[column_number])
            
            if index_number == 0 and df_columns_list[column_number] == '声優':
                if len(_df) != 1:
                    name = f'{record[column_number]}'
                    continue
                else:
                    name = f'{record[column_number]}'
                    im = Image.new('RGB', (cell_width, (count*cell_height)), (255, 255, 255))
                    draw = ImageDraw.Draw(im) 
                    w, h = im.size
                    draw.multiline_text(((cell_width)/2,(count*cell_height)/2), f'{name[:15]}', fill=(0,0,0), font=font,anchor="mm",align ="center")
                    draw.rectangle((0, 0, w-1, h-1), outline = (0,0,0))
                    height_concat_lists.append(im)
                    count = 1
                    continue

            if df_columns_list[column_number] == '声優':
                print('name',name)

                im = Image.new('RGB', (cell_width, (count*cell_height)), (255, 255, 255))
                draw = ImageDraw.Draw(im) 
                print('record[column_number',record[column_number])
                font = ImageFont.truetype('font/NotoSansJP-Black.otf', 32)

                if name == f'{record[column_number]}':
                    print('同じ名前',count)
                    count += 1
                else:
                    print('違う名前',count)
                    print((count*cell_height))
                    w, h = im.size
                    draw.multiline_text(((cell_width)/2,(count*cell_height)/2), f'{name[:15]}', fill=(0,0,0), font=font,anchor="mm",align ="center")
                    draw.rectangle((0, 0, w-1, h-1), outline = (0,0,0))
                    height_concat_lists.append(im)
                    count = 1
                    
                name = f'{record[column_number]}'
                if index_number+1 == len(cv_birthday_df):
                    im = Image.new('RGB', (cell_width, (count*cell_height)), (255, 255, 255))
                    draw = ImageDraw.Draw(im) 
                    w, h = im.size
                    draw.multiline_text(((cell_width)/2,(count*cell_height)/2), f'{name[:15]}', fill=(0,0,0), font=font,anchor="mm",align ="center")
                    draw.rectangle((0, 0, w-1, h-1), outline = (0,0,0))
                    height_concat_lists.append(im)
                    count = 1
                seiyuu_count += 1
            elif df_columns_list[column_number] == '何の日？':
                im = Image.new('RGB', (cell_width, cell_height), (221, 255, 255)) 
                draw = ImageDraw.Draw(im)  # Drawオブジェクトを生成  
                font = ImageFont.truetype('font/NotoSansJP-Black.otf', 13)
                output_text = ''
                text_list = record[column_number].split('。')
                for i,text in enumerate(text_list):
                    i += 1
                    #print(text)
                    if i > 11:
                        break
                    if i % 4 == 0:
                        output_text += '\n'+ text + ' '
                    else:
                        output_text += text + ' '
                print(output_text)
                draw.multiline_text((cell_width/2,cell_height/2), f'{output_text}', spacing= 0,fill=(0,0,0), font=font,anchor="mm",align ="center") 
                w, h = im.size
                draw.rectangle((0, 0, w-1, h-1), outline = (0,0,0))
                height_concat_lists.append(im)# イメージオブジェクトの生成(黒のベタ画像)

            else:
                if (index_number + 1 ) %  2 != 0:
                    im = Image.new('RGB', (cell_width, cell_height), (255, 255, 255))  # イメージオブジェクトの生成(黒のベタ画像)
                else:
                    im = Image.new('RGB', (cell_width, cell_height), (221, 255, 255))  # イメージオブジェクトの生成(黒のベタ画像)
                draw = ImageDraw.Draw(im)  # Drawオブジェクトを生成  
                name = record[column_number]
                print
                if 16 < len(name):
                    font = ImageFont.truetype('font/NotoSansJP-Black.otf', 18)
                else:
                    font = ImageFont.truetype('font/NotoSansJP-Black.otf', 24)
                

                draw.multiline_text((cell_width/2,cell_height/2), f'{name}', fill=(0,0,0),spacing= -6, font=font,anchor="mm",align ="center") 
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

def keepAspectResize(path, size):

    # 画像の読み込み
    image = Image.open(path)

    # サイズを幅と高さにアンパック
    width, height = size

    # 矩形の幅と画像の幅の比率を計算
    x_ratio = width / image.width

    # 矩形の高さと画像の高さの比率を計算
    y_ratio = height / image.height

    # 画像の幅と高さ両方に小さい方の比率を掛けてリサイズ後のサイズを計算
    if x_ratio < y_ratio:
        resize_size = (width, round(image.height * x_ratio))
    else:
        resize_size = (round(image.width * y_ratio), height)

    # リサイズ後の画像サイズにリサイズ
    resized_image = image.resize(resize_size)

    return resized_image

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


for day in range(1,5):
    try:
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=day)
        url = f'https://sulocale.sulopachinews.com/archives/%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88/{tomorrow.strftime("%m%d")}'
        print(url)
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        s = str(soup)
        reg = '<rt>.*?</rt>'
        print(re.findall(reg, s))
        rt_list = re.findall(reg, s)    
        # ['{123}', '{abc}']
        soup_str = str(soup)
        for replace_str in rt_list: 
            soup_str = soup_str.replace(replace_str, '')
        soup = BeautifulSoup(soup_str, 'html.parser')
        birthday_dfs = pd.read_html(soup.prettify())
        print(birthday_dfs)
        #pd.DataFrame(columns=['month', 'day', 'name','affiliation'])
        # for df in birthday_dfs:
        #     Zprint(df)

        charactor_birthday_df = pd.DataFrame(columns=[ 'キャラクター名','登場作品'])
        for text in birthday_dfs[0][0][1:]:
            text = text.replace(')','）').replace('？','').replace('(','（')
            charactor_name = text.split('（')[0].replace(' ','').replace(' ','')
            try:
                charactor_affiliation = text.split('（')[1].replace('(仮','(仮)').replace('）','')
            except:
                charactor_affiliation = '-'
            print(charactor_name,charactor_affiliation)
            charactor_birthday_df = pd.concat([charactor_birthday_df,pd.DataFrame({'キャラクター名':[charactor_name],'登場作品':[charactor_affiliation]})],axis=0)
        charactor_birthday_df = charactor_birthday_df[charactor_birthday_df['登場作品'] != '-']
        cv_birthday_df = pd.DataFrame(columns=[ '声優','キャラクター名','登場作品'])
        for i in range(1,len(birthday_dfs)):
            temp__birthday_df = birthday_dfs[i]
            #print(temp__birthday_df)
            try:
                vc_name = temp__birthday_df.loc[0][0].split('歳')[0].replace('（型）','').rstrip('さん')
                vc_name = vc_name.replace(' ','').replace(' ','').replace('？','')
                vc_name = "".join([i for i in vc_name if not i.isdigit()])
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
        extract_universary_df = extract_universary_df[:1]


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
        #img_resize = img.resize((1500, 2000))  # 画像のリサイズ

        # 画像のアスペクト比を維持したまま、指定したサイズに収まるようにリサイズ
        img_resize = img.resize((2000, int(2000 * img.size[1] / img.size[0])))  # 画像のリサイズ
        print("変更後の画像サイズ　width: {}, height: {}".format(img_resize.size[0], img_resize.size[1]))  # 変更後の画像のサイズ出力

        img_resize.save(concat_image_path) 


        try:
            birthday = extract_universary_df['日付'].iloc[0]
        except:
            birthday = tomorrow.strftime("%m月").lstrip('0') + tomorrow.strftime("%d日").lstrip('0')
        # text = f'\n\n{birthday} 明日は何の日？'
        # text += '\n◆キャラクターの誕生日一覧'
        # virtday_count_dict = dict(charactor_birthday_df['登場作品'].value_counts())
        # birthday_dict_tuple = sorted(virtday_count_dict.items(), key=lambda x:x[1], reverse=True)
        # for affitation in birthday_dict_tuple:
        #     print(affitation[0])
        #     extract_df = charactor_birthday_df[charactor_birthday_df['登場作品'] == affitation[0]]
        #     print(extract_df)
        #     text += f'\n📍{affitation[0]}'
        #     for index, row in extract_df.iterrows():
        #         text += f'\n｜{row["キャラクター名"]}'
        # print(text) 

        # text += '\n\n◆声優の誕生日一覧'

        # for affitation in cv_birthday_df['声優'].unique():
        #     print(affitation[0])
        #     extract_df = cv_birthday_df[cv_birthday_df['声優'] == affitation]
        #     print(extract_df)
        #     text += f'\n📍{affitation}'
        #     for index, row in extract_df.iterrows():
        #         text += f'\n｜{row["キャラクター名"]} {row["登場作品"]}'
        # print(text)

        post_line_image_and_text(birthday,concat_image_path, os.getenv('LINE_TOKEN'))
        #break
    except Exception as e:
        print(e)
        error_text = traceback.format_exc()
        post_line_text(f"{error_text} 失敗しました。",os.getenv('LINE_TOKEN'))
        print(traceback.format_exc())
        #break