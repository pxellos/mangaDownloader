import sys
import logging
import manatoki_cli as toki
import tistory_cli as tistory
import dc_cli as dc
import egloos_cli as eg
import subprocess
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
     QMainWindow, QAction, qApp, QLabel, \
     QFormLayout, QLineEdit, \
     QGridLayout, QTextEdit, QCheckBox, \
     QPlainTextEdit, QProgressBar


class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    def write(self, m):
        pass


class Stream(QtCore.QObject):
    newText = QtCore.pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))


class MyApp(QMainWindow, QPlainTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)

        # 메인창 크기 위치 설정
        self.setWindowTitle('Manatoki Download Application')
        self.setWindowIcon(QtGui.QIcon('web.png'))
        # self.move(400, 100)
        # self.resize(800, 600)
        self.setGeometry(0, 100, 800, 600)
        self.show()

        self.initUI()

        sys.stdout = Stream(newText=self.onUpdateText)

    def onUpdateText(self, text):
        cursor = self.process.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.process.setTextCursor(cursor)
        self.process.ensureCursorVisible()

    def __del__(self):
        sys.stdout = sys.__stdout__

    def initUI(self):

        # 메뉴바에 액션 설정
        log_action = QAction('Log', self)
        console_action = QAction('Console', self)
        exitAction = QAction(QtGui.QIcon('exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        # 상태바에 팁표시
        exitAction.setStatusTip('Exit application')
        # 액션에 기능 설정
        exitAction.triggered.connect(qApp.quit)
        log_action.triggered.connect(self.show_log)
        console_action.triggered.connect(self.console)

        # 메뉴바 생성
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(exitAction)
        filemenu.addAction(log_action)
        filemenu.addAction(console_action)

        # 하단 상태표시
        self.statusBar().showMessage('Ready')

        # 작업 결과 출력
        self.process = QTextEdit()
        self.process.moveCursor(QtGui.QTextCursor.Start)
        self.process.ensureCursorVisible()
        self.process.setLineWrapColumnOrWidth(400)
        self.process.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.process.setReadOnly(True)

        # 로그 처리
        self.logTextBox = QTextEditLogger(self)
        self.logTextBox.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self.logTextBox)
        logging.getLogger().setLevel(logging.DEBUG)

        # 메인윈도우에 중앙 위젯을 생성, 그리드 레이아웃 사용
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        grid = QGridLayout()
        self.centralWidget().setLayout(grid)

        # 입력 및 실행 위젯 생성
        self.stack1 = QWidget()
        self.stack1UI()
        self.stack2 = QWidget()
        self.stack2UI()
        self.stack3 = QWidget()
        self.stack3UI()

        # 그리드에 생성된 위젯을 배치(행, 열)
        grid.addWidget(self.process, 0, 0)
        grid.addWidget(self.stack1, 0, 1)
        grid.addWidget(self.stack2, 1, 0)
        grid.addWidget(self.stack3, 1, 1)

    # 주소 입력창 위젯
    def stack1UI(self):
        layout = QFormLayout()

        # 진행상태바 표시
        self.pbar = QProgressBar(self)
        self.pbar.setAlignment(QtCore.Qt.AlignCenter)
        self.pbar.setStyleSheet("QProgressBar"
                                "{"
                                "background-color : lightblue;"
                                "border : 1px"
                                "}")
        self.timer = QtCore.QBasicTimer()
        self.timer.start(100, self)

        self.url = QLineEdit()
        self.password = QLineEdit()
        self.folder = QLineEdit()
        self.check_box = QCheckBox('게시글 안에 링크 목록을 다운', self)
        label = QLabel()
        label4 = QLabel(
            '※ 저장 폴더는 현재 실행파일이 위치한 폴더' + '\n\n' +
            '1. 마나토끼와 티스토리는 만화 제목별 폴더 자동 생성: ' + '\n' +
            '   각 화 폴더는 제목별 폴더 아래에 저장' + '\n\n' +
            '2. 디시 이미지를 특정 제목 폴더 안에 넣고 싶은 경우:' + '\n' +
            '   저장폴더에 폴더이름 입력 (폴더 자동생성)'
                        )

        # 버튼 생성
        btn = QPushButton('Download', self)
        btn_clr = QPushButton('Clear', self)
        # btn.move(700, 0)
        # btn.resize(btn.sizeHint())
        btn.clicked.connect(self.download)
        btn_clr.clicked.connect(self.set_clear)

        layout.addRow("주소", self.url)
        # layout.addRow("", btn_clr)
        layout.addRow("실행", btn)
        layout.addRow("상태", self.pbar)
        layout.addRow("", label)
        layout.addRow("", label4)

        # 위젯에 작성한 레이아웃을 배치
        self.stack1.setLayout(layout)

    # 주소 입력 초기화
    def set_clear(self):
        self.url.setText('')

    def stack2UI(self):
        layout = QFormLayout()

        label = QLabel()
        label4 = QLabel(
            '※ 지원 사이트: manatoki.net , tistory.com, dcinside.com, egloos.com' + '\n\n' +
            '1. 주소창에 다운받을 사이트의 주소를 입력' + '\n\n' +
            '   ・manatoki는 전편보기 주소입력시 전편 다운(한 화도 가능):' + '\n' +
            '   예) https://manatoki77.net/comic/*****' + '\n\n' +
            '   ・tistory는 카테고리 주소입력시 전편 다운(한 화도 가능): ' + '\n' +
            '   예) https://xxx.tistory.com/category/*****  (전편)' + '\n' +
            '   예) https://xxx.tistory.com/xxx  (한 화)' + '\n\n' +
            '   ・dcinside는 입력주소 안에 있는 이미지 다운: ' + '\n' +
            '   게시글안에 복수링크가 있는 경우 디시링크 포함 체크시 전체 다운' + '\n' +
            '   예) https://gall.dcinside.com/board/view/?*****' + '\n\n' +
            '2. 실행 버튼 클릭: Download' + '\n\n' +
            '3. 완료 까지 대기: 상태 바 100% 녹색으로 변경' + '\n' +
            '   (프로세스 창이 응답 없음으로 표시되도 실제로는 기동중)' + '\n' +
            '   (콘솔창 실행 가능: Menubar - File - Console )' + '\n\n' +
            '4. 비밀번호는 티스토리 패스워드가 다를 경우만 입력후 실행: 기본 1111 설정'
                        )

        layout.addRow("[사용법]", label)
        layout.addRow("", label4)

        self.stack2.setLayout(layout)

    def stack3UI(self):
        layout = QFormLayout()
        label = QLabel()

        # layout.addRow("티스토리", label)
        layout.addRow("티스토리 비밀번호", self.password)
        layout.addRow("", label)
        # layout.addRow("디시", label)
        layout.addRow("디시 저장폴더", self.folder)
        layout.addRow("", label)
        layout.addRow("디시 다운 옵션", self.check_box)

        self.stack3.setLayout(layout)

    def display(self, i):
        self.Stack.setCurrentIndex(i)

    def download(self, i):
        self.pbar.setRange(0, 0)
        self.statusBar().showMessage('Processing...')
        print("*"*60)
        print("다운로드가 시작되었습니다.")
        print("*"*60)

        url = self.url.text()
        password = self.password.text()
        folder = self.folder.text()
        check_box = self.check_box.checkState()

        if 'manatoki' in url:
            # 마나토끼 다운로더 인스턴스 생성
            obj = toki.Downloader()
            obj.select_main(url)
            # try:
            #     obj.one_main(url)
            # except Exception:
            #     obj.zero_main(url)
        elif 'tistory' in url:
            # 티스토리 다운로더 인스턴스 생성
            obj = tistory.Downloader()

            if password:
                obj.change_password(password)

            if 'category' in url:
                obj.main(url)
            else:
                obj.one_main(url)
        elif 'dcinside' in url:
            # 디시 다운로더 인스턴스 생성
            obj = dc.Downloader()

            if folder:
                obj.change_folder(folder)

            if check_box:
                obj.two_main(url)
            else:
                obj.one_main(url)
        elif 'egloos' in url:
            # 이글루스 다운로더 인스턴스 생성
            obj = eg.Downloader()

            if 'category' in url:
                obj.main(url)
            else:
                obj.one_main(url)
        else:
            print('잘못된 주소를 입력하였습니다.')

        self.pbar.setRange(0, 100)
        self.pbar.setValue(100)
        self.statusBar().showMessage('Complete')

        print("*"*60)
        print("다운로드가 완료되었습니다.")
        self.set_clear()
        print("*"*60)

    def show_log(self):
        log = self.logTextBox.widget.toPlainText()
        self.exPopup = ExamplePopup(log)
        self.exPopup.setGeometry(400, 100, 400, 300)
        self.exPopup.show()

    def console(self):
        cmd = subprocess.run('python')


class ExamplePopup(QWidget):
    def __init__(self, log):
        super().__init__()

        self.setWindowTitle('Debug')

        grid = QGridLayout()
        self.setLayout(grid)

        process = QTextEdit()
        process.moveCursor(QtGui.QTextCursor.Start)
        process.ensureCursorVisible()
        process.setLineWrapColumnOrWidth(400)
        process.setLineWrapMode(QTextEdit.FixedPixelWidth)
        process.setReadOnly(True)
        process.setText(log)

        grid.addWidget(process)


def main():
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
