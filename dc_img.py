from bs4 import BeautifulSoup
from urllib import request
from selenium import webdriver
import os
import re
import time


def _parse(url):
    req_url = request.Request(url, headers={'User-Agent': 'Mozilla/6.0'})
    response = request.urlopen(req_url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    # 타이틀 추출
    title = soup.title.get_text()
    title_split = title.rsplit('-', maxsplit=1)
    title_re = re.sub(
        '[\\/:*\?\"<>|]', '？', title_split[0])
    title = title_re.strip()
    print(title)

    return title


# 다운로드 메인 경로
path = 'D:\\Hitomi_jmana\\페도마스'

# 다운받을 링크 목록
link_list = [
'https://gall.dcinside.com/board/view/?id=idolmaster_new1&no=3621771'
]

for url in link_list:
    # 타이틀 추출 및 파일 다운로드 경로 변경
    title = _parse(url)
    folder = path + '\\' + title
    print(folder)
    if not os.path.exists(folder):
        os.mkdir(folder)
    prefs = {"download.default_directory": folder}
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", prefs)

    # 크롬 드라이버 설정 및 실행
    options.add_argument('window-size=800x600')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    # options.add_argument('headless')  # 백그라운드 실행하면 중복된 파일명이 하나만 저장됨
    options.add_argument("disable-gpu")  # gpu 가속 안함 <- 셀레니움 작동시 동작 방해 가능성 있음
    driver = webdriver.Chrome(path + '\\chromedriver.exe', options=options)

    # 지정된 주소 접속해 소스 추출
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 파일 다운로드
    # gallview_contents = soup.find_all("div", class_="gallview_contents")
    for link in soup.find_all('img'):
        href = link.get('src')
        temp = str(href)
        if 'dcimg' in temp:
            print(temp)
            driver.get(temp)
            # 너무 빠르면 다운로드가 다 안돼서 딜레이 줌
            time.sleep(1)

    # 폴더 내의 모든 파일 및 디렉토리 가져오기
    files = os.listdir(folder)

    # 파일만 필터링하고 시간 순서로 정렬
    files = [f for f in files if os.path.isfile(os.path.join(folder, f))]
    files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(folder, f)))

    # 파일명 변경 및 삭제
    for i, filename in enumerate(files):
        # 파일 경로
        file_path = os.path.join(folder, filename)

        # 파일 크기 확인 (바이트 단위)
        file_size = os.path.getsize(file_path)

        if file_size <= 50 * 1024:  # 50KB 이하인 경우
            # 파일 삭제
            os.remove(file_path)
            print(f'Deleted: {file_path}')
        else:
            # 파일명 변경
            _, extension = os.path.splitext(filename)
            new_filename = str(i+1).zfill(3) + extension
            new_path = os.path.join(folder, new_filename)
            os.rename(file_path, new_path)
            print(f'Renamed: {file_path} => {new_path}')

print('*'*10, "실행 종료", '*'*10)
