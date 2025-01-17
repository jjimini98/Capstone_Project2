# 텐서플로 버전확인
#import tensorflow as tf
#print(tf.__version__)


'''import os
import matplotlib.pyplot as plt

print(os.getcwd())
re = os.getcwd()
path = 'C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/annotations/training' # 폴더 경로
os.chdir(path) # 해당 폴더로 이동
files = os.listdir(path) # 해당 폴더에 있는 파일 이름을 리스트 형태로 받음
print(files)

path_list = []
for file_name in files:
    path = os.path.join("./Data_zoo/MIT_SceneParsing/dataset/annotations/training", file_name)
    path_list.append(path)
print(path_list)

os.chdir(re)  # 다시 원래 경로로
image = plt.imread(path_list[0])
#plt.figure()
plt.imshow(image)
plt.show()

'''
import os

'''import BatchDatsetReader as dataset
IMAGE_SIZE = 224

image_options = {'resize': True, 'resize_size': IMAGE_SIZE}
dataset.BatchDatset(train_records, image_options)

DATA_URL = 'http://data.csail.mit.edu/places/ADEchallenge/ADEChallengeData2016.zip'
print(os.path.splitext(DATA_URL.split("/")[-1])[0])'''


# ----------------------------------
# JPG이미지 변환 test
from PIL import Image
'''
import os

path = 'C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/images/training' # 폴더 경로
os.chdir(path) # 해당 폴더로 이동
Img = Image.open('0001train_006690.png')
width, height = Img.size
print("width  : ", width)
print("height : ", height)
print("file name : ", Img.filename)
print("format : ", Img.format_description)
#Img.save('test.jpg')
'''


'''# JPG이미지 변환 적용
f_name = ['training', 'validation']
for f in f_name:
    path = 'C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/images/{}'.format(f)
    os.chdir(path)  # 해당 폴더로 이동
    files = os.listdir(path)  # 해당 폴더에 있는 파일 이름을 리스트 형태로 받음

    names = []
    for i in files:
        n = i.replace('.png', '')
        # print(n)
        names.append(n)

    print(f, ':', names)  # 사진파일의 이름만 저장되어있는 리스트
    print(f, ':', files)  # 사진파일.png 리스트

    for i in range(len(files)):
        Img = Image.open(files[i])
        Img.save('{}.jpg'.format(names[i]))'''

# --------------------------------------------------------------------------------------------------------------------
###### 이건 한번만 돌려야됨;;
## 전체 데이터 파일 이름 가져와서 training 601 / validation 100으로 나누기 >> 무작위 추출 방법으로!!! 함수 만들어야됨
# 전체 데이터 파일 이름 가져오는데, 이때 input과 output의 사진파일 이름 차이는 마지막에 _L밖에 없음
# 그러니까 input 파일 이름만 가져와서 그거를 601, 100으로 나눠
# C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/images/training(나머지 100은 validation)파일에 저장하고
# for문과 in을 사용해 output 파일도 저렇게 나눈다
# 경로는 C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/annotations/training(나머지 100은 validation)
# Labeled_data가 output / Original_data가 input
import os
import random
import shutil
'''
def annotations(f_list):
    name = []
    for i in f_list:
        n = i.replace('.png', '_L.png')
        name.append(n)
    return name

path = 'C:/Users/user_/Desktop/capstone2/dataset/Original_data'
os.chdir(path)  # 해당 폴더로 이동
files = os.listdir(path)  # 해당 폴더에 있는 파일 이름을 리스트 형태로 받음

validation = random.sample(files, 100)  # 리스트에서 val 100개 랜덤 추출 (중복 없이)
training = []  # 나머지 train 601개 파일 이름 저장리스트
for i in files:
    if i not in validation:
        training.append(i)
print('val :', len(validation), '/ train :', len(training))  # val : 100 / train : 601
#print(validation)

# annotations 함수를 이용해 .png를 _L.png로 바꿔주기
a_training = annotations(training)
a_validation = annotations(validation)
#print(a_validation)
#print(a_training)


# >> 원래 파일 경로 : 'C:/Users/user_/Desktop/capstone2/dataset/Original_data'
# training : C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/images/training
# validation : C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/images/validation
origin_path = 'C:/Users/user_/Desktop/capstone2/dataset/Original_data'
train_path = 'C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/images/training'
for i in training:
    shutil.copyfile(os.path.join(origin_path, i), os.path.join(train_path, i))
    # shutil.copyfile(os.path.join(원래 파일위치, 파일이름), os.path.join(파일이 복사될 위치, 파일이름))
val_path = 'C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/images/validation'
for i in validation:
    shutil.copyfile(os.path.join(origin_path, i), os.path.join(val_path, i))

# >> 원래 파일 경로 : 'C:/Users/user_/Desktop/capstone2/dataset/Labeled_data'
# a_training : C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/annotations/training
# a_validation : C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/annotations/validation
origin_path = 'C:/Users/user_/Desktop/capstone2/dataset/Labeled_data'
a_train_path = 'C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/annotations/training'
for i in a_training:
    shutil.copyfile(os.path.join(origin_path, i), os.path.join(a_train_path, i))
a_val_path = 'C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/annotations/validation'
for i in a_validation:
    shutil.copyfile(os.path.join(origin_path, i), os.path.join(a_val_path, i))
'''



'''## 같은 이미지가 잘 들어간건지 확인...
path = 'C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/images/validation'
os.chdir(path)  # 해당 폴더로 이동
image_val_files = os.listdir(path)   # 해당 폴더에 있는 파일 이름을 리스트 형태로 받음
path = 'C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/annotations/validation'
os.chdir(path)
annotations_val_files = os.listdir(path)

names = []
for i in annotations_val_files:
    n = i.replace('_L', '')
    # print(n)
    names.append(n)

sum = 0
for i in image_val_files:
    if i in names:
        sum += 1

print(sum)  # sum이 100이 나왔으므로 데이터가 정상적으로 들어간것'''



#### annotations을 흑백 이미지로 바꿔봅시다~~
'''
import cv2
f_name = ['training', 'validation']
for f in f_name:
    path = 'C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/annotations/{}'.format(f)
    os.chdir(path)  # 해당 폴더로 이동
    files = os.listdir(path)  # 해당 폴더에 있는 파일 이름을 리스트 형태로 받음
    for i in files:
        path_ = 'C:/Users/user_/PycharmProjects/CapstoneProject2_test/Data_zoo/MIT_SceneParsing/dataset/annotations/{}/{}'.format(f, i)
        image = cv2.imread(path_, cv2.IMREAD_GRAYSCALE)
        cv2.imwrite(path_, image)
'''




#### ddd.txt에는 sess.run(train_step, feed_dict=feed_dict) 코드를 돌리면
#### 에러메세지와 함께 나오는 라벨 values 값들을 복붙해서 저장해놓은 텍스트파일입니다. 개수나 세봅시다.
path = 'C:/Users/user_/Desktop/capstone2/ddddd.txt'
r = open(path, mode='rt')
label_values = r.read()
print(type(label_values))
#print(label_values.split('\n'))
label_values = label_values.replace('\n', '')
label_values_list = label_values.split()
print(len(label_values_list), '\n')

labels = list(set(label_values_list))
#print(label)
label = []
er = []
for i in labels:
    if int(i) < 184:
        #print(i)
        label.append(i)
    else:
        er.append(i)

print(list(set(label)))

'''import re
for i in range(len(label_values_list)):
    if int(label_values_list[i]) > 184:
        for j in list(set(label)):
            if j in label_values_list[i]:
                #print(label_values_list[i], ':')
                for m in re.finditer(j, label_values_list[i]):
                    st = m.start()
                    #print(label_values_list[i][st:len(j)+st])
                break
## 음... 이건 못쓰겠다!

'''