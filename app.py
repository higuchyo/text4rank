# -*- coding:utf-8 -*-
from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import urllib
import json, sys
import requests
from concurrent_crawl import concurrent_crawl

app = Flask(__name__)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    max_search=[20,50,100]
    return render_template('index.html',input=max_search)

@app.route('/query/',methods=['GET'])
def query():
    if request.method == 'GET':
        error = 0
        url_list=[]
        a = request.args.get('a', type=str)
        q = request.args.get('q', type=str)
        q_add = 'allintext:' + a + ' ' + q + ' 企業'
        max_num = request.args.get('max_num',default=20,type=int)
        # read engineID
        f = open('google_id/id_key.json')
        s = json.load(f)

        for i in range(len(s['engine'])) :
            sn = 'engine_' + str(i+1)
            key = s['engine'][i][sn]['key']
            cx = s['engine'][i][sn]['cx']

            cnt1=1
            cnt2=10

            while cnt1 < max_num:
                # search request
                url = "https://www.googleapis.com/customsearch/v1"
                query_string = {"hl":"ja","key":key,"cx":cx,"q":q_add,"start":cnt1,"num":cnt2}
                response = requests.request("GET", url, params=query_string)
                json_data = json.loads(response.text)
                hit = json_data["queries"]["request"][0]["totalResults"]
                print(hit)

                try:
                    if json_data['items']:
                        #検索結果のURL, TITLE, SNIPPET　をappendしてく
                        for p in range(len(json_data['items'])):
                            #print(json_data['items'][p]['link'])
                            #print(urllib.parse.urlparse(json_data['items'][p]['link']))
                            parsed_url=urllib.parse.urlparse(json_data['items'][p]['link'])
                            home_url='{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
                            url_list.append(home_url)
                except:
                    break

                cnt1+=1*cnt2

        #検索結果の親urlからcrawling
        results=concurrent_crawl(url_list)
        print(url_list)
        #結果はdict型：'title','description','keywords','link_url'（リンクのtextをkeyとしたdict型）,'keywords_extracted'

        if results:
            #print(results)
            output=[]
            num_result=0

            for result in results:
                print(result)
                if 'link_url' in list(result.keys()):
                    num_result+=1
                    output.append(result)
                else:
                    continue

            search_info = str(num_result)+' results'

            max_search=[20,50,100]

            return render_template('index.html',a=a,q=q,results=output,error=error,search_info=search_info, input=max_search)
        else :
            max_search=[20,50,100]
            search_info =  'No results from search words ' + q
            return render_template('index.html',a=a,q=q,error=error,search_info=search_info, input=max_search)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug = True,port=5000)
