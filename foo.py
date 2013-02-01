# -*- coding: utf-8 -*-
import os
import re
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
# select ebook file
root = Tkinter.Tk()
root.withdraw()
origin_file = tkFileDialog.askopenfilename(parent=root, title="Choose a file")
origin_file_name, origin_file_ext = os.path.splitext(origin_file)
epub_file = origin_file_name + '.epub'
target_dir = origin_file_name
epub_s2t_file = origin_file_name + u'_s2t.epub'
mobi_s2t_file = origin_file_name + u'_s2t.mobi'
# convert file to epub format
if not origin_file_ext.lower() == '.epub':
  os.system(r'"..\..\Kindle\Calibre Portable\Calibre\ebook-convert.exe" %s %s' % (origin_file.encode('utf-8'), epub_file.encode('utf-8')))
# extract epub file to temp folder
zipfile.ZipFile(epub_file).extractall(target_dir)
# remove epub file
if not origin_file_ext.lower() == '.epub':
  os.remove(epub_file)
# prepare convert
[dic_TW, dic_HK, dic_CN] = mdic()
# convert s2t
for base, dirs, files in os.walk(target_dir):
  for file in files:
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
# convert file to mobi format
os.system(r'"..\..\Kindle\Calibre Portable\Calibre\ebook-convert.exe" %s %s' % (epub_s2t_file, mobi_s2t_file))
# remove epub file
os.remove(epub_s2t_file)

