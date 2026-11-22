from bs4 import BeautifulSoup
from urllib import request, parse
from selenium import webdriver
import os
import re
import time


# 다운로드 메인 경로 (없으면 자동 생성)
path = 'D:\\Comics\\판타즈마 릴리 오리지널'

# 이 크기 이하의 이미지는 저장하지 않음 (디시콘, 광고 등 걸러내기용)
MIN_SIZE = 50 * 1024

# True 면 각 글 본문의 [시리즈] 박스에 있는 다른 화 링크도 따라가며 같이 받음
FOLLOW_SERIES = True

# 다운받을 링크 목록
link_list = [
'https://gall.dcinside.com/board/view/?id=comic_new6&no=7195221&exception_mode=recommend&page=1'
]


def _title(driver):
    # 타이틀 추출: "글 제목 - 갤러리명" 에서 갤러리명 제거, 파일명 금지 문자 치환
    title = driver.title.rsplit('-', maxsplit=1)[0]
    title = re.sub('[\\\\/:*?"<>|]', '？', title)
    return title.strip()


def _image_urls(html):
    # 본문(write_div) 안의 이미지만 대상으로 함 -> 댓글 디시콘, 다른 글 썸네일 제외
    soup = BeautifulSoup(html, 'html.parser')
    urls = []
    for img in soup.select('.write_div img'):
        # 지연 로딩 이미지는 src 에 로딩 gif 가 있고 실제 주소는 data-original 에 있음
        src = img.get('data-original') or img.get('src') or ''
        if 'dcimg' in src and src not in urls:
            urls.append(src)
    return urls


def _post_key(url):
    # 같은 글인지 판단하는 키: (갤러리 id, 글 번호). page, s_type 등 나머지 파라미터는 무시
    query = parse.parse_qs(parse.urlparse(url).query)
    return query.get('id', [''])[0], query.get('no', [''])[0]


def _series_urls(html):
    # 본문의 [시리즈] 박스(dc_series) 안에 있는 다른 화 링크 목록
    soup = BeautifulSoup(html, 'html.parser')
    return [a['href'] for a in soup.select('.dc_series a[href]')
            if 'gall.dcinside.com/board/view' in a['href']]


def _download(url, referer, cookie, user_agent):
    # Referer 가 없으면 403 이 나므로 글 주소를 Referer 로 넣고, 브라우저 쿠키도 함께 보냄
    headers = {'User-Agent': user_agent, 'Referer': referer, 'Cookie': cookie}
    with request.urlopen(request.Request(url, headers=headers), timeout=30) as res:
        data = res.read()
        # 원본 확장자는 Content-Disposition 의 파일명에서 가져옴
        disposition = res.headers.get('Content-Disposition') or ''
    match = re.search(r'filename=\"?([^\";]+)', disposition)
    extension = os.path.splitext(match.group(1))[1] if match else '.jpg'
    return data, extension or '.jpg'


# 크롬 드라이버 설정
# 드라이버 경로를 지정하지 않으면 Selenium Manager 가 설치된 크롬 버전을 확인해서
# 맞는 chromedriver 를 자동으로 내려받아 사용함 (Selenium 4.6 이상)
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')  # 브라우저 다운로드를 쓰지 않으므로 백그라운드 실행 가능
options.add_argument('--window-size=800,600')
options.add_argument('--disable-gpu')  # gpu 가속 안함 <- 셀레니움 작동시 동작 방해 가능성 있음
driver = webdriver.Chrome(options=options)
user_agent = driver.execute_script('return navigator.userAgent').replace('HeadlessChrome', 'Chrome')

# 받을 글 목록: link_list 로 시작해서, 시리즈 링크를 찾을 때마다 뒤에 추가함
queue = list(link_list)
seen = {_post_key(u) for u in queue}

try:
    while queue:
        url = queue.pop(0)

        # 지정된 주소 접속해 소스 추출
        driver.get(url)
        html = driver.page_source
        title = _title(driver)
        folder = os.path.join(path, title)
        print(f'\n[남은 글 {len(queue)}개] {folder}')

        # 시리즈 링크 수집 (이미 받은 글이어도 링크는 모아서 다른 화를 놓치지 않게 함)
        if FOLLOW_SERIES:
            added = 0
            for series_url in _series_urls(html):
                key = _post_key(series_url)
                if key not in seen:
                    seen.add(key)
                    queue.append(series_url)
                    added += 1
            if added:
                print(f'시리즈 링크 {added}개 추가')

        # 같은 제목 폴더에 파일이 있으면 이미 받은 글로 보고 건너뜀
        if os.path.isdir(folder) and os.listdir(folder):
            print('이미 받은 글이라 건너뜀')
            continue
        os.makedirs(folder, exist_ok=True)

        cookie = '; '.join(f"{c['name']}={c['value']}" for c in driver.get_cookies())
        urls = _image_urls(html)
        print(f'본문 이미지 {len(urls)}개')

        # 파일 다운로드: 본문 순서대로 001, 002 ... 로 저장
        count = 0
        for img_url in urls:
            try:
                data, extension = _download(img_url, url, cookie, user_agent)
            except Exception as e:
                print(f'Failed: {img_url} ({e})')
                continue
            if len(data) <= MIN_SIZE:
                print(f'Skipped (50KB 이하): {img_url}')
                continue
            count += 1
            file_path = os.path.join(folder, str(count).zfill(3) + extension)
            with open(file_path, 'wb') as f:
                f.write(data)
            print(f'Saved: {file_path}')

        # 글 사이에 잠깐 쉬어서 서버에 부담 주지 않게 함
        time.sleep(1)
finally:
    driver.quit()

print('*'*10, "실행 종료", '*'*10)
