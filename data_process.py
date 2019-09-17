#!/usr/bin/env python
#-*- coding:utf-8 -*- 
# Author: Joven Chu
# Email: jovenchu@gmail.com
# Time: 2019-09-17 11:16:18
# Project: data_process
# About: 统一处理IMDB、20News、AGNews、DBpedia和Reuters的分类数据集格式代码，
#        通过“python data_process.py"的cmd命令方式对数据进行统一处理



import os
import xlrd
from collections import Counter
import random
import numpy as np
import json


# 获取data文件夹数据集路径
def file_name(file_dir):
    for root, dirs, files in os.walk(file_dir):
        print('root_dir:', root)  # 当前目录路径
        print('files:', files)  # 当前路径下所有非目录子文件
    tasks = [i.split('.')[0] for i in files]
    return files

# 遍历所有的数据
def data_process(data_path,train_split,output_path):
  # 获取所有数据集的文件名
  file_list = file_name(data_path)
  # 对每个数据集进行归一化处理
  for f in file_list:
    if not f.endswith("xlsx"): continue
    task = f.split('.')[0]
    print(task)
    # 读取表格数据
    workbook = xlrd.open_workbook(os.path.join(data_path, f))
    worksheet = workbook.sheet_by_index(0)
    text = worksheet.col_values(0)
    text.remove('text')
    label = worksheet.col_values(1)
    label.remove('label')
    # print(label)

    # 获取文本的数量和标签的种类
    text_len = len(text) - 1
    label_counter = Counter(label)
    label_class = [i for i in label_counter.keys()]
    class_num = len(label_class)
    print(label_class)

    # 对标签进行数字化处理
    for i,v in enumerate(label_class):
      label = [i if l == v else l for l in label]
    # print(label)
    
    # 文本和标签的合并与乱序
    text_label_all = list(zip(text,label))
    random.shuffle(text_label_all)
    text[:],label[:] = zip(*text_label_all)

    # 新建输出文件夹
    paths = os.path.join(output_path, task)
    if not os.path.exists(paths):
      os.makedirs(paths)
    data_paths = os.path.join(paths, task + '.data')
    if not os.path.exists(data_paths):
      os.makedirs(data_paths)

    # trian和test数据的分割
    train_num = int(text_len * train_split)
    test_num = text_len - train_num
    print(train_num)
    print(test_num)
    train_text = text[:train_num]
    train_label = label[:train_num]
    test_text = text[train_num:]
    test_label = label[train_num:]

    # 记录信息
    items = {
          "class_num": class_num,
          "train_num": train_num,
          "test_num": test_num,
          "language": "EN",
          "time_budget": 2400,
          "label_class":label_class
    }
    with open(os.path.join(data_paths, 'meta.json'), 'w') as file:
      file.write(json.dumps(items,ensure_ascii=False) + '\n')
      file.close()

    # 录入数据集的文本
    with open(os.path.join(data_paths, 'train.data'), 'w') as file1:
      for t in train_text:
        file1.write(str(t) + '\n')
      file1.close()

    with open(os.path.join(data_paths, 'test.data'), 'w') as file2:
      for t in test_text:
        file2.write(str(t) + '\n')
      file2.close()

    # 录入数据集的标签one-hot编码
    train_label_onehot = np.eye(class_num)[train_label]
    print(train_label_onehot)
    np.savetxt(os.path.join(data_paths, 'train.solution'),train_label_onehot,fmt = '%d') # 保存为整数，delimiter=','可改为以逗号分隔，默认空格
    test_label_onehot = np.eye(class_num)[test_label]
    print(test_label_onehot)
    np.savetxt(os.path.join(paths, task + '.solution'),test_label_onehot,fmt = '%d')




if __name__ == '__main__':
  # 数据集文件夹路径
  data_path = './data'
  # 输出文件夹路径
  output_path = './output'
  # 数据集分割比例
  train_split = 0.8
  data_process(data_path, train_split, output_path)
