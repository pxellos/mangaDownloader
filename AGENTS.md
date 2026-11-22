# AGENTS.md

이 저장소에서 작업하는 코딩 에이전트(Codex, Claude Code, Antigravity 등)가 공통으로 읽는 지침이다. 도구별 설정 파일(`CLAUDE.md` 등)은 이 파일을 불러오기만 하고, 내용은 여기 한 곳에서 관리한다.

## 언어

- 답변, 문서, 코드 주석, 커밋 메시지는 한국어로 쓴다.

## 프로젝트 개요

웹 게시판과 블로그에 올라온 만화 이미지를 화별 폴더로 내려받는 개인용 Python 스크립트 모음이다. Windows에서 실행하는 것을 전제로 한다(경로 구분자 `\\`, `D:\` 드라이브 경로).

필요한 패키지: `selenium`, `beautifulsoup4`, `requests`, `PyQt5`(GUI만). 의존성 파일과 테스트는 없다.

## 파일 구성

| 파일 | 대상 | 실행 방식 |
|---|---|---|
| `main_gui.pyw` | 통합 GUI(PyQt5) | URL에 따라 `manatoki_cli`, `tistory_cli`, `dc_cli`, `egloos_cli`의 `Downloader`를 호출 |
| `dc_img.py` | 디시인사이드 글 | 단독 스크립트. 파일 위쪽의 `path`, `link_list`를 직접 고쳐서 실행 |
| `dc_cli.py`, `dc_basic.py` | 디시인사이드 | 예전 방식(크롬 다운로드 기능 사용) |
| `manatoki_cli.py`, `manatoki_cli_crome.py` | 마나토끼 | CLI 입력 |
| `jmana_cli.py` | 제이마나 | CLI 입력 |
| `tistory_cli.py`, `tistory_basic.py` | 티스토리 | CLI / 단독 스크립트 |
| `egloos_cli.py` | 이글루스 | CLI |
| `temp.py` | 받은 폴더의 파일명 정리용 임시 스크립트 | 단독 |
| `dc이미지다운로더. md` | `dc_img.py` 설계 메모 | 문서(파일명에 공백이 있어 확장자가 `.md`로 인식되지 않음) |

저장 경로는 스크립트마다 상수로 박혀 있다(`SELLECT_PATH = 'D:\\Manatoki'`, `dc_img.py`의 `path` 등). 없는 폴더를 가리킬 수 있으니 실행 전에 확인한다.

## dc_img.py 동작

1. `link_list`의 글을 셀레니움(헤드리스 크롬)으로 연다.
2. 페이지 제목(`- 갤러리명` 제거, 파일명 금지 문자는 `？`로 치환)으로 `path` 아래에 폴더를 만든다.
3. 본문 `.write_div` 안의 `img`만 대상으로 한다. 지연 로딩 이미지는 `src`가 로딩 gif이므로 `data-original`을 먼저 읽는다.
4. 이미지는 `urllib`로 직접 받는다. **`Referer`(글 주소)가 없으면 403**이 나므로 반드시 붙이고, 브라우저 쿠키도 함께 보낸다.
5. 본문 순서대로 `001.jpg`부터 저장하고, `MIN_SIZE`(50KB) 이하는 저장하지 않는다.
6. `FOLLOW_SERIES = True`이면 본문의 `[시리즈]` 박스(`.dc_series a`) 링크를 목록에 추가해 같이 받는다. 같은 글은 `(id, no)`로 구분한다.
7. 제목 폴더에 파일이 이미 있으면 그 글은 건너뛴다.

## 크롬 드라이버

- `webdriver.Chrome(options=options)`처럼 **드라이버 경로를 넘기지 않는다.** Selenium 4.6+의 Selenium Manager가 설치된 크롬 버전에 맞는 드라이버를 자동으로 받는다.
- 저장소의 `chromedriver.exe`는 예전 버전(90)이라 최신 크롬과 맞지 않는다. `dc_img.py`는 이미 쓰지 않는다.
- `dc_img.py`를 뺀 나머지 스크립트는 아직 `webdriver.Chrome(경로, ...)` 또는 `executable_path=`를 쓰고 있어 Selenium 4.10 이상에서 실패한다. 손볼 때 같은 방식으로 바꾼다.

## 작업 규칙

- 테스트가 없으므로 실제 URL로 실행해 확인한다. 이때 저장 경로는 임시 폴더로 바꾼 사본으로 돌리고, 받은 파일은 지운다. 많은 글을 한 번에 받는 시험은 피하고 몇 개로 제한한다.
- 사이트에 부담을 주지 않도록 글 사이에 지연(`time.sleep`)을 둔다.
- 주석 처리된 코드는 이전 방식을 남겨 둔 것이므로 요청이 없으면 지우지 않는다.
- 기본 브랜치는 `master`이고, 지금까지 `master`에 바로 커밋해 왔다.
