import concurrent.futures as cf
from crawler import app_main
import sys
import time

sys.setrecursionlimit(10000)

def concurrent_crawl(urls):
    start=time.time()
    results=[]
    with cf.ProcessPoolExecutor() as executor:
        futures = [executor.submit(app_main, url) for url in list(set(urls))]

    for r in cf.as_completed(futures):
        try:
            results.append(r.result())
        except:
            continue
    end=time.time()
    print("all process took "+str(end-start)+"s.....")
    return results

if __name__ == "__main__":
    urls=(
        "https://www.digitalidentity.co.jp",
        "http://www.tosen.com",
        "http://www.tkykanzai.co.jp",
        "http://www.kouei-unsou.com/",
        "https://www.willgate.co.jp",
        "https://tokyozidousya.co.jp",
        "http://www.tokyojiko.co.jp",
        "http://www.cine.co.jp",
        "http://apie.jp",
        "https://www.simildesign.com",
        "http://www.ichiharagumi.com",
        "http://www.taisyuu.co.jp"
        )
    results=concurrent_crawl(urls)
    print(results)
