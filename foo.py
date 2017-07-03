# subroutines to import


@app.route("/gc", methods = ['GET', 'POST'])
def get_res(dt='',reu=1, crs=1):
#def get_cotes(dt='170612', reu=1, crs=1, flg=9, cte=1, rdm='n', qt='n'):
    tmpdt  = request.args.get("dt")
    tmpreu = request.args.get("reu")
    tmpcrs = request.args.get("crs")
    if tmpdt:
        #here add validation on date -> YYMMDD throw error if format is invalid
        dt = tmpdt
    if tmpreu:
        reu = tmpreu
    if tmpreu:
        reu = tmpreu
    # dt format = YYMMDD
    ROOT_PROG = 'http://www.turfoo.fr/programmes-courses/'
    ROOT_RES = 'http://www.turfoo.fr/resultats-courses/'
    if dt != '':
        RES_URL  = ROOT_RES+dt
        PROG_URL = ROOT_PROG+dt
    api_url = api_root+'170612/reunion1-compiegne/course1-prix-major-fridolin/'
    api_url = str(get_race(reu,crs))
    print(api_url)
    # headers / user-agent
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
    payload = {}
    data = requests.get(api_url, headers = headers, params = payload)
    # use bs4 and get all races links
    soup = BeautifulSoup(data.content, 'html.parser')
    z = soup.find_all('div', class_="programme_partants")
    z1 = z[0].find_all('tr', class_="row")
    # print(len(z1))
    # recupere les cotes
    d1 = {}     #cotes1
    d2 = {}
    d3 = {}
    for e,i in enumerate(z1):
        # first regex to replace multiple \r\n by a space
        result = re.sub(r"(?sim)\r+|\n+", r"@", i.get_text())
        # replace multiple space by a ;
        result = re.sub(r"(?sim)@+", r";", result)
        t = result.split(';')
        # print(len(t),e+1,t[-5:-2])
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
    #print('cte=',cte)
    #print('Lt=',lt)
    #print('Lt=1',lt1)
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
    # here we store the data in 2 folds
    # 1. quintes    2. others
    v = m4(chlt,rt='raw',flg=flg,rdm=rdm)

    return render_template("m4.html", combs = sorted(v), lt=chlt,reu=reu, crs=crs, flg=flg, cte=cte)


