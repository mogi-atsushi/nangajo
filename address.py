# coding: utf-8
import os
import csv
import json
import requests
import sys
import re
from PIL import Image, ImageDraw, ImageFont

# Global Variables
inputfile = 'address.csv'
outputdir = 'output'
printval = '〇'
name_sep = '　'
names_sep = '、'
year = 2020
pref = False

# Specify the full path for the font files.
mincho = '/System/Library/Fonts/ヒラギノ明朝 ProN.ttc'
times = '/System/Library/Fonts/Times.ttc'

pat1 = '(...??[都道府県])((?:旭川|伊達|石狩|盛岡|奥州|田村|南相馬|那須塩原|東村山|武蔵村山|羽村|十日町|上越|富山|野々市|大町|蒲郡|四日市|姫路|大和郡山|廿日市|下>松|岩国|田川|大村|宮古|富良野|別府|佐伯|黒部|小諸|塩尻|玉野|周南)市|(?:余市|高市|[^市]{2,3}?)郡(?:玉村|大町|.{1,5}?)[町村]|(?:.{1,4}市)?[^町]{1,4}?区|.{1,7}?[市町村])(.+)'
pat2 = '((?:旭川|伊達|石狩|盛岡|奥州|田村|南相馬|那須塩原|東村山|武蔵村山|羽村|十日町|上越|富山|野々市|大町|蒲郡|四日市|姫路|大和郡山|廿日市|下>松|岩国|田川|大村|宮古|富良野|別府|佐伯|黒部|小諸|塩尻|玉野|周南)市|(?:余市|高市|[^市]{2,3}?)郡(?:玉村|大町|.{1,5}?)[町村]|(?:.{1,4}市)?[^町]{1,4}?区|.{1,7}?[市町村])(.+)'

class pycolor:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RETURN = '\033[07m' #反転
    ACCENT = '\033[01m' #強調
    FLASH = '\033[05m' #点滅
    RED_FLASH = '\033[05;41m' #赤背景+点滅
    END = '\033[0m'

def kansuji(s):
    s = s.replace('0','〇')
    s = s.replace('1','一')
    s = s.replace('2','二')
    s = s.replace('3','三')
    s = s.replace('4','四')
    s = s.replace('5','五')
    s = s.replace('6','六')
    s = s.replace('7','七')
    s = s.replace('8','八')
    s = s.replace('9','九')
    s = s.replace('-','｜')
    s = s.replace('ー','丨')
    return s

def get_pref(address):
    results = []
    if (pref):
        tmp = re.split(pat1, address)
        results.append(tmp[1])
        results.append(tmp[2])
        results.append(tmp[3])
    else:
        tmp = re.split(pat2, address)
        results.append('')
        results.append(tmp[1])
        results.append(tmp[2])
    position = 999
    for i in range(1, 10):
        if (results[2].find(str(i)) == -1):
            pass
        else:
            position = min(position, results[2].find(str(i)))
    results[2] = results[2][:position]
    return results

def get_address(postal_code):
    RECEST_URL = 'http://zipcloud.ibsnet.co.jp/api/search?zipcode={0}'.format(postal_code)
    address = []
    response = requests.get(RECEST_URL)
    json_result = response.text
    json_to_dic_result = json.loads(response.text)

    if json_to_dic_result['message'] == None:
        result_dic = json_to_dic_result['results'][0]
        for i in range(1, 4): ## 市町村・町名
            address.append(result_dic['address' + str(i)])
        return address
    else:
        address.append('not found')
        return address

if __name__ == '__main__':
    print('------------------------------------------')
    print('           入力元csvファイル：'+inputfile)
    print('          出力先ディレクトリ：'+outputdir)
    print('          　　　　　　発行年：'+str(year))
    print(' csv住所に都道府県が含まれる：'+str(pref))
    print('------------------------------------------')

    try:
        os.mkdir('./'+outputdir)
    except:
        pass
    print('✓ 出力先ディレクトリを作成しました。')

    try:
        f = open(inputfile, 'r', errors = '', newline = '')
    except:
        print('')
        print(pycolor.PURPLE+'【エラー】'+pycolor.END+inputfile+'が見つかりません。')
        print('')
        sys.exit()
    reader = csv.reader(f)
    data = [e for e in reader]
    f.close()
    print('✓ csvファイルを読み込みました。')

    sent = 0
    for i in range(len(data[1])):
        if (data[0][i]==str(year)+'送'):
            sent = i
    if (sent==0):
        print('')
        print(pycolor.PURPLE+'【エラー】'+pycolor.END+'：属性「'+str(year)+'送」がありません。')
        print('')
        sys.exit()
    print('✓ ヘッダー行が正しいことを確認しました。')

    if (False):
        for i in range(1, len(data)):
            postal_address = get_address(data[i][2])
            data_address = get_pref(data[i][3])
            if (postal_address[0] == 'not found'):
                print('')
                print(pycolor.PURPLE+'【エラー】'+pycolor.END+'郵便番号が実在しません。')
                print('      No.：'+str(data[i][0]))
                print('     氏名：'+str(data[i][1]))
                print(' 郵便番号：'+str(data[i][2]))
                print('     住所：'+str(data[i][3]))
                print('')
                sys.exit()
            elif (postal_address[1] == data_address[1])and(postal_address[2] == data_address[2]):
                pass
            else:
                print('')
                print(pycolor.RED+'【警告】'+pycolor.END+'郵便番号と住所とが一致していない可能性があります。')
                print('                      No.：'+str(data[i][0]))
                print('                     氏名：'+str(data[i][1]))
                print('                 郵便番号：'+str(data[i][2]))
                print('                     住所：'+str(data[i][3]))
                print('   郵便番号に基づいた住所：'+postal_address[0]+postal_address[1]+postal_address[2])
                print('')
        print('✓ 郵便番号が存在することを確認しました。')

    for i in range(1, len(data)):
        if (data[i][sent]==printval):
            image = Image.new('RGB',(1000,1480),'white')
            draw = ImageDraw.Draw(image)

            ## Name ##
            ##################################################
            ############### THIS IS NOT NEEDED ###############
            ################### FROM HERE ####################
            # name_num: the number of names
            # len_family: the length of a family name
            # len_first: the maximum length of first names
            name_num = data[i][1].count(names_sep) + 1
            len_family = data[i][1].find(name_sep)
            names = (data[i][1])[len_family+1:].split(names_sep)
            len_first = 1
            for name in names:
                len_first = max(len_first, len(name))
            '''
            +----------- x
            |
            |       〇  <---- start_y
            |           <---- chara_space
            |       〇
            |
            |
            |       〇  <---- name_start_y
            | 〇
            |       〇  <---- name_mid_y
            | 〇
            |       〇  <---- name_end_y
            |
            | 様    様  <---- title_y
            |
            y
            '''
            ################### UP TO HERE ###################
            ##################################################

            write_posit = [10*name_num**1.5+460,250]
            textsize = 100 - name_num * 5
            sep_size = textsize / 2
            for character in data[i][1]:
                if (character==names_sep):
                    write_posit[1] += textsize + sep_size
                    draw.text(write_posit, '様', font=ImageFont.truetype(mincho,textsize), fill=(0,0,0))
                    write_posit[1] = name_y
                    write_posit[0] -= textsize * 1.2
                elif (character==name_sep):
                    write_posit[1] += sep_size
                    name_y = write_posit[1]
                else:
                    write_posit[1] += textsize + sep_size
                    draw.text(write_posit, character, font=ImageFont.truetype(mincho,textsize), fill=(0,0,0))
            write_posit[1] += textsize + sep_size
            draw.text(write_posit, '様', font=ImageFont.truetype(mincho,textsize), fill=(0,0,0))

            ## Postal Num ##
            write_posit = [450,100]
            textsize = 64
            for character in data[i][2]:
                if (character=='-'):
                    write_posit[0] += textsize * .7
                else:
                    write_posit[0] += textsize * .7
                    draw.text(write_posit, character, font=ImageFont.truetype(times,textsize), fill=(0,0,0))

            ## Address ##
            write_posit = [800,300]
            textsize = 50
            for character in kansuji(data[i][3]):
                draw.text(write_posit, character, font=ImageFont.truetype(mincho,textsize), fill=(0,0,0))
                write_posit[1] += textsize * 1.1

            image.save('./'+outputdir+'/'+data[i][0]+'.png')
    print('✓ 画像ファイルを出力しました。')
