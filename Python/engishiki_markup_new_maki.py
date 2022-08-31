from bs4 import BeautifulSoup as BS
import csv

def generate_TEIheader(output_filename):
    """ ヘッダーの記述
    既存のTEIヘッダーの記述を新規ファイルに出力する（モード 'w'）
    地理情報なども入れると良い"""

    output_file = open(output_filename, 'w', encoding='utf-8')

    header_file = open('../TEI files/engishiki_header.xml', 'r', encoding='utf-8')
    header = header_file.read()
    header_file.close()
    
    output_file.write(header)

    output_file.close()

    print('TEIヘッダー情報書き込み完了')

######################################################################
################### 読み込み＆書き出しファイルの指定 ########################
######################################################################


#作業者が適切なディレクトリを指定する

file_volume = input('読み込む巻を入力してください\n')

input_filename = f'../vol_metadata/metadata_v{file_volume}.tsv'
# 巻11.csv
output_filename = f'../途中生成物/engishiki_v{file_volume}.xml'
# engishiki_v11.xml


# headerを書き込む
generate_TEIheader(output_filename)
# 関数は別ファイルとして保存してある
result = open(output_filename, 'r', encoding='utf-8')
soup = BS(result, 'xml')

# <teiHeader>の後、<text><body></text>タグを挿入
root = soup.TEI
t_text = soup.new_tag("text")
t_body = soup.new_tag('body')
root.append(t_text)
t_text.append(t_body)

# https://note.nkmk.me/python-csv-reader-writer/
# CSVリーダーで見出し行のカラム名をキーとする順序付き辞書を取得し、巻のメタデータをリストとして保持
f = open(input_filename, 'r', encoding='utf-8')
reader = csv.DictReader(f, delimiter='\t')
metadata = [row for row in reader]
f.close()
shiki_name = metadata[0]['式名']
shiki_no = metadata[0]['巻']

### 全体構造について確認
# 最上位はdivタグのtype="巻"
# その子要素にdivが4つ、それぞれtype="首題", "式名", "尾題", "本奥書"
# type="式名"のdivタグの子要素には、type="式題"のdivがあり、その兄弟要素として本文が条数分だけある

# 最上位のdivタグから生成
t_div_maki = soup.new_tag('div', ana=f"{shiki_name}", n=f"{shiki_no}", type="巻", subtype="式")
t_body.append(t_div_maki)

# 4つのdivタグをその子要素に。それぞれ変数名で区別できるように
t_div_shudai = soup.new_tag('div', type="首題")
t_div_shiki = soup.new_tag('div', ana=f"{shiki_name}", n=f"{shiki_no}", type="式", subtype="条")
t_div_bidai = soup.new_tag('div', type="尾題")
t_div_okugaki = soup.new_tag('div', type="本奥書")

# 首題のdivタグを最上位の子要素にし、自身の子要素にpタグと文字列を挿入。尾題と本奥書についても同様
t_div_maki.append(t_div_shudai)
t_div_shudai.append(soup.new_tag('p'))
t_div_shudai.p.string = '首題'

# 本文を格納する式タグを生成
t_div_maki.append(t_div_shiki)

# 尾題
t_div_maki.append(t_div_bidai)
t_div_bidai.append(soup.new_tag('p'))
t_div_bidai.p.string = '尾題'

# 本奥書
t_div_maki.append(t_div_okugaki)
t_div_okugaki.append(soup.new_tag('p'))
t_div_okugaki.p.string = '本奥書'

### メインの式タグの中身を格納していく
# 条数分だけdivタグを生成する必要があるので、上記で定義した巻のmetadataのリストをすべてforループ
for data in metadata:
    t_div_shiki.append(soup.new_tag('div', ana=f"{shiki_name}", n=f"{shiki_no}.{data['条']}", type="条", subtype="項"))
    # ポイントは、ここで末尾のdivを指定しないといけないこと。以下、同様
    t_div_shiki.select('div')[-1].append(soup.new_tag('head', ana=f'{data["新条文名"]}'))
    
    # 次に、項数文だけpタグを追加
    kous = int(data["項"])
    for kou in range(kous):
        item_id = f'item{shiki_no.zfill(2)}{data["式順"]}{data["条"].zfill(3)}{str(kou+1).zfill(2)}'
        # BSでxml:id属性値を与える方法について。https://zenn.dev/nakamura196/articles/ed3c614b08b0c4
        # https://stackoverflow.com/questions/38379451/using-beautiful-soup-to-create-new-tag-with-attribute-named-name
        t_div_shiki.select('div')[-1].append(soup.new_tag('p', **{"ana":"項", "xml:id":f"{item_id}", "corresp":f"engishiki_ja.xml#{item_id} engishiki_en.xml#{item_id}"}))
        t_div_shiki.select('div')[-1].p.string = "本文"

# すべての結果の書き込み
result = open(output_filename, 'w', encoding='utf-8')
result.write(str(soup))
result.close()



