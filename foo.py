# -*- coding: utf-8 -*-
import os
import re
import glob
import shutil
import zipfile
import Tkinter, tkFileDialog

def conv(string, dic):
  i = 0
  while i < len(string):
    for j in range(len(string) - i, 0, -1):
      if string[i:][:j] in dic:
        t = dic[string[i:][:j]]
        string = string[:i] + t + string[i:][j:]
        i += len(t) - 1
        break
    i += 1
  return string
 
def mdic():   
  # http://svn.wikimedia.org/svnroot/mediawiki/trunk/phase3/includes/ZhConversion.php
  table = open('ZhConversion.txt', 'r').readlines()
  dic = dict()
  name = []
  for line in table:
    if line[0] == '$':
      name.append(dic)
      dic = dict()
    if line[0] == "'":
      word = line.split("'")
      dic[word[1]] = word[3]
  name[3].update(name[1])
  name[4].update(name[1]) 
  name[5].update(name[2]) 
  return name[3], name[4], name[5]
 
# =================================================
# TODO: 指定目錄底下的所有 epub 檔案 簡體轉繁體, 包含檔案名稱
# select ebook folder
root = Tkinter.Tk()
root.withdraw()
dirname = tkFileDialog.askdirectory(parent=root, initialdir='/', title='Please select a directory')

# prepare convert
[dic_TW, dic_HK, dic_CN] = mdic()

for epub_file in glob.glob(dirname + r'/*.epub'):
  print '-------------------------------------'
  print epub_file
  epub_file_name, epub_ext_name = os.path.splitext(epub_file)
  target_dir = epub_file_name
  epub_s2t_file = epub_file_name + '_s2t.epub'
  # extract epub file to temp folder
  zipfile.ZipFile(epub_file).extractall(target_dir)
  # convert s2t
  for base, dirs, files in os.walk(target_dir):
    for file in files:
      print file
      fn = os.path.join(base, file)
      name, ext = os.path.splitext(fn) 
      if ext in ['.opf', '.xhtml', '.ncx', '.html']: # convert
        # rename old file
        os.rename(fn, fn + '_DEL')
        # translate
        lines = open(fn + '_DEL', 'r')
        fout = open(fn, 'wt')
        words = []
        for line in lines:
          words = [conv(word, dic_TW) for word in re.split(r'(</?[\w][^>]*>)', line) if not word == '\n']
          fout.write(''.join(words))
          fout.write('\n')
        fout.close()
        lines.close()
        # delete old file
        os.remove(fn + '_DEL')
      elif ext in ['', '.css', '.xml', '.jpg']: # pass
        pass
      else:
        print '!!!!! FIND UNKNOW EXT FILE: %s%s !!!!!' % (name, ext)
  # zip folder to epub file
  zip = zipfile.ZipFile(epub_s2t_file, 'w', zipfile.ZIP_DEFLATED)
  rootlen = len(target_dir) + 1
  for base, dirs, files in os.walk(target_dir):
    for file in files:
      fn = os.path.join(base, file)
      zip.write(fn, fn[rootlen:])
  zip.close()
  # remove the temp folder 
  shutil.rmtree(target_dir)
