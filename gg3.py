# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 07:58:45 2017
@author: milal
"""

from flask import Flask
from flask import render_template
from flask import request
#import redis
import feedparser
import random
#import lxml
import requests
from bs4 import BeautifulSoup
import re
import operator
import datetime

app = Flask(__name__)

RSS_FEEDS = {'bbc':'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn':'http://rss.cnn.com/rss/edition.rss',
             'fox':'http://feeds.foxnews.com/foxnews/latest',
             'iol':'http://iol.co.za/cmlink/1.640',
             'rt':'http://rss.russiatoday.ru',
             'rt2':'https://www.rt.com/rss/news/',
             'rt3':'https://www.rt.com/rss/',
             'rt4':'rss.russiatoday.ru'
             }


def send_sms(auth, who, msg, ):
    api_url = 'https://smsapi.free-mobile.fr/sendmsg?user=10628240&pass=aHSBG5ohgtNaQ3&msg='
    payload = {'user' :'10628240', 'pass' : 'aHSBG5ohgtNaQ3', 'msg' : msg}
    data = requests.get(api_url, params = payload)
    return "message send"
    # https://smsapi.free-mobile.fr/sendmsg?user=10628240&pass=aHSBG5ohgtNaQ3&msg=
    # send
    # pass


@app.route("/gr", methods = ['GET', 'POST'])
def get_race(reu=1,crs=3,dt='',allurls='n'):
    #returns all hyperlinks from turfoo.fr for a given date (default = today)
    tmpdt  = request.args.get("dt")
    tmpreu = request.args.get("reu")
    tmpcrs = request.args.get("crs")
    tmpallurls = request.args.get("allurls")
    if tmpallurls:
        #here add validation on date -> YYMMDD throw error if format is invalid
        allurls = tmpallurls.upper()
    if tmpdt:
        #here add validation on date -> YYMMDD throw error if format is invalid
        dt = tmpdt
    # from main page get all races details for url mapping
    print('dt from get-race',dt)
    api_root = 'http://www.turfoo.fr/programmes-courses/'
    api_root2 = 'http://www.turfoo.fr'
    api_url = api_root+dt
    #print('api_url',api_url)
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
    data = requests.get(api_url, headers = headers)
    soup = BeautifulSoup(data.content, 'html.parser')
    z = soup.find_all('div', class_="programme_reunion")
    # programme reunion will contain tables of races for all differents reunions
    race_urls = []  #hold all races href  of the day
    for i in z:     #loop thru all reunions
        z1 = i.find_all('tr', class_="row")
        # loop on race of the reunion
        for j in z1:
            #for now we need to find qt - how ?
            #get all class = violet +href contain the url of races
            z2 = j.find_all('a', class_="violet")
            for k in z2[:1]:
                rc = k['href']    #this gives us the url of every race of the day
                #print(k['href'])    #this gives us the url of every race of the day
                race_urls.append(rc)
            #print(len(z2),z2)
    # find the url requested by using r &c variables
    crs = 'course'+str(crs)
    reu = 'reunion'+str(reu)
    m = [s for s in race_urls if (crs in s) & (reu in s)]
    #print(m)
    #print(api_root2+m[0])
    # build reunion+r and course+c
    # find it in the race_urls array
    if allurls == 'Y':
        return race_urls
    else:
        return str(api_root2+m[0])
    # now we get the page will all the races for the current day
    # build a list and detect the main one
    # in a dictionnary x = {'date' : 170612,
    #                       'reunion': '1',
    #                       'url' : 'urlreunion',
    #                       'urls' : [(1,urlcourse),(2,...)]
    #                       }
    #pass


# def savecotes_txt():
# pass
def store_res(data):
    # store data mainly received from extract_res into a .txt file
    # sore in mongodb / redis / mysql / couchbase
    # generate xls
    pass


def extract_res(reu=1,crs=3,dat='',allurls='Y'):
    today = datetime.datetime.today()
    d1 = today.strftime('%Y%m%d')
    #print(d1[2:])
    #d1.year,d1.month,d1.day)
    if dat == '':
        dat = d1[2:]
    print(dat)
    x = get_race(reu=1,crs=2,dt=dat,allurls='Y')
    api_root = 'http://www.turfoo.fr'
    # change root url programme-courses with resultats-courses
    rurl = []
    for e,i in enumerate(x):
        a = str(i).replace('/programmes-courses','/resultats-courses')
        rurl.append(a)
    #print(x)
    #extract 1. race arrival numbers / odds / and else ?
    #extract 2. rapports
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
    payload = {}
    req = api_root+rurl[0]
    #print('req=',req)
    try:
        data = requests.get(req, headers = headers, params = payload)
    except:
        return "cannot connect"
    # use bs4
    #print(data.content)
    soup = BeautifulSoup(data.content, 'html.parser')
    # here start to extract
    z = soup.find_all('div', class_="pari")
    rap = []
    for e,j in enumerate(z[:350]):
        #print(j.get_text().encode('utf-8'))
        #i = i.encode('utf-8')
        # first regex to replace multiple \r\n by a space
        try:
            result = re.sub(r"\\n|\\r|\\xe2|\\x82|\\xac", r";", str(j.get_text().encode('utf-8')))
            #result = re.sub(r"(?sim)\r+|\n+", r"@", str(j.get_text().encode('utf-8')))
            result = re.sub(r"\\*xc3|\\*xa9|\\*t|\\*xc2|\\*xa0", r"", result)
            result = re.sub(r"\s+", r"", result)
            result = re.sub(r"(?sim);+", r";", result)
            print(result)
            t = result.split(';')
            rap.extend(t)
            #print('t=',t)
        except:
            print("error in regex area")
            return "error in regex area"
            break
    print('rap=',rap)
    #return "ya"
    #print(j.encode('utf-8').get_text())
    #return t
    # store t now
    #print('z0',z[0].get_text())
    z1 = soup.find_all('tr', class_="row")
    # return as json or array
    horses = []
    for e,i in enumerate(z1):
        #i = i.encode('utf-8')
        # first regex to replace multiple \r\n by a space
        result = re.sub(r"(?sim)\r+|\n+", r"@", str(i.get_text().encode('utf-8')))
        # replace multiple space by a ;
        result = re.sub(r"(?sim)@+", r";", result)
        t = result.split(';')
        horses.extend(t)
        #print(t)
        # print(i.get_text())
    # print(z1)
    print('horses=',horses)
    return "ya"



@app.route("/tst", methods = ['GET', 'POST'])
def tst():
    extract_res()
    # routine to test other routine
    # test /gr with allurls to see if it comes back as an array
    #x = get_race(reu=1,crs=3,dt='',allurls='Y')
    #ok its good as it return an array of all race all reunions !
    #print('x=',x)
    #for i in x:
        #print(i)
    return "yo"

@app.route("/gc", methods = ['GET', 'POST'])
def get_cotes(dt='170612', reu=1, crs=1, flg=9, cte=1, rdm='n', qt='n', extract = 'n'):
    # extract parameter allow the routine to return data :nbrs-horse name-
    # cotes-jockey-distance-corde-poids-entraineur-musique-age-others
    # extract parameter is not available yet for being called from the
    # web - only in the subroutine
    reu = request.args.get("r")
    crs = request.args.get("c")
    tmpflg = request.args.get("flg")   # allow to choose 9 or 11 LT
    tmpcte = request.args.get("cte")   # allow to choose which odds to use
    tmprdm = request.args.get("rdm")   # allow to choose which odds to use
    tmpqt = request.args.get("qt")   # allow to choose which odds to use
    if tmpflg:
        flg = tmpflg
    if tmpcte:
        cte = int(tmpcte)
    if tmprdm:
        rdm=tmprdm
    if tmpqt:
        qt=tmpqt
    # t1=pmuvente 2=pmuinternet 3=zeturf
    # dt format = YYMMDD
    # here we need to get the cotes of the requested date/reunion/course
    api_root = 'http://www.turfoo.fr/programmes-courses/170618/'
    api_url = api_root+'170612/reunion1-compiegne/course1-prix-major-fridolin/'
    api_url = str(get_race(reu,crs))
    print(api_url)
    # q={}&units=metric&appid=8a839a08492fc8191c3b9e02ddcf272b'
    # query = urllib.quote(query)
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
    payload = {}
    # url = api_url.format(query)
    # print(url)
    # data = urllib2.open(url).read() #urllib2 does not seem to exist for python3 try request instead
    try:
        data = requests.get(api_url, headers = headers, params = payload)
    except:
        return "Cannot connect to "+api_url
    # use bs4
    soup = BeautifulSoup(data.content, 'html.parser')
    # print(data.text)
    z = soup.find_all('div', class_="programme_partants")
    z1 = z[0].find_all('tr', class_="row")
    # z1 = z.find_all('tr', class_="row")
    # class="programme_partants"
    # print(len(z1))
    d1 = {}     #cotes1
    d2 = {}
    d3 = {}
    for e,i in enumerate(z1):
        # first regex to replace multiple \r\n by a space
        result = re.sub(r"(?sim)\r+|\n+", r"@", i.get_text())
        # replace multiple space by a ;
        result = re.sub(r"(?sim)@+", r";", result)
        t = result.split(';')
        print(len(t),e+1,t[-5:-2])
        try:
            d1[e+1]=float(t[-5:-4][0])
        except:
            pass
        try:
            d2[e+1]=float(t[-4:-3][0])
        except:
            pass
        try:
            # d3 is normally containing zeturf cotes and may not be available
            d3[e+1]=float(t[-3:-2][0])
        except:
            pass
        # print(i.get_text())
    # print(z1)
    lt = sorted(d1.items(),key=operator.itemgetter(1))
    lt = [0]+[j for j,k in lt]
    lt1 = sorted(d2.items(),key=operator.itemgetter(1))
    lt1 = [0]+[j for j,k in lt1]
    try:        # lt zeturf
        lt2 = sorted(d3.items(),key=operator.itemgetter(1))
        lt2 = [0]+[j for j,k in lt2]
    except:
        pass
    print('cte=',cte)
    print('Lt=',lt)
    print('Lt=1',lt1)
    try:
        print('Lt=2',lt2)
    except:
        print('looks like lt2/d3 are not available !')
    chlt = lt     #default
    if cte == 1:
        chlt = lt
    elif cte == 2:
        chlt = lt1
    elif cte == 3:
        chlt = lt2
    v = m4(chlt,rt='raw',flg=flg,rdm=rdm)
    if qt == 'Y':
        # call quinte generation subroutine
        pass
    # print(v)
    # return str(sorted(v))
    return render_template("m4.html", combs = sorted(v), lt=chlt,reu=reu, crs=crs, flg=flg, cte=cte)


def storedb():
    # store somethin into redis DB and persist the data
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.set('foo', 'bar')


def get_currency():
    #app_id = e66979a8fb2c4eb8a1f1f5bf6b1fb1be
    # https://openexchangerates.org/api/latest.json    ->retourne les derniers cours format json
    # https://openexchangerates.org/api/currencies.json   ->retourne la liste de currencies et leur code
    # https://openexchangerates.org/api/convert/:value/:from/:to   ->conversion
    # example:https://openexchangerates.org/api/convert/19999.95/GBP/EUR?app_id=YOUR_APP_APP_ID
    pass


def get_weather(query,unit='metric'):
    api_url = 'http://api.openweathermap.org/data/2.5/weather'
    #q={}&units=metric&appid=8a839a08492fc8191c3b9e02ddcf272b'
    #query = urllib.quote(query)
    #unit = 'metric'
    payload = {'q': query, 'appid': '8a839a08492fc8191c3b9e02ddcf272b', 'units':unit}
    #url = api_url.format(query)
    #print(url)
    # data = urllib2.open(url).read() #urllib2 does not seem to exist for python3 try request instead
    data = requests.get(api_url, params = payload)
    print(data.json())
    try:
        #parsed = json.loads(data.json())
        parsed = data.json()
        weather = None
        if parsed.get("weather"):
            weather = {"description":parsed["weather"][0]["description"],
            "temperature":parsed["main"]["temp"],
            "city":parsed["name"]
            }
    except:
        print('something happened...')
        weather = None
    print(weather)
    return weather

DEFAULTS = {'publication' : 'bbc',
            'city' : 'LONDON,UK'
    }


@app.route("/", methods = ['GET', 'POST'])
def home_page():
    return render_template("/businessworldtemplate/index.html")



@app.route("/about.html", methods = ['GET', 'POST'])
def about_page():
    return render_template("/businessworldtemplate/about.html")



@app.route("/blog.html", methods = ['GET', 'POST'])
def blog_page():
    return render_template("/businessworldtemplate/blog.html")



@app.route("/services.html", methods = ['GET', 'POST'])
def services_page():
    return render_template("/businessworldtemplate/services.html")



@app.route("/products.html", methods = ['GET', 'POST'])
def products_page():
    return render_template("/businessworldtemplate/products.html")



@app.route("/contact.html", methods = ['GET', 'POST'])
def contact_page():
    return render_template("/businessworldtemplate/contact.html")


@app.route("/news", methods = ['GET', 'POST'])
def get_news(city='LONDON,UK'):
    query = request.args.get("publication")
    unt = request.args.get("unit")
    ct = request.args.get("city")
    if not ct:
        ct ='Luxembourg, LU'
    if not unt:
        unt='metric'
    else:
        unt='imperial'
    if not query or query.lower() not in RSS_FEEDS:
        publication = "bbc"
    else:
        publication = query.lower()
    fd=feedparser.parse(RSS_FEEDS[publication])
    if publication == 'rt2':
        imgtbl = []
        for e,i in enumerate(fd.entries):
            soup = BeautifulSoup(i.summary)
            image_url = soup.find('img')['src']
            if image_url:
                imgtbl.append(image_url)
            #if fd.entries[e].summary:
            #st = re.sub(r"<img.*\/>", r"", fd.entries[e].summary)
            #print('st=',st.group(0))
        #print(str(fd.entries[0]).encode('utf-8'))
        #imgtbl.append('<img none />')
        #print(fd.entries[0].summary)
        #print('image', fd.entries[0].summary[0:1])
    weather = get_weather(ct, unt)
    #first_article = feed['entries'][0]
    if publication == 'rt2':
        return render_template("homert.html", articles = fd['entries'], imgs = imgtbl, weather = weather)
    else:
        return render_template("home.html", articles = fd['entries'], weather = weather)

def compile_cbs(cb=[]):
    # compile a srie of unitary combs into champs reduits
    a = []
    cb = sorted(cb)
    for i in cb:
        if i[:3] in a:
            pass
        else:
            a.append(i[:3])
    s = ''
    mem = cb[0][:3]
    s = str(mem)+' / '
    tbstr = []
    for e,i in enumerate(cb):
        if i[:3] == mem:
            s += str(i[3])+' - '
        else:
            tbstr.append(s)
            s = ''
            s = str(i[:3])+' / '+str(i[3])+' - '
            mem = i[:3]
    tbstr.append(s)
    return tbstr

def cb1():
    cb1 = [
            [1,4,6,12],
            [1,4,6,13],
            [1,4,7,12],
            [1,4,7,13],
            [1,4,8,12],
            [1,4,8,13],
            [1,4,9,12],
            [1,4,9,13],
            [1,4,10,12],
            [1,4,10,13],
            [1,4,11,12],
            [1,4,11,13],
            [1,5,6,12],
            [1,5,6,13],
            [1,5,7,12],
            [1,5,7,13],
            [1,5,8,12],
            [1,5,8,13],
            [1,5,9,12],
            [1,5,9,13],
            [1,5,10,12],
            [1,5,10,13],
            [1,5,11,12],
            [1,5,11,13],
            [2,4,6,12],
            [2,4,6,13],
            [2,4,7,12],
            [2,4,7,13],
            [2,4,8,12],
            [2,4,8,13],
            [2,4,9,12],
            [2,4,9,13],
            [2,4,10,12],
            [2,4,10,13],
            [2,4,11,12],
            [2,4,11,13],
            [2,5,6,12],
            [2,5,6,13],
            [2,5,7,12],
            [2,5,8,13],
            [2,5,8,12],
            [2,5,8,13],
            [2,5,9,12],
            [2,5,9,13],
            [2,5,10,12],
            [2,5,10,13],
            [2,5,11,12],
            [2,5,11,13],
            [3,4,6,12],
            [3,4,6,13],
            [3,4,7,12],
            [3,4,7,13],
            [3,4,8,12],
            [3,4,8,13],
            [3,4,9,12],
            [3,4,9,13],
            [3,4,10,12],
            [3,4,10,13],
            [3,4,11,12],
            [3,4,11,13],
            [3,5,6,12],
            [3,5,6,13],
            [3,5,7,12],
            [3,5,8,13],
            [3,5,8,12],
            [3,5,8,13],
            [3,5,9,12],
            [3,5,9,13],
            [3,5,10,12],
            [3,5,10,13],
            [3,5,11,12],
            [3,5,11,13],
    ]
    return cb1


@app.route("/m4", methods = ['GET', 'POST'])
def m4(c=[0,1,2,3,4,5,6,7,8,9],flg = 9, rt = 'html', rdm='N', comp='y', combi = 0):
    # set flg = 11 to apply -1 in 6,7,8 and -1 in 9,10,11
    # provide 11 members LT
    # rt = html means that the routine will use the return render template
    # rt = raw will return combs as a list
    # rdm allow to shuffle the lt passed to m4 routine possible value = Y/N
    # rdm defaults to N
    # compile = y will return by default the combs compiled in a champ reduit
    # combi permet de choisir parmi les tableaux de combs a utiliser
    # pour generer les jeux 0 = default 1 = cb1()
    dm = list(range(9,19))
    flg = request.args.get("flg")
    query = request.args.get("lt")
    comp = request.args.get("comp")
    #print(type(c))s
    if query:
        c = query.split(',')
        c = [0]+c[:]
        c = [int(x) for x in c]
    if len(c) < 10:
        # complete lt with dummy numbers
        return ['not enough runners']
            #query += random.sample(dm,9)
        #print(type(c))
    if flg == '11':
        p1 = c[6:9]
        p2 = c[9:12]
        px1 = random.sample(p1,1)
        px2 = random.sample(p2,1)
        #remove them from p1 and p2
        p1.remove(px1[0])
        p2.remove(px2[0])
        c = c[:6]+p1+p2
        #print(c)
    # multis en 4 favos - c contient la liste type
    print('rdm=',rdm)
    if rdm.upper() == 'Y':
        #print('entering rdm')
        c = [0]+random.sample(c[1:], len(c)-1)
        #print(random.shuffle(c[1:]))
    print('c=',c,' rdm = ',rdm)
    cbs = [
    		[1, 4, 2, 5],
    		[1, 4, 2, 9],
    		[1, 4, 2, 6],
    		[1, 4, 2, 7],
    		[1, 8, 2, 6],
    		[1, 8, 2, 7],
    		[2, 5, 3, 6],
    		[2, 5, 3, 7],
    		[2, 9, 3, 6],
    		[2, 9, 3, 7],
    		[2, 5, 3, 4],
    		[2, 5, 3, 8],
    		[2, 9, 3, 4],
    		[2, 9, 3, 8],
    		[3, 6, 1, 4],
    		[3, 6, 1, 8],
    		[3, 7, 1, 4],
    		[3, 7, 1, 8],
    		[3, 6, 1, 5],
    		[3, 6, 1, 9],
    		[3, 7, 1, 5],
    		[3, 7, 1, 9],
    	]
    #print(cbs)
    if combi == 1:
        cbs = cb1()
    #print(cbs)
    l = [0,1,2]
    #print(r[:],c)
    combs = []
    for e1,i in enumerate(cbs):
        p = random.sample(l[:3],2)
        if (2 in p):
            c1 = []
            for j in i:
                #print(c[j], end='-')
                try:
                    c1.append(c[j])
                except:
                    c1.append(j)
            #print()
            combs.append(c1)
    print(combs)
    # routine to compile combs in champ reduit
    # compile_cbs(combs)
    print('comp=',comp)
    if comp == 'n':
        pass
    else:
        combs = ['0']+compile_cbs(combs)
    if rt == 'html':
        return render_template("m4.html", lt = c, combs = combs)
    else:
        return combs



@app.route("/e2", methods = ['GET', 'POST'])
def e2(rg1=1,rg2=50,loop=5,shuf='n'):
    #pass
    r1 = request.args.get("rg1")
    r2 = request.args.get("rg2")
    lp = request.args.get("loop")
    sh = request.args.get("shuf")
    if r1:
        rg1 = int(r1)
    if r2:
        rg2 = int(r2)
    if lp:
        loop = int(lp)
    if sh:
        shuf = sh.upper()
    l = list(range(rg1,rg2+1))
    if shuf == 'Y':
        l = random.sample(l,len(l))
    # pick 2 out of 3
    # loop=5
    for j in range(loop):
        ln = int(len(l)/3)
        rem = int(len(l) % 3)
        print('ln=',ln, rem)
        ofs = 0
        t = []
        for i in range(ln):
            x = random.sample(l[ofs:ofs+3],2)
            print(l[ofs:ofs+3],x)
            t.extend(x)
            ofs+=3
        # add the remainders
        rem = rem * -1
        print('rem=',rem)
        if rem < 0:
            t.extend(l[rem:])
        print(len(t),t)
        l = t[:]
        if shuf == 'Y':
            l = random.sample(l,len(l))
    return str(t)



@app.route("/eur", methods = ['GET', 'POST'])
def eur(c=[0,1,2,3,4,5,6,7,8,9],nb=10):
    #nb specifies the repetion number of 11's
    query = request.args.get("nb")
    if query:
        nb = int(query)
    # purpose :generate draws for euromillions
    # query = request.args.get("lt")
    #print(nb)
    l = list(range(1,51))
    s = list(range(1,13))
    s1 = random.sample(s,7)
    s2 = sorted(random.sample(s,3))
    x = random.sample(l,23)
    y =[]
    for q in range(nb):
        tmp = [0]+sorted(random.sample(x,11))
        y.append(tmp)
    #c = [0]+y
    #z = random.sample(y,7)
    #print(y)
    cbs = [
    		[ 1 , 2 , 4 , 6 , 9 ],
    		[ 1 , 2 , 4 , 6 , 10 ],
    		[ 1 , 2 , 4 , 6 , 11 ],
    		[ 1 , 2 , 4 , 7 , 9 ],
    		[ 1 , 2 , 4 , 7 , 10 ],
    		[ 1 , 2 , 4 , 7 , 11 ],
    		[ 1 , 2 , 4 , 8 , 9 ],
    		[ 1 , 2 , 4 , 8 , 10 ],
    		[ 1 , 2 , 4 , 8 , 11 ],
    		[ 1 , 2 , 5 , 6 , 9 ],
    		[ 1 , 2 , 5 , 6 , 10 ],
    		[ 1 , 2 , 5 , 6 , 11 ],
    		[ 1 , 2 , 5 , 7 , 9 ],
    		[ 1 , 2 , 5 , 7 , 10 ],
    		[ 1 , 2 , 5 , 7 , 11 ],
    		[ 1 , 2 , 5 , 8 , 9 ],
    		[ 1 , 2 , 5 , 8 , 10 ],
    		[ 1 , 2 , 5 , 8 , 11 ],
    		[ 1 , 3 , 4 , 6 , 9 ],
    		[ 1 , 3 , 4 , 6 , 10 ],
    		[ 1 , 3 , 4 , 6 , 11 ],
    		[ 1 , 3 , 4 , 7 , 9 ],
    		[ 1 , 3 , 4 , 7 , 10 ],
    		[ 1 , 3 , 4 , 7 , 11 ],
    		[ 1 , 3 , 4 , 8 , 9 ],
    		[ 1 , 3 , 4 , 8 , 10 ],
    		[ 1 , 3 , 4 , 8 , 11 ],
    		[ 1 , 3 , 5 , 6 , 9 ],
    		[ 1 , 3 , 5 , 6 , 10 ],
    		[ 1 , 3 , 5 , 6 , 11 ],
    		[ 1 , 3 , 5 , 7 , 9 ],
    		[ 1 , 3 , 5 , 7 , 10 ],
    		[ 1 , 3 , 5 , 7 , 11 ],
    		[ 1 , 3 , 5 , 8 , 9 ],
    		[ 1 , 3 , 5 , 8 , 10 ],
    		[ 1 , 3 , 5 , 8 , 11 ],
    		[ 2 , 3 , 4 , 6 , 9 ],
    		[ 2 , 3 , 4 , 6 , 10 ],
    		[ 2 , 3 , 4 , 6 , 11 ],
    		[ 2 , 3 , 4 , 7 , 9 ],
    		[ 2 , 3 , 4 , 7 , 10 ],
    		[ 2 , 3 , 4 , 7 , 11 ],
    		[ 2 , 3 , 4 , 8 , 9 ],
    		[ 2 , 3 , 4 , 8 , 10 ],
    		[ 2 , 3 , 4 , 8 , 11 ],
    		[ 2 , 3 , 5 , 6 , 9 ],
    		[ 2 , 3 , 5 , 6 , 10 ],
    		[ 2 , 3 , 5 , 6 , 11 ],
    		[ 2 , 3 , 5 , 7 , 9 ],
    		[ 2 , 3 , 5 , 7 , 10 ],
    		[ 2 , 3 , 5 , 7 , 11 ],
    		[ 2 , 3 , 5 , 8 , 9 ],
    		[ 2 , 3 , 5 , 8 , 10 ],
    		[ 2 , 3 , 5 , 8 , 11 ],
    	]
    l = [0,1,2]
    combs = []
    for c in y:
        print(c)
        for e1,i in enumerate(cbs):
            p = random.sample(l[:3],2)
            if (2 in p):
                c1 = []
                for j in i:
                    #print(c[j], end='-')
                    c1.append(c[j])
                combs.append(sorted(c1))
        #combs.append('======================')
    #combs = combs.sort()
    #print(combs)
    return render_template("eur.html", combs = combs, stars = s2, lcombs=len(combs))


# plan an help section
# with param /help to display all routes and possible parameters
@app.route("/help", methods = ['GET', 'POST'])
def hlp():
    # pass
    t = 'options = /eur /e2 /news /m4 /gc /gr '
    return str(t)


def index():
    # storedb()
    return "Hello World!"


@app.route("/rea", methods = ['GET', 'POST'])
def rea():
    # Test react page
    query = request.args.get("nb")
    if query:
        nb = int(query)
    return render_template("react.html")


if __name__ == '__main__':
    app.run(port=8000, debug=True)
