#!/usr/bin/env python3

import asyncio
import logging
import re
import signal
import sys
import cchardet
from pprint import pprint

import aiohttp
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import urldefrag
from bs4 import BeautifulSoup
#ページから本文を抜き出すlibrary
from readability.readability import Document
from extractcontent3 import ExtractContent

#textrankによりkeywordを抽出するlibirary
#from textrank import TextRank4Keyword
from collections import OrderedDict
import numpy as np
import spacy
import ginza
import itertools
from stop_words import STOP_WORDS

import time


class Scraping:
    def __init__(self):
        self.meta={}
        self.link={}
        self.result=[]

    def get_meta(self, html):
        meta={}
        soup=BeautifulSoup(html,"lxml")
        title=soup.find('title')
        desc=[m for m in soup.find_all('meta',attrs={'name':'description'}) if m.attrs['content']!=""]
        keywords=soup.find('meta',attrs={'name':'keywords'})
        if desc:
            meta['title']=title.text
            meta['description']=desc[0].attrs['content']
            if keywords:
                meta['keywords']=keywords.attrs['content']
            return meta
        else:
            meta['title']=title.text
            return meta

    def get_company_desc_links(self,base,html):
        result=[]
        link={}
        soup = BeautifulSoup(html, "lxml")
        links = soup.find_all("a",href=True,rel=lambda x:"nofollow" not in str(x).lower())

        check_keys=re.compile(r"(会社概要|会社情報|会社案内|企業情報|企業概要|事業案内|事業内容|事業概要|事業紹介|業務案内)")

        for a in links:
           link_text=""
           link_alt=""
           href = a.attrs['href']
           link_text=a.get_text()
           img = a.select('img')

           if len(img) >0:
               try:
                   link_alt=a.img['alt']
               except: continue

           if check_keys.search(link_text) or check_keys.search(link_alt):
               parsed_url = urlparse(urljoin(base, href))
               base_url=urlparse(base)
               if parsed_url.netloc != base_url.netloc:continue
#               if parsed_url.query != "":
#                   url='{}://{}{}?{}'.format(base_url.scheme,parsed_url.netloc,parsed_url.path,parsed_url.query)
#               else:
               url='{}://{}{}'.format(base_url.scheme,parsed_url.netloc,parsed_url.path)
               if url in result:continue
               if url+"index.html" in result:continue
               if url in [r+"index.html" for r in result]:continue
               if link_text.strip():
                   link.setdefault('link_url',{})
                   link['link_url'].setdefault(link_text.strip(),url)
                   #if url not in link['link_url'].values():
                       #link['link_url'][link_text]=url
               elif link_alt.strip():
                   link.setdefault('link_url',{})
                   link['link_url'].setdefault(link_alt.strip(),url)
                   #if url not in link['link_url'].values():
                       #link['link_url'][link_alt]=url

        if link:
            return link
        else:
            return

    def get_lang(self,html):
        soup=BeautifulSoup(html, "lxml")
        try:
            lang=soup.html.attrs['lang']
        except:
            lang='ja'
        return lang

    def get_links(self,base,html):
        result=[]
        soup=BeautifulSoup(html, "lxml")
        links = soup.find_all("a",href=True,rel=lambda x:"nofollow" not in str(x).lower())

        stop_keywords=re.compile(r"(お問い合わせ|採用情報|交通案内|プライバシー|求人|ご相談|サイトのご利用にあたって|"\
                        "アクセス|ブログ|ニュース|IR|マップ|個人情報|規約|実績|情報セキュリティ|コンプライアンス|反社会的勢力)")
        stop_directory=re.compile(r"(catalogue|policy|campaign|blog/|img/|information/|news/|topics/|ir/|history/|brand/|list/|works/|"\
                        "csr|recruit|career|contact|catalog|jisseki|privacy|interview/|press/|pdf/|support|intern|doc/|creative/|"\
                        "recommend|archive|award|chronicle|channel|heartland|jobs|diversity|faq|en/|attach_file|"\
                        "cgi-bin/|.wvx|.jpg|.pdf|.gif|diary|wp-content/|log/|studies/|english/|jisseki/|tel:|blogs/)")

        for a in links:
           link_text=""
           link_alt=""
           href = a.attrs['href']
           link_text=a.get_text()
           img = a.select('img')

           if len(img) >0:
               try:
                   link_text=a.img['alt']
               except: continue

           if not stop_keywords.search(link_text) and not stop_directory.search(href.lower())\
            and href!="/" and not re.search("<a href=",href):
               parsed_url = urlparse(urljoin(base, href))
               base_url=urlparse(base)
               if parsed_url.netloc != base_url.netloc:continue
#               if parsed_url.query != "":
#                   url='{}://{}{}?{}'.format(base_url.scheme,parsed_url.netloc,parsed_url.path,parsed_url.query)
#               else:
               url='{}://{}{}'.format(base_url.scheme,parsed_url.netloc,parsed_url.path)
               if url in result:continue
               if url+"index.html" in result:continue
               if url in [r+"index.html" for r in result]:continue
               if url+"index.php" in result:continue
               if url in [r+"index.php" for r in result]:continue
               result.append(url)
        return result

    def main_contents(self, html):
        result=set()
        flg=False
        tmp=""
        extractor=ExtractContent()
        options={
            "threshold":50,
            "min_length":30,
            "decay_factor":1.0,
            "continuous_factor":1.0,
            "punctuation_weight":10,
            "waste_expressions": r"(?i)All Rights Reserved"
        }
        delete_char=re.compile(r'(\u3000|&quot;|&lt;|&gt;|&amp;|&nbsp;|&rarr;|&reg;|&deg;|&ensp;|&rdquo;|&ldquo;|=|＝)')
        chg2punct=re.compile(r'(\||｜|・)')

        extractor.set_option(options)
        extractor.analyse(html)
        content,title=extractor.as_text()
        for s in filter(lambda x: x.strip(), map(lambda x: x.strip(), content.split('\n'))):
            s=delete_char.sub("",s)
            s=chg2punct.sub("、",s)
            if s[-1:]=="、" or s[-1:]=="､":
                tmp+=s
                flg=True
            elif flg==True:
                if s[-1:]!="。":
                    if len(tmp+s)>=20:
                        result.add(tmp+s+"。")
                else:
                    if len(tmp+s)>=20:
                        result.add(tmp+s)
                tmp=""
                flg=False
            else:
                if s[-1:]!="。":
                    if len(s)>=20:
                        result.add(s+"。")
                else:
                    if len(s)>=20:
                        result.add(s)
        #print("\n".join(list(result)))
        return "\n".join(list(result))

class Crawler:

    def __init__(self, rooturl, depth=2, maxtasks=100):
        self.rooturl = rooturl
        self.depth = depth
        self.cur_depth = 0
        self.naccess = 0
        self.counter = 0
        self.next_trigger = 0
        self.todo = set()
        self.busy = set()
        self.done = {}
        self.tasks = set()
        self.contents = set()
        self.meta = {}
        self.sem = asyncio.Semaphore(maxtasks)

        # connector stores cookies between requests and uses connection pool
        self.session = aiohttp.ClientSession()

    async def run(self):
        t = asyncio.ensure_future(self.addurls([(self.rooturl, '')]))
        await asyncio.sleep(1)
        while self.busy:
            await asyncio.sleep(1)
        await t
        await self.session.close()
        return [self.meta,self.contents]

    async def addurls(self, urls):
        self.naccess+=1
        for url, parenturl in urls:
            url = urljoin(parenturl, url)
            url, frag = urldefrag(url)
            if (url.startswith(self.rooturl) and
                    url not in self.busy and
                    url not in self.done and
                    url not in self.todo and
                    self.counter<50 and
                    len(urls)<50 and
                    self.cur_depth+1<=self.depth):
                self.counter+=1
                #print(self.naccess,self.counter,url,parenturl,len(urls))
                self.todo.add(url)
                await self.sem.acquire()
                task = asyncio.ensure_future(self.process(url))
                task.add_done_callback(lambda t: self.sem.release())
                task.add_done_callback(self.tasks.remove)
                self.tasks.add(task)
        #Crawlする階層の深さ(デフォルトで3)を指定しているので、トリガー計算
        if self.naccess==2:
            self.cur_depth+=1
            #print(self.cur_depth,self.next_trigger,self.counter)
            self.next_trigger=self.counter
        elif self.next_trigger==self.naccess and self.naccess>2:
            self.cur_depth+=1
            #print(self.cur_depth,self.next_trigger,self.counter)
            self.next_trigger=self.counter


    async def process(self, url):
        self.todo.remove(url)
        self.busy.add(url)
        print(url+" is progress...")
        try:
            resp = await self.session.get(url)
        except Exception as exc:
            #print('...', url, 'has error', repr(str(exc)))
            self.done[url] = False
        else:
            if (resp.status == 200 and
                    ('text/html' in resp.headers.get('content-type'))):
                if cchardet.detect(await resp.read())['encoding'] in (None,'ISO-8859-1'):
                    data = (await resp.read()).decode('utf-8','replace')
                else:
                    data=(await resp.read()).decode(cchardet.detect(await resp.read())['encoding'].lower(),'replace')
                if url==self.rooturl:
                    s=Scraping()
                    self.meta=s.get_meta(data)
                    self.meta['title_url']=self.rooturl
                    if 'description' in self.meta.keys():
                        self.contents.add(self.meta['description']+"。")

                s=Scraping()
                html = s.get_links(url,data)
                urls = [l for l in html]
                if s.get_lang(data) =='ja':
#                urls = re.findall(r'(?i)href=["\']?([^\s"\'<>]+)', data)
                    asyncio.Task(self.addurls([(u, url) for u in urls]))
                    if s.get_company_desc_links(url,data):
                        self.meta.update(s.get_company_desc_links(url,data))
                    self.contents.add(s.main_contents(data))

            resp.close()
            self.done[url] = True

        self.busy.remove(url)

class TextRank4Keyword:
     """Extract keywords from text"""

     def __init__(self,nlp):
         self.d = 0.85 # damping coefficient, usually is .85
         self.min_diff = 1e-5 # convergence threshold
         self.steps = 10 # iteration steps
         self.node_weight = None # save keywords and its weight
         self.nlp=nlp

     def set_stopwords(self, stopwords):
         """Set stop words"""
         for word in STOP_WORDS.union(set(stopwords)):
             lexeme = self.nlp.vocab[word]
             lexeme.is_stop = True

     def sentence_segment(self, doc, candidate_pos):
         """Store those words only in cadidate_pos"""
         sentences = []
         sentences = list(filter(lambda x:len(x)>1,[tuple(token.text for token in sent if token.pos_ in candidate_pos and token.is_stop is False) for sent in self.nlp.pipe(doc,batch_size=20000,disable=['ner','JapaneseCorrector','textcat'])]))

         return sentences

     def get_vocab(self, sentences):
         """Get all tokens"""
         vocab_list=[w for sentence in sentences for w in sentence]
         vocab = OrderedDict([(value,i) for i,value in enumerate(sorted(set(vocab_list),key=vocab_list.index))])

         return vocab

     def get_token_pairs(self, window_size, sentences):
         """Build token_pairs from windows in sentences"""
         token_pairs_tmp=tuple(tuple(zip(sentence,sentence[i+1:])) for sentence in sentences for i in range(min(len(sentence),window_size)))
         token_pairs=[t_inside for t_out in token_pairs_tmp for t_inside in t_out if t_inside]
         return token_pairs

     def symmetrize(self, a):
         return a + a.T - np.diag(a.diagonal())

     def get_matrix(self, vocab, token_pairs):
         """Get normalized matrix"""
         # Build matrix
         vocab_size = len(vocab)
         g = np.zeros((vocab_size, vocab_size), dtype='float32')
         for word1, word2 in token_pairs:
             i, j = vocab[word1], vocab[word2]
             g[i][j] = 1

         # Get Symmeric matrix
         g = self.symmetrize(g)

         # Normalize matrix by column
         norm = np.sum(g, axis=0)
         g_norm = np.divide(g, norm, where=norm!=0) # this is ignore the 0 element in norm

         return g_norm

     def get_keywords(self, number=10):
         """Print top number keywords"""
         results=[]
         node_weight = OrderedDict(sorted(self.node_weight.items(), key=lambda t: t[1], reverse=True))
         for i, (key, value) in enumerate(node_weight.items()):
             results.append(key)
 #            print(key + ' - ' + str(value))
             if i > number:
                 return(results)

     def analyze(self, text,
                 candidate_pos=['NOUN', 'PROPN'],
                 window_size=4, stopwords=list()):
         """Main function to analyze text"""
         start=time.time()
         # Set stop words
         self.set_stopwords(stopwords)
         split1=time.time()
         # Pare text by spaCy
         #doc = nlp(text)

         # Filter sentences
         #sentences = self.sentence_segment(doc, candidate_pos) # list of list of words
         sentences = self.sentence_segment(text, candidate_pos) # list of list of words
         #self.sentence_segment2(text,candidate_pos)
         #print(sentences)
         split2=time.time()
         # Build vocabulary
         vocab = self.get_vocab(sentences)
         split3=time.time()
         # Get token_pairs from windows
         token_pairs = self.get_token_pairs(window_size, sentences)
         split4=time.time()
         # Get normalized matrix
         g = self.get_matrix(vocab, token_pairs)
         split5=time.time()
         # Initionlization for weight(pagerank value)
         pr = np.array([1] * len(vocab))
         split6=time.time()
         # Iteration
         previous_pr = 0
         for epoch in range(self.steps):
             pr = (1-self.d) + self.d * np.dot(g, pr)
             if abs(previous_pr - sum(pr))  < self.min_diff:
                 break
             else:
                 previous_pr = sum(pr)
         split7=time.time()
         # Get weight for each node
         node_weight = dict()
         for word, index in vocab.items():
             node_weight[word] = pr[index]

         self.node_weight = node_weight
         split8=time.time()
         print(split1-start,split2-split1,split3-split2,split4-split3,split5-split4,split6-split5,split7-split6,split8-split7)

def handle_exception(loop, context):
    print("Exception handler called....")
    pprint(context)
    loop.stop()

def app_main(rooturl):
    start=time.time()
    output={}
    results=[]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    c = Crawler(rooturl)
    future=asyncio.ensure_future(c.run())

    try:
        loop.add_signal_handler(signal.SIGINT, loop.stop)
    except RuntimeError:
        pass

    loop.set_exception_handler(handle_exception)

    try:
        results=loop.run_until_complete(future)
    except:
        loop.stop()
        loop.close()
        return None


    output=results[0]
    result=[lambda x:x.strip(),"。\n".join("\n".join(list(results[1])).split("。")).split("\n")]
    result=set([x for x in result[1] if x !="。" and x])
    #print(output,result)

    nlp = spacy.load('ja_ginza',disable=['ner','textcat','JapaneseCorrector'])
    #nlp.tokenizer=ginza.sudachi_tokenizer.SudachiTokenizer(nlp=nlp,mode="C")
    merge_nps = nlp.create_pipe("merge_noun_chunks")
    nlp.add_pipe(merge_nps)

    tr4k=TextRank4Keyword(nlp)
    tr4k.analyze(list(result), candidate_pos = ['NOUN', 'PROPN'], window_size=10)
    keywords=tr4k.get_keywords(10)
    output['keywords_extracted']=",".join(keywords)
    print(rooturl+" is done...")
    end=time.time()
    print("process finished over "+str(end-start))
    return output

if __name__ == '__main__':
    results=app_main(sys.argv[1])
    print(results)
