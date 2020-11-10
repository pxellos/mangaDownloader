import os
import re
import manatoki_cli as cli
import dc_cli as dc
from urllib import request
from bs4 import BeautifulSoup
from requests import get
# from multiprocessing import Process, Queue
from concurrent import futures
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys

# 최대 프로세스 개수
MAX_PROCESS = 10
# 최대 쓰레드 개수, 한화에 파일 개수가 많은 경우 다른 스레드에서 타임아웃 발생함에 따라 줄임
MAX_THREAD = 10
# 현재 폴더 경로
CURRENT_PATH = os.getcwd()
# 지정 경로
global SELLECT_PATH
SELLECT_PATH = 'D:\\Manatoki'
# SELLECT_PATH = CURRENT_PATH
# 비밀번호
global PASSWORD
PASSWORD = '1111'


class Downloader():

    # 이미지 저장 메소드
    def download(self, url, file_name, path):

        locate = path + '\\' + file_name
        if not os.path.exists(locate):
            with open(locate, mode="wb") as file:   # open in binary mode
                response = get(url)                 # get request
                file.write(response.content)        # write to file

        # 파일 크기가 100KB 미만이면 삭제
        file_size = os.path.getsize(locate)
        if file_size < 100000:
            os.remove(locate)
            return False

        return True

    # 크롬드라이버로 파싱
    def crome_parse(self, url):

        # 크롬드라이버 로드
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=800x600')
        options.add_argument("disable-gpu")

        # UserAgent값 변경(비정상 접속차단 회피)
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

        path = CURRENT_PATH
        driver = webdriver.Chrome(path + '\\chromedriver.exe', options=options)

        driver.get(url)

        # # 패스워드 입력창을 찾기 위한 이름 작성, 아이디 입력 필요경우 수정
        # num = url.rsplit('/')
        # name = 'entry' + num[len(num) - 1] + 'password'
        # driver.find_element_by_name(name).send_keys('1111')

        # 패스워드를 입력
        # driver.find_element_by_tag_name('input').send_keys('1111')
        driver.find_element_by_xpath(
            "//input[@type='password']").send_keys(PASSWORD)

        # 확인 버튼을 클릭, 경로가 다른경우가 있어서 예외처리로 수행
        try:
            driver.find_element_by_xpath('//button[@type="submit"]').click()
        except Exception:
            submit_path = '/html/body/div/div/main/div/div/div/div/div/form/button[@type="submit"]'
            driver.find_element_by_xpath(submit_path).click()

        # 패스워드 입력후 글이 보여지면 정보 취득
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 드라이버 종료
        driver.quit()

        return soup

    # 도메인 추출 메소드, 카테고리에서 각 링크는 뒤에 번호만 나오기 때문에 필요
    def domain_parse(self, url):

        spl_str = '.com'
        domain = url.split(spl_str)
        domain_name = domain[0] + spl_str

        return domain_name

    # 총 페이지 주소 추출 메소드
    def page_parse(self, url, domain_name):

        soup = self._parse(url)

        # 타이틀 추출
        title = soup.title.get_text()
        title_split = title.rsplit("'", maxsplit=1)
        title = title_split[0][1:]
        title_re = re.sub('[\\/:*\?\"<>|]', '？', title)
        title_strip = title_re.strip()

        print(title_strip)

        # 페이지 번호 없을 경우 붙임
        if '/page/' not in url:
            url = url + '/page/1'

        # 링크가 중복되는 경우 있어서 set객체로 저장
        page_set = set()
        page_set.add(url)

        max_num = 1

        temp = soup.find_all('div', {'id': 'titlelist_paging'})
        s = temp[0].find_all('a')
        num = len(s)
        # 페이지 번호가 있을 때, 10이 넘어가서 다음이 있을때의 수정 필요
        if num > 0:
            max_num = s[num-1].get_text().strip()
            cnt = 0
            next_num = ''
            while 1:
                if max_num == '다음':
                    if cnt == 0:
                        next_num = s[num-2].get_text().strip()

                    max_num, url, next_num = self.next_page(url, next_num)
                    print(max_num)
                    print(url)
                    cnt = cnt + 1
                else:
                    break

            # 페이지 번호별 주소 생성
            for i in range(1, int(max_num) + 1):
                _url = url.replace('/page/1', '/page/{}'.format(i))
                page_set.add(_url)

        return page_set, title_strip

    # 다음 페이지 번호 추출
    def next_page(self, url, next_num):
        i = int(next_num) + 1
        _url = url.replace('/page/1', '/page/{}'.format(i))

        max_num = next_num

        soup = self._parse(_url)

        temp = soup.find_all('div', {'id': 'titlelist_paging'})
        s = temp[0].find_all('a')
        num = len(s)

        # 페이지 번호가 있을 때, 10이 넘어가서 다음이 있을때의 수정 필요
        if num > 0:
            max_num = s[num-1].get_text().strip()
            next_num = s[num-2].get_text().strip()

        return max_num, _url, next_num

    # 각 화 링크 주소 추출 메소드
    def link_parse(self, soup, domain_name):

        mode = 0

        link_set = set()
        soup_list = soup.find_all('div', {'id': 'titlelist_list'})
        href = soup_list[0].find_all('a')

        for link in href:
            temp_link = link.get('href')
            temp_name = domain_name + str(temp_link)
            link_set.add(temp_name)

        # set에 정보가 없으면 패스워드 입력란이 있음
        # 따라서 크롬드라이버로 파싱 수행하게 모드 설정
        if not link_set:
            mode = 1
            for link in soup_list:
                temp_link = link.get('href')

                # 비밀번호가 있을 때의 링크 주소 획득
                if re.match('/([0-9])', str(temp_link)):
                    temp_name = domain_name + str(temp_link)
                    link_set.add(temp_name)

        return link_set, mode

    # 타이틀 추출 및 폴더 경로작성
    def get_title(self, soup, path):

        # 타이틀 추출
        title = soup.title.get_text()
        # title_split = title.rsplit('-', maxsplit=1)
        title_re = re.sub(
            '[\\/:*\?\"<>|]', '？', title)
        title = title_re.strip()
        print(title)

        # 저장될 폴더 경로 작성
        if title:
            folder = path + '\\' + title
        else:
            folder = ''

        return folder

    # 각 화 이미지 추출 및 저장 메소드
    def image_parse(self, soup, path):

        # 타이틀 추출
        folder = self.get_title(soup, path)
        print(folder)

        img_list = []
        http = 'http://'

        # for link in soup.find_all('img', {'class': 'image_mid'}):
        #     href = link.get('src')
        #     if href:
        #         img_list.append(href)
        #         print(href)

        # 썸네일이 있는 경우
        for link in soup.find_all('img', {'class': 'image_mid'}):
            href = link.get('src')
            if href:
                if 'thumbnail' in href:
                    src_temp = href.rsplit(http, maxsplit=1)
                    src = http + src_temp[1]
                    img_list.append(src)
                    print(src)
                else:
                    img_list.append(href)
                    print(href)

        # 패스워드 있어서 이미지 없을시 예외발생해서 크롬다운로드 실행
        if len(img_list) < 2:
            raise Exception

        if not os.path.exists(folder):
            os.mkdir(folder)
            get_obj = cli.CreateRequests()
            print(folder)
        else:
            print(folder + ' is exist')
            return

        # 이미지 파일 다운로드
        for i, img in enumerate(img_list, 1):
            file_ext = img.rsplit('.', maxsplit=1)
            num = '%03d' % i
            file_name = num + '.' + file_ext[1]
            print(file_name)
            locate = folder + '\\' + file_name
            if not os.path.exists(locate):
                with open(locate, mode="wb") as file:
                    print(img)
                    response = get_obj.get(img)
                    file.write(response.content)

    # soup 웹 파싱 메소드
    def _parse(self, url):
        # with request.urlopen(web_url) as response:
        #     html = response.read()
        #     soup = BeautifulSoup(html, 'html.parser')
        req_url = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = request.urlopen(req_url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        return soup

    # 멀티 쓰레딩으로 각화 다운
    def _multi_threading(self, page_tuple):

        link = page_tuple[0]
        mode = page_tuple[1]
        path = page_tuple[2]

        # 비밀번호 설정된 경우
        if mode == 1:
            # 셀레티움으로 링크 주소에서 다운받을 이미지 주소 파싱
            soup = self.crome_parse(link)
            try:
                # 이미지 다운로드 실행
                self.image_parse(soup, path)
            except Exception as e:
                print(e)
        else:
            # 비밀번호 없는 경우는 requests사용 (빠름)
            soup = self._parse(link)
            try:
                # 이미지 다운로드 실행
                self.image_parse(soup, path)
            except Exception as e:
                print(e)

    # 카테고리 통해 전체 다운
    def main(self, url):
        path = SELLECT_PATH

        # 홈페이지 메인주소 작성 ex) xxx.tistory.com
        # 카테고리에서 각 링크 주소를 추출해서 작성하는데 필요
        domain_name = self.domain_parse(url)
        print(domain_name)

        # 페이지 번호를 포함한 전체 주소 리스트 획득
        page_set, title = self.page_parse(url, domain_name)
        print(title)
        folder = path + '\\' + title
        if not os.path.exists(folder):
            os.mkdir(folder)

        print(page_set)

        for page in page_set:
            soup = self._parse(page)
            link_set, mode = self.link_parse(soup, domain_name)
            page_tuple_list = []
            for link in link_set:
                temp = (link, mode, folder)
                page_tuple_list.append(temp)

            # 실행될 최대 쓰레드 개수 설정
            workers = min(MAX_THREAD, len(link_set))
            with futures.ThreadPoolExecutor(workers) as executor:
                executor.map(self._multi_threading, page_tuple_list)

    # 해당 게시글 한화만 다운
    def one_main(self, url):

        path = SELLECT_PATH
        soup = self._parse(url)

        # 비밀번호 없는 경우, 있는 경우는 예외처리로 수행
        try:
            # 이미지 다운로드 실행
            self.image_parse(soup, path)
        except Exception:
            # 비밀번호 설정된 경우
            # 셀레티움으로 링크 주소에서 다운받을 이미지 주소 파싱
            soup = self.crome_parse(url)
            try:
                # 이미지 다운로드 실행
                self.image_parse(soup, path)
            except Exception as e:
                print(e)

    # 비밀글 입력 패스워드 변경 메소드 (gui에서 사용)
    def change_password(self, password):
        global PASSWORD
        PASSWORD = password


if __name__ == "__main__":
    while True:
        print("*"*70)
        print("정보를 수집할 티스토리 주소를 입력하세요.")
        print("1. 한화 주소")
        print("2. 카테고리 주소(전체)")
        print("q를 입력하면 종료 합니다.")
        print("*"*70)

        # url = 'https://garbage6974.tistory.com/category/%EA%B2%BD%EB%85%80?page=1'
        # url = 'https://chizb.tistory.com/category/%EB%B2%88%EC%97%AD?page=1'

        print("입력: ")
        cli_input = input()
        obj = Downloader()

        try:
            if cli_input == 'q':
                os._exit(0)
            elif cli_input == '1':
                print("다운받을 주소를 입력하세요.")
                url = input()
                obj.one_main(url)
            else:
                print("다운받을 주소를 입력하세요.")
                url = input()
                obj.main(url)
        except Exception as e:
            print('[Error]: ' + str(e))
            print('다운로드 받을 주소는 카테고리 주소를 입력하세요.')
            print('예) https://xxx.tistory.com/category/xxx')

        print("*"*70)
        print("작업이 종료 되었습니다.")
        print("다운로드 받을 주소를 입력 하거나 종료하려면 q 를 입력하세요.")
        print("*"*70)

        print("Enter: ")
        command = input()
        if command == 'q' or 'Q':
            break
