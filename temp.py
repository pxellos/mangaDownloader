import os
import glob


directory = 'D:\\Hitomi_jmana\\[핫산] 아이돌 마스터 신데렐라 걸즈 U149 2화 [제 3 예능과②]'
print(directory)

# 폴더 내의 모든 파일 및 디렉토리 가져오기
files = os.listdir(directory)
print(files)

# 파일만 필터링하고 시간 순서로 정렬
files = [f for f in files if os.path.isfile(os.path.join(directory, f))]
print(files)

files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(directory, f)))

print(files)

# 파일명 변경 및 삭제
for i, filename in enumerate(files):
    # 파일 경로
    file_path = os.path.join(directory, filename)
    
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
        new_path = os.path.join(directory, new_filename)
        os.rename(file_path, new_path)
        print(f'Renamed: {file_path} => {new_path}')