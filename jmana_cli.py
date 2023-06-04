import os
import re
import time
import importlib
from urllib import request, parse
import urllib
from bs4 import BeautifulSoup
from concurrent import futures
from selenium import webdriver

# 지정 경로
global SELLECT_PATH
SELLECT_PATH = 'D:\\Manatoki'


class CreateRequests:

    def get(self, url):
        requests = importlib.import_module('requests')
        headers = {'User-Agent': 'Mozilla/6.0'}

        return requests.get(url, headers=headers)


class Downloader():

    # 이미지 저장 메소드
    def download(self, url, file_name, path):

        # get_obj = CreateRequests()

        locate = path + '\\' + file_name

        print(locate)
        print(url)

        # 아스키 코드 변환 url 인코딩
        url = parse.urlparse(url) 
        path = {'path': url.path}
        result = parse.urlencode(path, doseq=False)
        res1 = result.replace('path=', '')
        res2 = res1.replace('+', '%20')
        res = res2.replace('%2F', '/').strip()
        url_re = url.scheme + '://' + url.netloc + res
        print(url_re)

        try:
            if not os.path.exists(locate):
                urllib.request.urlretrieve(url_re, locate)
        except Exception as e:
            print(e)

    # 각 화 이미지 추출 및 저장 메소드
    def image_parse(self, soup, locate, img_list):

        # # 폴더 생성 및 제목 추출
        # path = SELLECT_PATH + '\\' + path
        # locate, title = self.folder_name(soup, path)

        for num, img in enumerate(img_list, 1):

            print(img)

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

            print(file_name)
            print(locate)

            self.download(img, file_name, locate)
            print(file_name + ' is downloaded')

    # 각 화 폴더 이름 생성 메소드
    def folder_name(self, soup, path):

        title = soup.title.get_text()
        # title_split = title.rsplit('화', maxsplit=1)
        # title_split = title.rsplit('(', maxsplit=1)

        # 폴더 생성이 실패하는 특수문자 제거
        title_re = re.sub(
            '[\/:*?"<>|]', '？', title)
        title_strip = title_re.strip()

        locate = path + '\\' + title_strip

        return locate, title

    # 제이마나 이미지 주소 파싱 메소드
    def jmana_parse(self, soup):
        img_list = []

        for link in soup.find_all('img', {"class": 'comicdetail'}):
            img = link.get('data-src')
            if not img:
                img = link.get('src')
            img_list.append(img)

        return img_list

    # 한 화 저장 메소드
    def zero_main(self, url):

        path = SELLECT_PATH

        # 이미지 소스 추출
        soup = self._parse(url)

        # 이미지 링크 추출
        img_list = self.jmana_parse(soup)

        # 전체목록 주소 추출
        # total_url = self.total_list_parse(soup)
        # total_soup = self._parse(total_url)

        # # 작가명 폴더 생성
        # path, flag = self.create_folder(total_soup)

        # 한 화 폴더 경로 작성
        locate, title = self.folder_name(soup, path)
        # path_locate = SELLECT_PATH + '\\' + locate

        # 한 화 폴더가 존재하면 스킵
        if os.path.exists(locate):
            print(title + ' is exist')
        else:
            os.mkdir(locate)
            print(title)
            # 다운로드 실행
            try:
                self.image_parse(soup, locate, img_list)
            except Exception:
                print('에러가 발생하였습니다. 로그를 확인하세요.')

    # soup 웹 파싱 메소드
    def _parse(self, url):
        req_url = request.Request(url, headers={'User-Agent': 'Mozilla/6.0'})
        # req_url = request.Request(url, headers={'User-Agent': 'Edg/87.0.664.47'})
        response = request.urlopen(req_url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        return soup


# Console로 실행했을 때 사용하는 메소드
def main():

    while True:
        try:
            print("*"*70)
            print("실행할 작업을 선택하고 엔터를 누르시오.")
            print("*"*70)
            print("0. 한 화 다운로드")
            print("1. 전편보기 주소를 입력해서 만화별 다운로드(각 화 폴더 존재시 스킵)")
            # print("2. 제이마나 전체 만화를 전부 다운로드")
            # print("3. 한 페이지 다운로드")
            # print("4. 전체 다운로드한 만화들을 업데이트")
            # print("8. 저장폴더 변경")
            print("9. 종료")
            print("*"*70)
            print("입력: ")
            cli_input = input()

            obj = Downloader()

            if cli_input == '0':
                try:
                    print("다운받을 제이마나 주소를 입력하세요.")
                    cli_input = input()
                    obj.zero_main(cli_input)
                except Exception as e:
                    print('[Error]: ' + str(e))
                    print('다운로드 받을 주소는 한 화 주소를 입력하세요.')
                    print('예) https://jmana1.net/bookdetail?bookdetailid=259220&viewstyle=list')
            if cli_input == '1':
                try:
                    print("다운받을 제이마나 전편목록 주소를 입력하세요.")
                    cli_input = input()
                    obj.one_main(cli_input)
                except Exception as e:
                    print('[Error]: ' + str(e))
                    print('다운로드 받을 주소는 전편목록 주소를 입력하세요.')
                    print('예) https://jmana1.net/comic_list_title?bookname=오렌지+로드')
            # elif cli_input == '2':
            #     try:
            #         print("전체 만화의 다운로드를 시작합니다.")
            #         print("다운받을 마나토끼 최종 페이지 주소를 입력하세요.")
            #         cli_input = input()
            #         obj.two_main(cli_input)
            #         print("전체 만화의 다운로드가 완료되었습니다.")
            #     except Exception as e:
            #         print('[Error]: ' + str(e))
            #         print('에러가 발생하였습니다. 관리자에게 문의하세요.')
            # elif cli_input == '3':
            #     try:
            #         print("한 페이지 만화 다운로드를 시작합니다.")
            #         print("다운받을 페이지 주소를 입력하세요.")
            #         TOTAL_DOWNLOAD = False
            #         ONE_DOWNLOAD = True
            #         cli_input = input()
            #         obj.three_main(cli_input)
            #         print("한 페이지 만화 다운로드가 완료되었습니다.")
            #     except Exception as e:
            #         print('[Error]: ' + str(e))
            #         print('에러가 발생하였습니다. 관리자에게 문의하세요.')
            # elif cli_input == '4':
            #     try:
            #         print("전체 만화 업데이트를 시작합니다.")
            #         TOTAL_DOWNLOAD = False
            #         obj.four_main()
            #         print("전체 만화 업데이트가 완료되었습니다.")
            #     except Exception as e:
            #         print('[Error]: ' + str(e))
            #         print('에러가 발생하였습니다. 관리자에게 문의하세요.')
            # elif cli_input == '8':
            #     print('현재 설정 폴더: ' + SELLECT_PATH)
            #     print('설정할 폴더 경로를 입력하세요. 변경하지 않을 경우 그냥 엔터룰 누르세요.')
            #     cli_input = input()
            #     if cli_input:
            #         SELLECT_PATH = cli_input
            #     else:
            #         continue
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