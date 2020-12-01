import os
import time
import re
import manatoki_cli as cli
from bs4 import BeautifulSoup
from concurrent import futures
from selenium import webdriver
from urllib import request

# 최대 프로세스 개수
MAX_PROCESS = 10
# 최대 쓰레드 개수
MAX_THREAD = 10
# 현재 폴더 경로
CURRENT_PATH = os.getcwd()
# 지정 경로
global SELLECT_PATH
SELLECT_PATH = 'D:\\Manatoki'


class Downloader():

    # 크롬드라이버로 다운로드
    def crome_download(self, url, folder):

        path = CURRENT_PATH

        chromeOptions = webdriver.ChromeOptions()
        # 창없는 모드로 실행, 봇 차단 방지위해 에어전트 정보 설정
        chromeOptions.add_argument('headless')
        chromeOptions.add_argument("disable-gpu")
        chromeOptions.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

        # 파일 다운로드 경로 변경
        prefs = {"download.default_directory": folder}
        chromeOptions.add_experimental_option("prefs", prefs)

        # 드라이버 실행
        chromedriver = path + '\\chromedriver.exe'
        driver = webdriver.Chrome(executable_path=chromedriver,
                                  chrome_options=chromeOptions)

        # 지정된 주소 접속
        driver.get(url)

        # 페이지 소스 추출
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 이미지 링크 추출, 디시는 실제 이미지를 별개의 도메인에 저장(이하는 동일)
        img_list = []
        img_list_pop = []
        # for link in soup.find_all('img', {'class': 'txc-image'}):
        for link in soup.find_all('img'):
            href = link.get('src')
            temp = str(href)
            if 'viewimage.php' in temp:
                # 불필요한 주소 삭제
                temp = re.sub('https://dcimg[0-9].dcinside.co.kr/', '', temp)
                temp = re.sub('https://dcimg[0-9].dcinside.com/', '', temp)

                # 추출 주소로 팝업 주소와 이미지 파일 주소 생성
                img_list.append('https://image.dcinside.com/' + temp)
                pop = temp.replace("viewimage.php", "viewimagePop.php")
                img_list_pop.append('https://image.dcinside.com/' + pop)

        print("img_list: ")
        print(img_list)

        # 이미지 파일 있으면 폴더 생성 및 다운로드
        if img_list:
            # 폴더 생성
            self.create_folder(folder)
            # 팝업 주소로 접속후 이미지 파일 주소 접속시 자동다운됨
            for i, link in enumerate(img_list_pop, 0):
                driver.get(link)
                driver.get(img_list[i])
                print(img_list[i] + ' is downloaded')
                time.sleep(2)
        else:
            # blogspot 업로드 파일 확인
            self.three_main(url)

        # 드라이버 종료
        driver.quit()

    # 게시글 하나에서만 이미지 다운
    def one_main(self, url):
        # url = 'https://gall.dcinside.com/board/view/?id=keion&no=181231'
        print(url)

        # 주소 파싱
        soup = self._parse(url)

        # 타이틀 추출 및 폴더 생성
        folder = self.get_title(soup)
        if folder:
            self.crome_download(url, folder)

    # 게시글에 포함된 링크 전체의 이미지 다운
    def two_main(self, url):
        # url = 'https://gall.dcinside.com/mgallery/board/view/?id=keionshuffle&no=11'

        # 주소 파싱
        cli_obj = cli.Downloader()
        soup = cli_obj._parse(url)

        # 각화 링크 추출
        page_list = []
        # 링크 주소에 클래스 속성이 없는 경우 필터링 하기가 어려움
        # for link in soup.find_all('a', {'class': 'tx-link'}):
        for link in soup.find_all('a'):
            href = link.get('href')
            page_list.append(href)

        # 각화 링크별 다운로드 실행
        # 실행될 최대 쓰레드 개수 설정
        workers = min(MAX_THREAD, len(page_list))

        # with futures.ProcessPoolExecutor(workers) as executor:
        with futures.ThreadPoolExecutor(workers) as executor:
            # executor.map(self.two_sub_main, page_list)
            executor.map(self.one_main, page_list)

    # 게시글 하나에서만 이미지 다운
    def two_sub_main(self, url):
        # url = 'https://gall.dcinside.com/board/view/?id=keion&no=181231'

        # 주소 파싱
        soup = self._parse(url)

        # 파싱되는 주소가 다른 페이지로 리다이렉트 됨으로 추출해서 다시 파싱 필요
        temp_url = str(soup)
        spl_url = temp_url.split("'", maxsplit=1)
        rspl_url = spl_url[1].rsplit("'", maxsplit=1)
        url = 'https://gall.dcinside.com' + rspl_url[0]

        print(url)

        # 링크 되는 주소로 다시 파싱
        soup = self._parse(url)

        # 타이틀 추출 및 폴더 생성
        folder = self.get_title(soup)
        if folder:
            self.crome_download(url, folder)

    # 구글 저장된 페이지 다운
    def three_main(self, url):
        # url = 'https://gall.dcinside.com/board/view/?id=keion&no=181231'
        print(url)

        # 주소 파싱
        soup = self._parse(url)

        img_list = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                if 'blogspot.com' in href:
                    img_list.append(href)

        print(img_list)

        # 이미지 파일 없으면 삭제
        if not img_list:
            return

        # 타이틀 추출 및 폴더 생성
        folder = self.get_title(soup)
        if folder:
            self.create_folder(folder)
            get_obj = cli.CreateRequests()
            # 이미지 파일 다운로드
            for i, img in enumerate(img_list, 1):
                # file_name = img.rsplit('/', maxsplit=1)
                file_ext = img.rsplit('.', maxsplit=1)
                num = '%03d' % i
                file_name = num + '.' + file_ext[1]
                print(file_name)
                locate = folder + '\\' + file_name
                if not os.path.exists(locate):
                    with open(locate, mode="wb") as file:
                        response = get_obj.get(img)
                        file.write(response.content)

    # 저장폴더 변경 메소드
    def change_folder(self, forlder):

        global SELLECT_PATH
        # 디폴트 폴더 변경시 이하로 수정
        # SELLECT_PATH = CURRENT_PATH + '\\' + forlder
        SELLECT_PATH = 'D:\\Manatoki' + '\\' + forlder
        if not os.path.exists(SELLECT_PATH):
            os.mkdir(SELLECT_PATH)

    # 링크 파싱
    def _parse(self, url):
        req_url = request.Request(url, headers={'User-Agent': 'Mozilla/6.0'})
        response = request.urlopen(req_url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        return soup

    # 타이틀 추출 및 폴더 경로작성
    def get_title(self, soup):

        path = SELLECT_PATH

        # 타이틀 추출
        title = soup.title.get_text()
        title_split = title.rsplit('-', maxsplit=1)
        title_re = re.sub(
            '[\\/:*\?\"<>|]', '？', title_split[0])
        title = title_re.strip()
        print(title)

        # 저장될 폴더 경로 작성
        if title:
            folder = path + '\\' + title
        else:
            folder = ''

        # if not os.path.exists(folder):
        #     os.mkdir(folder)
        # else:
        #     print(title + ' is exist')
        #     folder = ''

        return folder

    # 폴더 생성
    def create_folder(self, folder):

        # 저장될 폴더 생성
        if not os.path.exists(folder):
            os.mkdir(folder)
        else:
            print(folder + ' is exist')
            folder = ''


if __name__ == "__main__":
    # url = 'https://gall.dcinside.com/board/view/?id=keion&no=181231'

    print("*"*70)
    print("다운받을 디시 주소를 입력하고 엔터를 누르시오.")
    print("1. 이미지가 포함되어 있는 주소")
    print("2. 링크가 포함되어 있는 주소 (각화 모음)")
    print("3. 삭제된 주소 (구글 저장된 페이지)")
    print("q를 입력하면 종료 합니다.")
    print("*"*70)

    cli_input = input()
    obj = Downloader()

    try:
        if cli_input == 'q':
            os._exit(0)
        elif cli_input == '1':
            print("다운받을 주소를 입력하세요.")
            url = input()
            obj.one_main(url)
        elif cli_input == '2':
            print("다운받을 주소를 입력하세요.")
            url = input()
            obj.two_main(url)
        elif cli_input == '3':
            print("다운받을 주소를 입력하세요.")
            url = input()
            obj.three_main(url)
    except Exception as e:
        print(e)

    print("*"*70)
    print("작업이 종료 되었습니다.")
    print("*"*70)
