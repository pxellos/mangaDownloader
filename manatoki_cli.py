import os
import re
import time
import importlib
import ssl
from urllib import request
from bs4 import BeautifulSoup
from concurrent import futures
from selenium import webdriver

# 최대 프로세스 개수
MAX_PROCESS = 5
# 최대 쓰레드 개수, 한화에 파일 개수가 많은 경우 다른 스레드에서 타임아웃 발생함에 따라 줄임, 포비든 뜸
MAX_THREAD = 5
# 현재 폴더 경로
CURRENT_PATH = os.getcwd()
# 지정 경로
global SELLECT_PATH
SELLECT_PATH = 'D:\\Manatoki'
# SELLECT_PATH = CURRENT_PATH
# 전체 다운로드 플래그
TOTAL_DOWNLOAD = True
# 전체화 검사 다운로드 플래그
ONE_DOWNLOAD = True


class CreateRequests:

    def get(self, url):
        requests = importlib.import_module('requests')
        # headers = {'Content-Type': 'application/json; charset=utf-8'}
        headers = {'User-Agent': 'Mozilla/6.0'}
        # cookies = {'session_id': 'sorryidontcare'}

        return requests.get(url, headers=headers)


class Downloader():

    # 이미지 저장 메소드
    def download(self, url, file_name, path):

        get_obj = CreateRequests()

        locate = path + '\\' + file_name
        if not os.path.exists(locate):
            with open(locate, mode="wb") as file:   # open in binary mode
                response = get_obj.get(url)                 # get request
                file.write(response.content)        # write to file

    # 크롬드라이버로 파싱
    def crome_parse(self, url):

        # 크롬드라이버 로드
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        # options.add_argument('window-size=800x600')
        options.add_argument("disable-gpu")

        # UserAgent값 변경(비정상 접속차단 회피)
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

        path = CURRENT_PATH
        driver = webdriver.Chrome(path + '\\chromedriver.exe', options=options)

        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        driver.quit()

        return soup

    # 마나토끼 html 파싱 메소드
    def manatoki_parse(self, url):
        img_list = []
        flag = False
        soup_main = None

        while True:
            try:
                get_obj = CreateRequests()
                res = get_obj.get(url).text
                soup_main = BeautifulSoup(res, 'html.parser')
                try:
                    text = res.split('html_data=', 1)[1].rsplit(
                        'html_data+=', 1)[0]
                    text = text.replace("\'", "")
                    text = text.replace("html_data+=", "")
                    text = text.replace(".", "")
                    text = text.replace(";", "")
                    text = text.replace(";", "")
                    text = text.replace('\n', "")
                    text = text.strip()

                    i = hex(int(text, 16))
                    hex_string = i[2:]
                    bytes_object = bytes.fromhex(hex_string)
                    html = bytes_object.decode("utf-8")
                    soup = BeautifulSoup(html, 'html.parser')
                except Exception:
                    # 이미지 링크가 없으면 전편보기 주소로 판단하고 리턴함
                    return soup_main, img_list

                link = soup.find("p")
                class_num = link.get('class')
                # print(class_num)
                parse_name = 'data-' + str(class_num[0])
                for link in soup.find_all("img"):
                    img = link.get(parse_name)
                    src = link.get("src")
                    if (img) and (src == "/img/loading-image.gif"):
                        img_list.append(img)
            except Exception as e:
                print(e)
                time.sleep(5)
                print('Try again...')
                if not flag:
                    continue
                else:
                    flag = True

            return soup_main, img_list

    # 각 화 이미지 추출 및 저장 메소드
    def image_parse(self, soup, path, img_list):

        # 폴더 생성 및 제목 추출
        path = SELLECT_PATH + '\\' + path
        locate, title = self.folder_name(soup, path)

        for num, img in enumerate(img_list, 1):
            extension = img.rsplit('.')
            length = len(extension)
            img_extension = extension[length - 1]
            if img_extension == 'gif':
                continue
            # if img_extension == 'php':
            else:
                img_extension = 'jpg'
            number = '%03d' % num
            file_name = number + '.' + img_extension
            self.download(img, file_name, locate)
            print(title + ' ' + file_name + ' is downloaded')

    # 각 화 폴더 이름 생성 메소드
    def folder_name(self, soup, path):

        link = soup.find('div', {"class": 'toon-title'})
        title = link.get_text()
        # title = soup.title.get_text()
        # title_split = title.rsplit('화', maxsplit=1)
        title_split = title.rsplit('(', maxsplit=1)

        # 폴더 생성이 실패하는 특수문자 제거
        title_re = re.sub(
            '[\/:*?"<>|]', '？', title_split[0])
        title_strip = title_re.strip()

        locate = path + '\\' + title_strip

        return locate, title

    # 각 화 링크 주소 추출 메소드
    def link_parse(self, soup):

        page_list = []

        for link in soup.find_all('a', {"class": 'item-subject'}):
            href = link.get('href')
            page_list.append(href)

        return page_list

    # 전체목록 주소 추출 메소드
    def total_list_parse(self, soup):
        href = ''

        for link in soup.find_all('a', {"style": 'margin: 0 5px;'}):
            href = link.get('href')

        return href

    # 멀티 쓰레딩, 각 화 다운로드 수행
    def _multi_threading(self, page_tuple):

        url = page_tuple[1]
        path = page_tuple[0]

        try:
            # soup = _parse(url)
            # jQuery로 이미지 처리함에 따라 파싱 방식변경
            soup, img_list = self.manatoki_parse(url)
            self.image_parse(soup, path, img_list)
        except Exception as e:
            print(e)

    # 멀티 프로세스, 페이지별로 다운로드 실행
    def _multi_process(self, page):

        # 만화별 다운로드
        try:
            print("*"*70)
            print(page)
            print("*"*70)
            soup = self._parse(page)
            link_set = self.entity_page(soup)
            # link_set = self.one_page(soup)
            if len(link_set) > 0:
                for link in link_set:
                    self.one_main(link)
        except Exception as e:
            print(e)

    # soup 웹 파싱 메소드
    def _parse(self, url):
        req_url = request.Request(url, headers={'User-Agent': 'Mozilla/6.0'})
        # req_url = request.Request(url, headers={'User-Agent': 'Edg/87.0.664.47'})
        # 개정된 PEP 467에 따라 모든 https 통신은 필요한 인증서와 호스트명을 기본으로 체크
        context = ssl._create_unverified_context()
        response = request.urlopen(req_url,  context=context)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        return soup

    # 폴더 생성 메소드
    def create_folder(self, soup):
        path = SELLECT_PATH
        title = soup.title.get_text()
        title_split = title.split('>')
        writer = ''
        flag = False

        for link in soup.find_all('div', {"class": 'view-content'}):
            temp = link.get_text()
            temp_split = temp.splitlines()

            indices = [i for i, s in enumerate(temp_split) if '작가' in s]
            if indices:
                index = indices.pop()
                try:
                    writer = temp_split[index + 1]
                    writer = writer.strip()
                except Exception:
                    pass

        if not writer:
            writer = 'N／A'

        # 폴더 생성이 실패하는 특수문자 제거
        folder_name = '[' + writer + '] ' + title_split[0]
        folder_re = re.sub(
            '[\/:*?"<>|]', '？', folder_name)
        folder_strip = folder_re.strip()
        folder = path + '\\' + folder_strip

        if not os.path.exists(folder):
            os.mkdir(folder)
        else:
            flag = True

        if not TOTAL_DOWNLOAD:
            flag = False

        return folder_strip, flag

    # 전체 페이지 번호 추출 및 리스트 작성
    def total_page(self, input_url):
        url = 'https://manatoki.net'

        # 헤더 정보가 없어서 접속 안될때 사용방법
        # req_url = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        # response = request.urlopen(req_url)
        # html = response.read()

        get_obj = CreateRequests()
        res = get_obj.get(url)
        # html = res.text
        # soup = BeautifulSoup(html, 'html.parser')

        templete = res.url + '/comic/p'

        page_list = []
        # max_num = 0

        # 최종 페이지 번호 추출
        # for link in soup.find_all('a'):
        #     # print(link.get)
        #     temp = link.get('href')
        #     if temp:
        #         temp_rsplit = temp.rsplit('/')
        #         length = len(temp_rsplit)

        #         # 정규식
        #         if re.match('p([0-9])', temp_rsplit[length-1]):
        #             temp_num = temp_rsplit[length-1][1:]
        #             if int(temp_num) > max_num:
        #                 max_num = int(temp_num)
        page_num = input_url.rsplit('/', 1)[1]
        page_num = page_num.replace('p', '').strip()
        max_num = int(page_num)
        print(max_num)

        # 페이지 번호별 주소 작성
        for i in range(2, max_num):
            page = templete + str(i)
            page_list.append(page)

        # 전체 리스트 중 1페이지 다운로드
        page = res.url + 'comic/p1'
        try:
            soup = self._parse(page)
            link_set = self.one_page(soup)
            if len(link_set) > 0:
                for link in link_set:
                    self.select_main(link)
        except Exception as e:
            print(e)

        return page_list

    # 페이지에서 만화별 링크 추출
    def entity_page(self, soup):
        link_set = set()

        for link in soup.find_all('a'):
            temp = link.get('href')
            if temp:
                if 'page' in temp:
                    if 'http' in temp:
                        temp_rsplit = temp.rsplit('?')
                        link_set.add(temp_rsplit[0])

        return link_set

    # 업데이트용: 페이지에서 만화별 링크 추출
    def update_page(self, soup):
        link_set = set()

        # 한 화 링크만 추출
        # for link in soup.find_all('a', {"class": 'ellipsis'}):
        # 전편 보기 링크만 추출
        for link in soup.find_all('a', {"class": 'btn btn-xs btn-primary'}):
            temp = link.get('href')
            if temp:
                print(temp)
                if 'comic/' in temp:
                    if 'http' in temp:
                        temp_rsplit = temp.rsplit('?')
                        link_set.add(temp_rsplit[0])

        return link_set

    # 한 페이지에서 만화별 링크 추출
    def one_page(self, soup):
        link_set = set()

        # 전체 링크 추출
        for link in soup.find_all('a'):
            temp = link.get('href')
            if temp:
                print(temp)
                if 'comic/' in temp:
                    if 'http' in temp:
                        temp_rsplit = temp.rsplit('/')
                        length = len(temp_rsplit)
                        if re.match('p([0-9])', temp_rsplit[length-1]):
                            continue
                        else:
                            link_set.add(temp)

        print(link_set)
        return link_set

    # 현재 존재하는 폴더를 dict 형태로 반환
    def search_folder(self):
        path = SELLECT_PATH

        # 예) {'[작가] 제목':['제목 x화':'']}
        folder_dict = {}
        # 현재 경로의 폴더 및 파일 리스트 취득
        folder_list = os.listdir(path)
        for folder in folder_list:
            folder_path = path + '\\' + folder
            # 해당 경로가 폴더인지 확인
            if os.path.isdir(folder_path):
                sub_folder_list = os.listdir(folder_path)
                for sub_folder in sub_folder_list:
                    sub_folder_path = folder_path + '\\' + sub_folder
                    if os.path.isdir(sub_folder_path):
                        # 각화별 폴더 안에 파일이 있는 경우만 제외 목록에 등록
                        if os.listdir(sub_folder_path):
                            if folder_dict.get(folder):
                                folder_dict[folder].append({sub_folder: ''})
                            else:
                                folder_dict[folder] = [{sub_folder: ''}]

        return folder_dict
    # data = {}
    # # 전체 만화 목록 및 링크를 dict로 변수에 저장
    # def total_parse_json():
    #     path = os.getcwd()
    #     file_path = path + "\\file.json"
    #     thread_lock = threading.Lock()

    #     # 예) {'[작가] 제목':['제목 x화':'https://manatoki102.net/comic/5374287']}
    #     global data

    #     # # 현재 폴더에 저장되어 있는 내용 확인
    #     # if os.path.exists(file_path):
    #     #     with open(file_path, "r") as json_file:
    #     #         data = json.load(json_file)
    #     # else:

    #     # 현재 폴더를 검색해서 제외할 목록 작성

    #     start = time.time()  # 시작 시간 저장

    #     # 사이트로 부터 전체 정보 취득
    #     page_list = total_page()

    #     def _total_parse(page):
    #     # for page in page_list:
    #         global data
    #         # 만화별 정보취득
    #         soup = _parse(page)
    #         link_set = entity_page(soup)
    #         if len(link_set) > 0:
    #             for link in link_set:
    #                 # 전편보기 파싱
    #                 try:
    #                     _soup = _parse(link)
    #                 except Exception as e:
    #                     print(e)
    #                     continue
    #                 # 작가명 폴더 생성
    #                 folder = create_folder(_soup)
    #                 # 한화별 주소 파싱
    #                 _page_list = link_parse(_soup)
    #                 # 각화별 폴더이름 생성
    #                 for page in _page_list:
    #                     try:
    #                         __soup = _parse(page)
    #                     except Exception as e:
    #                         print(e)
    #                         continue
    #                     temp_link = __soup.find(
    #                         'div', {"class": 'toon-title'})
    #                     if temp_link:
    #                         title = temp_link.get_text()
    #                         if title:
    #                             title_split = title.split('(')
    #                             # locate = path + '\\' + title_split[0]
    #                             # 데이터에 저장
    #                             thread_lock.acquire()
    #                             print(title_split[0])
    #                             if folder_dict.get(folder):
    #                                 data[folder].append(
    #                                     {title_split[0]: page})
    #                             else:
    #                                 data[folder] = [{title_split[0]: page}]
    #                             thread_lock.release()

    #     workers = len(page_list)

    #     with futures.ThreadPoolExecutor(workers) as executor:
    #         futuer = executor.map(_total_parse, page_list)
    #         print(futuer)

    #     # 취득한 정보에서 기존 정보 데이터를 제외

    #     # print(data)
    #     print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간

    #     with open(file_path, 'w') as outfile:
    #         json.dump(data, outfile)

    #     file_path = path + "\\time.txt"
    #     with open(file_path, 'w') as outfile:
    #         txt = "time :", time.time() - start
    #         outfile.write(str(txt))

    #     return data

    # 한 화 저장 메소드
    def zero_main(self, soup, img_list):

        # url = 'https://manatoki76.net/comic/5495612'

        # 전체목록 주소 추출
        # total_soup = self._parse(url)
        total_url = self.total_list_parse(soup)
        total_soup = self._parse(total_url)

        # 작가명 폴더 생성
        path, flag = self.create_folder(total_soup)

        # 한 화 폴더 경로 작성
        locate, title = self.folder_name(soup, path)
        path_locate = SELLECT_PATH + '\\' + locate

        # 한 화 폴더가 존재하면 스킵
        if os.path.exists(path_locate):
            print(title + ' is exist')
        else:
            os.mkdir(path_locate)
            print(title)
            # 다운로드 실행
            try:
                self.image_parse(soup, path, img_list)
            except Exception:
                print('에러가 발생하였습니다. 로그를 확인하세요.')

    # 1개 만화 전체 저장 메소드
    def one_main(self, url):

        # url = 'https://manatoki102.net/comic/5374287'

        if not url:
            print('다운받을 주소를 입력하세요.')
            return

        # 전편보기 파싱
        try:
            soup = self._parse(url)
        except Exception as e:
            print(e)
            return

        # 작가명 폴더명 작성
        path, flag = self.create_folder(soup)

        # 전체 다운로드시 한번이라도 다운로드 받았으면 패스
        if flag:
            print(path + ' is exist')
            return

        # 한화별 주소 파싱
        page_list = self.link_parse(soup)
        page_tuple_list = []
        for page in page_list:
            # 존재하는 폴더 스킵
            soup = self._parse(page)
            locate, title = self.folder_name(soup, path)
            path_locate = SELLECT_PATH + '\\' + locate

            # 각 화 폴더가 존재하면 스킵
            if os.path.exists(path_locate):
                print(title + ' is exist')
                # 업데이트 수행중 이하에 중복폴더가 있는 경우 이하는 패스
                if ONE_DOWNLOAD is True:
                    break
            else:
                os.mkdir(path_locate)
                print(title)
                temp = (path, page)
                page_tuple_list.append(temp)

        # 실행될 최대 쓰레드 개수 설정
        page_num = len(page_tuple_list)
        if page_num > 0:
            num = page_num if page_num > 0 else 1
            workers = min(MAX_THREAD, num)
            with futures.ThreadPoolExecutor(workers) as executor:
                executor.map(self._multi_threading, page_tuple_list)

    # 마나토끼의 업로드 된 전체만화를 백업
    def two_main(self, url):

        # 전체 리스트 파싱
        page_list = self.total_page(url)
        # process_list = []

        # 페이지별로 변수 할당해 프로세스 생성(페이지 수만큼 프로세스 생성)
        page_num = len(page_list)
        num = page_num if page_num > 0 else 1

        # for i in range(0, num):
        #     temp = vars()['p_{}'.format(i)] = Process(
        #         target=_multi_process, args=(i, page_list[i]))
        #     process_list.append(temp)

        # for process in process_list:
        #     process.start()

        # for process in process_list:
        #     process.join()

        # 실행될 최대 프로세스 개수 설정
        workers = min(MAX_PROCESS, num)
        with futures.ProcessPoolExecutor(workers) as executor:
            futers = executor.map(self._multi_process, page_list)
            print(futers)

    # 한 페이지만 다운로드
    def three_main(self, url):

        link_set = None

        # 페이지 다운로드
        try:
            soup = self._parse(url)
            link_set = self.one_page(soup)

            if len(link_set) > 0:
                for link in link_set:
                    self.select_main(link)
        except Exception as e:
            print(e)
            return

        # 멀티 프로세스 사용시 글로벌 변수 값변경 처리가 안됨
        # with futures.ProcessPoolExecutor(MAX_PROCESS) as executor:
        #     futers = executor.map(self.select_main, link_set)
        #     print(futers)

    # 전체만화 업데이트
    def four_main(self):

        # 전체 리스트 중 1페이지 파싱
        url = 'https://manatoki.net'
        get_obj = CreateRequests()

        res = get_obj.get(url)
        # page = res.url + 'comic/p1'
        print(res.status_code)
        # 기본 웹서버 다운에러
        if res.status_code == 521 or 523:
            print('마나토끼 주소 번호를 입력하시오.')
            cli_input = input()
            # page = 'https://manatoki'+ cli_input + '.net/bbs/page.php?hid=update&page=1'
            page = 'https://manatoki' + cli_input + '.net/page/update'
        else:
            page = res.url + 'bbs/page.php?hid=update&page=1'

        link_set = None

        # 페이지 다운로드
        try:
            soup = self._parse(page)
            link_set = self.update_page(soup)
            if len(link_set) > 0:
                for link in link_set:
                    self.select_main(link)
        except Exception as e:
            print(e)

        # 멀티 프로세스 사용시 글로벌 변수 값변경 처리가 안됨
        # with futures.ProcessPoolExecutor(MAX_PROCESS) as executor:
        #     futers = executor.map(self.select_main, link_set)
        #     print(futers)

    # 입력된 주소로 한화 인지 1개 만화인지 판별해서 수행
    def select_main(self, url):
        soup, img_list = self.manatoki_parse(url)
        print(url)
        if img_list:
            if TOTAL_DOWNLOAD is True:
                print('입력한 주소는 한화 주소입니다. 한화다운을 시작합니다.')
                self.zero_main(soup, img_list)
        else:
            print('입력한 주소는 전편보기 주소입니다. 전편다운을 시작합니다.')
            self.one_main(url)


# Console로 실행했을 때 사용하는 메소드
def main():
    global SELLECT_PATH
    global TOTAL_DOWNLOAD
    global ONE_DOWNLOAD

    while True:
        try:
            print("*"*70)
            print("실행할 작업을 선택하고 엔터를 누르시오.")
            print("*"*70)
            print("0. 한 화 다운로드")
            print("1. 전편보기 주소를 입력해서 만화별 다운로드(각 화 폴더 존재시 스킵)")
            print("2. 마나토끼 전체 만화를 전부 다운로드")
            print("3. 한 페이지 다운로드")
            print("4. 전체 다운로드한 만화들을 업데이트")
            print("8. 저장폴더 변경")
            print("9. 종료")
            print("*"*70)
            print("입력: ")
            cli_input = input()

            obj = Downloader()

            if cli_input == '0':
                try:
                    print("다운받을 마나토끼 주소를 입력하세요.")
                    cli_input = input()
                    obj.select_main(cli_input)
                except Exception as e:
                    print('[Error]: ' + str(e))
                    print('다운로드 받을 주소는 한 화 주소를 입력하세요.')
                    print('예) https://manatoki102.net/comic/*****')
            if cli_input == '1':
                try:
                    print("다운받을 마나토끼 전편보기 주소를 입력하세요.")
                    TOTAL_DOWNLOAD = False
                    ONE_DOWNLOAD = False
                    cli_input = input()
                    obj.one_main(cli_input)
                except Exception as e:
                    print('[Error]: ' + str(e))
                    print('다운로드 받을 주소는 전편보기 주소를 입력하세요.')
                    print('예) https://manatoki102.net/comic/*****')
            elif cli_input == '2':
                try:
                    print("전체 만화의 다운로드를 시작합니다.")
                    print("다운받을 마나토끼 최종 페이지 주소를 입력하세요.")
                    cli_input = input()
                    obj.two_main(cli_input)
                    print("전체 만화의 다운로드가 완료되었습니다.")
                except Exception as e:
                    print('[Error]: ' + str(e))
                    print('에러가 발생하였습니다. 관리자에게 문의하세요.')
            elif cli_input == '3':
                try:
                    print("한 페이지 만화 다운로드를 시작합니다.")
                    print("다운받을 페이지 주소를 입력하세요.")
                    TOTAL_DOWNLOAD = False
                    ONE_DOWNLOAD = True
                    cli_input = input()
                    obj.three_main(cli_input)
                    print("한 페이지 만화 다운로드가 완료되었습니다.")
                except Exception as e:
                    print('[Error]: ' + str(e))
                    print('에러가 발생하였습니다. 관리자에게 문의하세요.')
            elif cli_input == '4':
                try:
                    print("전체 만화 업데이트를 시작합니다.")
                    TOTAL_DOWNLOAD = False
                    obj.four_main()
                    print("전체 만화 업데이트가 완료되었습니다.")
                except Exception as e:
                    print('[Error]: ' + str(e))
                    print('에러가 발생하였습니다. 관리자에게 문의하세요.')
            elif cli_input == '8':
                print('현재 설정 폴더: ' + SELLECT_PATH)
                print('설정할 폴더 경로를 입력하세요. 변경하지 않을 경우 그냥 엔터룰 누르세요.')
                cli_input = input()
                if cli_input:
                    SELLECT_PATH = cli_input
                else:
                    continue
            elif cli_input == '9':
                break
            else:
                print('입력이 잘못되었습니다. 다시 시도하세요.')

            print("*"*70)
            print("작업이 종료 되었습니다.")
            print("*"*70)

        # Ctrl+c 입력해서 일시중지
        except KeyboardInterrupt:
            print('\nPausing...  (Hit ENTER to continue, type quit to exit.)')
            try:
                response = input()
                if response == 'quit':
                    break
                print('Resuming...')
            except KeyboardInterrupt:
                print('Resuming...')
                continue


if __name__ == "__main__":
    main()
