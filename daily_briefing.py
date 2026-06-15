import urllib.request, xml.etree.ElementTree as ET, json, datetime

BARK_KEY = "2iySCcxHSxN7ei4oKb8KcZ"

SOURCES = [
    ("xh", "http://www.xinhuanet.com/politics/news_politics.xml"),
    ("36kr", "https://36kr.com/feed"),
    ("sdt", "https://www.solidot.org/index.rss")
]

CATS = {
    "[财经]": ["财经","股市","央行","美元","经济","A股","金融","降准","GDP"],
    "[科技]": ["AI","芯片","苹果","微软","机器人","数据","自动驾驶","华为"],
    "[政治]": ["习近平","总理","中美","外交","制裁","选举","议会","会谈"],
    "[娱乐]": ["电影","票房","演唱会","游戏","明星","综艺","热映","音乐"]
}

def fetch(url, n=30):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        root = ET.fromstring(urllib.request.urlopen(req, timeout=10).read())
        items = root.findall(".//item")
        titles = []
        for item in items:
            t = item.findtext("title", "")
            if t:
                titles.append(t[:50])
        return titles[:n]
    except:
        return []

def build():
    alls = []
    for n, u in SOURCES:
        alls += fetch(u)
    
    parts = []
    for lb, kws in CATS.items():
        ms = []
        for t in alls:
            for kw in kws:
                if kw in t and t not in ms:
                    ms.append(t)
                    break
            if len(ms) == 3:
                break
        line = lb + "\n" + (" | ".join(ms) if ms else "暂无相关新闻") + "\n"
        parts.append(line)
    return "\n".join(parts)

def push(title, body):
    data = json.dumps({
        "device_key": BARK_KEY,
        "title": title,
        "body": body,
        "group": "晨间简报",
        "icon": "https://img.icons8.com/fluency/96/news.png"
    }).encode()
    req = urllib.request.Request(
        "https://api.day.app/push",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req)
    print(resp.read().decode())

if __name__ == "__main__":
    now = datetime.datetime.now()
    is_weekend = now.weekday() >= 5
    title = "周末简报 📬" if is_weekend else "晨间简报 🌅"
    body = build()
    if body:
        push(title, body)
        print("OK:", title)
    else:
        print("No news fetched")