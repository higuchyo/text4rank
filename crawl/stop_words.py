# coding: utf8
from __future__ import unicode_literals

# This list was created by taking the top 2000 words from a Wikipedia dump and
# filtering out everything that wasn't hiragana. ー (one) was also added.
# Considered keeping some non-hiragana words but too many place names were
# present.
STOP_WORDS = set(
    """
あ あっ あまり あり ある あるいは あれ
い いい いう いく いずれ いっ いつ いる いわ
うち
え
お おい おけ および おら おり
か かけ かつ かつて かなり から が
き きっかけ
くる くん
こ こう ここ こと この これ ご ごと
さ さらに さん
し しか しかし しまう しまっ しよう
す すぐ すべて する ず
せ せい せる
そう そこ そして その それ それぞれ
た たい ただし たち ため たら たり だ だけ だっ
ち ちゃん
つ つい つけ つつ
て で でき できる です
と とき ところ とっ とも どう
な ない なお なかっ ながら なく なけれ なし なっ など なら なり なる
に にて
ぬ
ね
の のち のみ
は はじめ ば
ひと
ぶり
へ べき
ほか ほとんど ほど ほぼ
ま ます また まで まま
み
も もう もっ もと もの
や やっ
よ よう よく よっ より よる よれ
ら らしい られ られる
る
れ れる
を
ん
一
当 本 年 等 日本 人 上 数 方 為 中 事 道 歴史 時代 挑戦 貴社 当社 弊社 株式会社 有限会社 お客様 お客さま
上
中
下
字
年
月
日
時
分
秒
週
火
水
木
金
土
国
都
道
府
県
市
区
町
村
番
丁目
号

各
第
方
何
的
度
文
者
性
体
人
他
今
部
課
係
外
類
達
気
室
口
誰
用
界
会
首
男
女
別
話
私
屋
店
家
場
等
見
際
観
段
略
例
系
論
形
間
地
員
線
点
書
品
力
法
感
作
元
手
数
彼
彼女
子
内
楽
喜
怒
哀
輪
頃
化
境
俺
奴
高
校
婦
伸
紀
誌
レ
行
列
事
士
台
集
様
所
歴
器
名
情
連
毎
式
簿
心
共

回
匹
個
席
束
歳
目
通
面
円
玉
枚

前
後
左
右
次
先

春
夏
秋
冬



一
二
三
四
五
六
七
八
九
十
百
千
万
億
兆


下記
上記
時間
今回
前回
場合
一つ
年生
自分
ヶ所
ヵ所
カ所
箇所
ヶ月
ヵ月
カ月
ヶ月間
ヵ月間
カ月間
箇月
名前
本当
確か
時点
全部
関係
近く
方法
我々
違い
多く
扱い
新た
その後
半ば
結局
様々
以前
以後
以降
未満
以上
以下
幾つ
毎日
自体
向こう
何人
手段
同じ
感じ
社員
社員全員
社員一人ひとり
私たち
想い
思い
社内
常
英文
創業
昭和
明治
大正
平成
令和
ホームページ
長年
経験
ニーズ
ご要望
ご使用
要望
公式
実際
皆さま
皆様
みなさま
お知らせ
今後
日々
lt
gt
amp
quot
nbsp
u3000
御
企業
会社
℃
mm
reg
etc
TEL
Tel
tel
FAX
FAX.
a
b
c
d
e
f
g
h
i
j
k
l
m
n
o
p
q
r
s
t
u
v
w
x
y
z
A
B
C
D
E
F
G
H
I
J
K
L
M
N
O
P
Q
R
S
T
U
V
W
X
Y
Z
御客様
御客さま
お取引先
ご紹介
顧客
私
私たち
私達
FEATURE
READMORE
年創業以来
創業以来
年創業
本サイト
当サイト
当ウェブサイト
本ウェブサイト
本サービス
当サービス
全
やすく
やすさ
約
社
各種
お願い
ご注文
目的
個人情報
笑

㎡
m2
kg
mg
cm
Ltd
EXCEL
e-mail
info
copyright
Copyright
com
net
Net
copy
times
city
No.

""".split()
)
