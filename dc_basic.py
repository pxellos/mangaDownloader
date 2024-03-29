from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib import request
import os
import time


def _parse(url):
    req_url = request.Request(url, headers={'User-Agent': 'Mozilla/6.0'})
    response = request.urlopen(req_url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    return soup


# 주소 입력
# url = input()
# soup = _parse(url)
# print(soup)

# for link in soup.find_all('img', {'class': 'image_mid'}):
#     href = link.get('src')

# for a in soup.find_all('a', href=True):
#     print('"'+a['href']+'"', ',')

link_list = [
"https://gall.dcinside.com/idolmaster/4479201" ,
"https://gall.dcinside.com/idolmaster/4749329" ,
"https://gall.dcinside.com/idolmaster/4869427" ,
"https://gall.dcinside.com/idolmaster/4961881" ,
"https://gall.dcinside.com/idolmaster/5062069" ,
"https://gall.dcinside.com/idolmaster/5158256" ,
"https://gall.dcinside.com/idolmaster/5263498" ,
"https://gall.dcinside.com/idolmaster/6629089" ,
"https://gall.dcinside.com/idolmaster/6588845" ,
"https://gall.dcinside.com/idolmaster/5366711" ,
"https://gall.dcinside.com/idolmaster/5460893" ,
"https://gall.dcinside.com/idolmaster/5561135" ,
"https://gall.dcinside.com/idolmaster/5660931" ,
"https://gall.dcinside.com/idolmaster/5755802" ,
"https://gall.dcinside.com/idolmaster/5973890" ,
"https://gall.dcinside.com/idolmaster/6079933" ,
"https://gall.dcinside.com/idolmaster/6193272" ,
"https://gall.dcinside.com/idolmaster/6330126" ,
"https://gall.dcinside.com/idolmaster/6586576" ,
"https://gall.dcinside.com/idolmaster/6709593" ,
"https://gall.dcinside.com/idolmaster/6827090" ,
"https://gall.dcinside.com/idolmaster/6946042" ,
"https://gall.dcinside.com/idolmaster/7005667" ,
"https://gall.dcinside.com/idolmaster/7131229" ,
"https://gall.dcinside.com/idolmaster/7363599" ,
"https://gall.dcinside.com/idolmaster/7494790" ,
"https://gall.dcinside.com/idolmaster/7560825" ,
"https://gall.dcinside.com/idolmaster/7827623" ,
"https://gall.dcinside.com/idolmaster/7975852" ,
"https://gall.dcinside.com/idolmaster/8126329" ,
"https://gall.dcinside.com/idolmaster/8250980" ,
"https://gall.dcinside.com/idolmaster/8260198" ,
"https://gall.dcinside.com/idolmaster/8390111" ,
"https://gall.dcinside.com/idolmaster/8665580" ,
"https://gall.dcinside.com/idolmaster/8795094" ,
"https://gall.dcinside.com/idolmaster/8918974" ,
"https://gall.dcinside.com/idolmaster/9045902" ,
"https://gall.dcinside.com/idolmaster/9183773" ,
"https://gall.dcinside.com/idolmaster_new1/1446949" ,
"https://gall.dcinside.com/idolmaster/9316992" ,
"https://gall.dcinside.com/idolmaster/9357935" ,
"https://gall.dcinside.com/idolmaster/9436293" ,
"https://gall.dcinside.com/idolmaster/9554842" ,
"https://gall.dcinside.com/idolmaster/9676718" ,
"https://gall.dcinside.com/idolmaster/9808204" ,
"https://gall.dcinside.com/idolmaster/9940755" ,
"https://gall.dcinside.com/idolmaster/10180037" ,
"https://gall.dcinside.com/idolmaster/10319823" ,
"https://gall.dcinside.com/idolmaster/10572201" ,
"https://gall.dcinside.com/idolmaster/10855502" ,
"https://gall.dcinside.com/idolmaster/10821676" ,
"https://gall.dcinside.com/idolmaster/11098788" ,
"https://gall.dcinside.com/idolmaster/11099822" ,
"https://gall.dcinside.com/idolmaster/11100480" ,
"https://gall.dcinside.com/idolmaster/11239471" ,
"https://gall.dcinside.com/idolmaster/11372221" ,
"https://gall.dcinside.com/idolmaster/11499540" ,
"https://gall.dcinside.com/idolmaster/11620251" ,
"https://gall.dcinside.com/idolmaster/11735838" ,
"https://gall.dcinside.com/idolmaster/11854158" ,
"https://gall.dcinside.com/idolmaster/11986402" ,
"https://gall.dcinside.com/idolmaster/12101582" ,
"https://gall.dcinside.com/idolmaster/12229017" ,
"https://gall.dcinside.com/idolmaster/12356424" ,
"https://gall.dcinside.com/idolmaster/12479303" ,
"https://gall.dcinside.com/idolmaster/12608952" ,
"https://gall.dcinside.com/idolmaster/12810772" ,
"https://gall.dcinside.com/idolmaster/12745336" ,
"https://gall.dcinside.com/idolmaster/12931814" ,
"https://gall.dcinside.com/idolmaster/12869317" ,
"https://gall.dcinside.com/idolmaster/13057843" ,
"https://gall.dcinside.com/idolmaster/12991420" ,
"https://gall.dcinside.com/idolmaster/13122674" ,
"https://gall.dcinside.com/idolmaster/13191135" ,
"https://gall.dcinside.com/idolmaster/13256323" ,
"https://gall.dcinside.com/idolmaster/13316401" ,
"https://gall.dcinside.com/idolmaster/13378601" ,
"https://gall.dcinside.com/idolmaster/13434749" ,
"https://gall.dcinside.com/idolmaster/13494482" ,
"https://gall.dcinside.com/idolmaster/13556278" ,
"https://gall.dcinside.com/idolmaster/13623401" ,
"https://gall.dcinside.com/idolmaster/13686797" ,
"https://gall.dcinside.com/idolmaster/13751053" ,
"https://gall.dcinside.com/idolmaster/13814274" ,
"https://gall.dcinside.com/idolmaster/13878162" ,
"https://gall.dcinside.com/idolmaster/13940463" ,
"https://gall.dcinside.com/idolmaster/14005112" ,
"https://gall.dcinside.com/idolmaster/14066368" ,
"https://gall.dcinside.com/idolmaster/14128030" ,
"https://gall.dcinside.com/idolmaster/14187965" ,
"https://gall.dcinside.com/idolmaster/14246382" ,
"https://gall.dcinside.com/idolmaster/14299529" ,
"https://gall.dcinside.com/idolmaster/14351304" ,
"https://gall.dcinside.com/idolmaster/14458776" ,
"https://gall.dcinside.com/idolmaster/14511781" ,
"https://gall.dcinside.com/idolmaster/14564782" ,
"https://gall.dcinside.com/idolmaster/14625175" ,
"https://gall.dcinside.com/idolmaster/14685155" ,
"https://gall.dcinside.com/idolmaster/14742943" ,
"https://gall.dcinside.com/idolmaster/14808071" ,
"https://gall.dcinside.com/idolmaster/14869251" ,
"https://gall.dcinside.com/idolmaster/14926463" ,
"https://gall.dcinside.com/idolmaster/14983688" ,
"https://gall.dcinside.com/idolmaster/15041442" ,
"https://gall.dcinside.com/idolmaster/15099421" ,
"https://gall.dcinside.com/idolmaster/15161395" ,
"https://gall.dcinside.com/idolmaster/15272408" ,
"https://gall.dcinside.com/idolmaster/15327203" ,
"https://gall.dcinside.com/idolmaster/15381392" ,
"https://gall.dcinside.com/idolmaster/15435430" ,
"https://gall.dcinside.com/idolmaster/15493514" ,
"https://gall.dcinside.com/idolmaster/15609414" ,
"https://gall.dcinside.com/idolmaster/15670265" ,
"https://gall.dcinside.com/idolmaster/15728283" ,
"https://gall.dcinside.com/idolmaster/15791740" ,
"https://gall.dcinside.com/idolmaster/15854191" ,
"https://gall.dcinside.com/idolmaster/15911973" ,
"https://gall.dcinside.com/idolmaster/15972388" ,
"https://gall.dcinside.com/idolmaster/16029828" ,
"https://gall.dcinside.com/idolmaster/16078627" ,
"https://gall.dcinside.com/idolmaster/16134007" ,
"https://gall.dcinside.com/idolmaster/16192706" ,
"https://gall.dcinside.com/idolmaster/16248982" ,
"https://gall.dcinside.com/idolmaster/16306850" ,
"https://gall.dcinside.com/idolmaster/16417760" ,
"https://gall.dcinside.com/idolmaster/16464779" ,
"https://gall.dcinside.com/idolmaster/16513026" ,
"https://gall.dcinside.com/idolmaster/16560808" ,
"https://gall.dcinside.com/idolmaster/16615203" ,
"https://gall.dcinside.com/idolmaster/16682553" ,
"https://gall.dcinside.com/idolmaster/16750939" ,
"https://gall.dcinside.com/idolmaster/16815270" ,
"https://gall.dcinside.com/idolmaster/16875243" ,
"https://gall.dcinside.com/idolmaster/16932877" ,
"https://gall.dcinside.com/idolmaster/16991517" ,
"https://gall.dcinside.com/idolmaster/17046817" ,
"https://gall.dcinside.com/idolmaster/17106756" ,
"https://gall.dcinside.com/idolmaster/17173040" ,
"https://gall.dcinside.com/idolmaster/17233940" ,
"https://gall.dcinside.com/idolmaster/17298237" ,
"https://gall.dcinside.com/idolmaster/17359019" ,
"https://gall.dcinside.com/idolmaster/17417221" ,
"https://gall.dcinside.com/idolmaster/17530222" ,
"https://gall.dcinside.com/idolmaster/17579971" ,
"https://gall.dcinside.com/idolmaster/17627733" ,
"https://gall.dcinside.com/idolmaster/17682781" ,
"https://gall.dcinside.com/idolmaster/17731351" ,
"https://gall.dcinside.com/idolmaster/17788202" ,
"https://gall.dcinside.com/idolmaster/18134484" ,
"https://gall.dcinside.com/idolmaster/17905265" ,
"https://gall.dcinside.com/idolmaster/17959079" ,
"https://gall.dcinside.com/idolmaster/18017428" ,
"https://gall.dcinside.com/idolmaster/18082492" ,
"https://gall.dcinside.com/idolmaster/18182587" ,
"https://gall.dcinside.com/idolmaster/18232155" ,
"https://gall.dcinside.com/idolmaster/18278730" ,
"https://gall.dcinside.com/idolmaster/18330515" ,
"https://gall.dcinside.com/idolmaster/18380282" ,
"https://gall.dcinside.com/idolmaster/18427124" ,
"https://gall.dcinside.com/idolmaster/18472513" ,
"https://gall.dcinside.com/idolmaster/18523363" ,
"https://gall.dcinside.com/idolmaster/18573436" ,
"https://gall.dcinside.com/idolmaster/18619614" ,
"https://gall.dcinside.com/idolmaster/18668890" ,
"https://gall.dcinside.com/idolmaster/18715834" ,
"https://gall.dcinside.com/idolmaster/18835323" ,
"https://gall.dcinside.com/idolmaster/18883814" ,
"https://gall.dcinside.com/idolmaster/18930377" ,
"https://gall.dcinside.com/idolmaster/18976389" ,
"https://gall.dcinside.com/idolmaster/19073397" ,
"https://gall.dcinside.com/idolmaster/19120761" ,
"https://gall.dcinside.com/idolmaster/19175057" ,
"https://gall.dcinside.com/idolmaster/19235081" ,
"https://gall.dcinside.com/idolmaster/19348018" ,
"https://gall.dcinside.com/idolmaster/19397067" ,
"https://gall.dcinside.com/idolmaster/19444912" ,
"https://gall.dcinside.com/idolmaster_new1/28232" ,
"https://gall.dcinside.com/idolmaster_new1/131397" ,
"https://gall.dcinside.com/idolmaster_new1/179860" ,
"https://gall.dcinside.com/idolmaster_new1/228310" ,
"https://gall.dcinside.com/idolmaster_new1/273862" ,
"https://gall.dcinside.com/idolmaster_new1/373534" ,
"https://gall.dcinside.com/idolmaster_new1/422245" ,
"https://gall.dcinside.com/idolmaster_new1/512202" ,
"https://gall.dcinside.com/idolmaster_new1/603246" ,
"https://gall.dcinside.com/idolmaster_new1/651065" ,
"https://gall.dcinside.com/idolmaster_new1/699995" ,
"https://gall.dcinside.com/idolmaster_new1/744462" ,
"https://gall.dcinside.com/idolmaster_new1/834235" ,
"https://gall.dcinside.com/idolmaster_new1/877461" ,
"https://gall.dcinside.com/idolmaster_new1/916879" ,
"https://gall.dcinside.com/idolmaster_new1/956509" ,
"https://gall.dcinside.com/idolmaster_new1/1029886" ,
"https://gall.dcinside.com/idolmaster_new1/1068410" ,
"https://gall.dcinside.com/idolmaster_new1/1111015" ,
"https://gall.dcinside.com/idolmaster_new1/1149084" ,
"https://gall.dcinside.com/idolmaster_new1/1348455" ,
"https://gall.dcinside.com/idolmaster_new1/1391680" ,
"https://gall.dcinside.com/idolmaster_new1/1434959" ,
"https://gall.dcinside.com/idolmaster_new1/1483392" ,
"https://gall.dcinside.com/idolmaster_new1/1568282" ,
"https://gall.dcinside.com/idolmaster_new1/1607092" ,
"https://gall.dcinside.com/idolmaster_new1/1646291" ,
"https://gall.dcinside.com/idolmaster_new1/1684117" ,
"https://gall.dcinside.com/idolmaster_new1/1766011" ,
"https://gall.dcinside.com/idolmaster_new1/1805527" ,
"https://gall.dcinside.com/idolmaster_new1/1856167" ,
"https://gall.dcinside.com/idolmaster_new1/1897043" ,
"https://gall.dcinside.com/idolmaster_new1/1971287" ,
"https://gall.dcinside.com/idolmaster_new1/2006984" ,
"https://gall.dcinside.com/idolmaster_new1/2047263" ,
"https://gall.dcinside.com/idolmaster_new1/2082176" ,
"https://gall.dcinside.com/idolmaster_new1/2150249" ,
"https://gall.dcinside.com/idolmaster_new1/2184854" ,
"https://gall.dcinside.com/idolmaster_new1/2231595" ,
"https://gall.dcinside.com/idolmaster_new1/2271500" ,
"https://gall.dcinside.com/idolmaster_new1/2348634" ,
"https://gall.dcinside.com/idolmaster_new1/2384080" ,
"https://gall.dcinside.com/idolmaster_new1/2417480" ,
"https://gall.dcinside.com/idolmaster_new1/2451250" ,
"https://gall.dcinside.com/idolmaster_new1/2514230" ,
"https://gall.dcinside.com/idolmaster_new1/2546271" ,
"https://gall.dcinside.com/idolmaster_new1/2579929" ,
"https://gall.dcinside.com/idolmaster_new1/2622653" ,
"https://gall.dcinside.com/idolmaster_new1/2708165" ,
"https://gall.dcinside.com/idolmaster_new1/2751251" ,
"https://gall.dcinside.com/idolmaster_new1/2791031" ,
"https://gall.dcinside.com/idolmaster_new1/2830293" ,
"https://gall.dcinside.com/idolmaster_new1/2922669" ,
"https://gall.dcinside.com/idolmaster_new1/2962529" ,
"https://gall.dcinside.com/idolmaster_new1/3001444" ,
"https://gall.dcinside.com/idolmaster_new1/3043530" ,
"https://gall.dcinside.com/idolmaster_new1/3122286" ,
"https://gall.dcinside.com/idolmaster_new1/3165520" ,
"https://gall.dcinside.com/idolmaster_new1/3319737" ,
"https://gall.dcinside.com/idolmaster_new1/3358830" ,
"https://gall.dcinside.com/idolmaster_new1/3398992" ,
"https://gall.dcinside.com/idolmaster_new1/3444028" ,
"https://gall.dcinside.com/idolmaster_new1/3487121" ,
"https://gall.dcinside.com/idolmaster_new1/3533654" ,
"https://gall.dcinside.com/idolmaster_new1/3576182" ,
"https://gall.dcinside.com/idolmaster_new1/3621771" ,
"https://gall.dcinside.com/idolmaster_new1/3661836" ,
]

# 크롬드라이버 로드
options = webdriver.ChromeOptions()
# options.add_argument('headless')
options.add_argument('window-size=800x600')
# options.add_argument("disable-gpu")

# UserAgent값 변경(비정상 접속차단 회피)
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
path = os.getcwd()
driver = webdriver.Chrome(path + '\\chromedriver.exe', options=options)

err_list = ['https://gall.dcinside.com/idolmaster/4869427', 'https://gall.dcinside.com/idolmaster/6629089', 'https://gall.dcinside.com/idolmaster/6588845', 'https://gall.dcinside.com/idolmaster/8250980', 'https://gall.dcinside.com/idolmaster/9357935', 'https://gall.dcinside.com/idolmaster/9436293', 'https://gall.dcinside.com/idolmaster/9554842']

for i in link_list:
    # print(i)
    driver.get(i)
    # print(driver.page_source)
    try:
        driver.find_element(By.XPATH, r'//*[@id="container"]/section/article[2]/div[1]/div/div[6]/a').click()
    except Exception:
        err_list.append(i)
    time.sleep(5)

print(err_list)
