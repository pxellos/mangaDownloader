from bs4 import BeautifulSoup
from urllib import request
import os
import time
from requests import get


SELLECT_PATH = 'D:\\Hitomi_jmana\\이세계 헌헌'


def _parse(url):
    req_url = request.Request(url, headers={'User-Agent': 'Mozilla/6.0'})
    response = request.urlopen(req_url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    return soup


# 이미지 저장 메소드
def download(url, file_name, path):

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


# 각 화 이미지 추출 및 저장 메소드
def image_parse(url, soup, path):

    ret = False
    # 폴더명 만들기
    title = url.rsplit('/', 1)[1]
    title = title.zfill(3)

    print(title)

    img_list = []
    filename_dict = {}

    for link in soup.find_all("img"):
        img_list.append(link.get('src'))
        filename_dict[link.get('src')] = link.get('filename')

    # 패스워드 있어서 이미지 없을시 예외발생해서 크롬다운로드 실행
    if len(img_list) < 2:
        raise Exception

    locate = path + '\\' + title

    if not os.path.exists(locate):
        os.mkdir(locate)
        print(title)
    else:
        print(title + ' is exist')
        return

    for num, img in enumerate(img_list, 1):
        # print('img: ' + img)
        extension = img.rsplit('.')
        length = len(extension)
        img_extension = extension[length - 1].split('?')
        # print(img_extension)
        img_name = ''

        # 링크에 확장자가 지정이 되있는 경우
        if len(img_extension[0]) == 3 or 4:
            if img_extension[0] == 'gif':
                pass
            else:
                number = '%03d' % num
                img_name = str(number) + '.' + img_extension[0]
                ret = download(img, img_name, locate)
        else:
            # 링크에 확장자가 없는 경우 파일이름 엘리먼츠로 작성
            img_name = filename_dict.get(img)
            # print('img_name: ' + img_name)
            if not img_name:
                ret = download(img, img_name, locate)

        if ret:
            print(title + ' ' + img_name + ' is downloaded')


link_list = ['https://mobsi.tistory.com/62']

base_url = link_list[0].rsplit('/', 1)[0]  # 숫자 부분을 제외한 URL 베이스

new_link_list = [f'{base_url}/{num}' for num in range(84, 113)]

print(new_link_list)

err_list = []

for i in new_link_list:
    # print(i)
    soup = _parse(i)
    # print(soup)

    # 한화 다운
    image_parse(i, soup, SELLECT_PATH)

    time.sleep(5)

print(err_list)
