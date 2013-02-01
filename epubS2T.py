#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import glob
import shutil
import zipfile
import urllib2
import Tkinter as tk, tkFileDialog

class App(tk.Frame):
  TITLE = u'epubS2T v0.1 - by 0_o'
  TXT = u'ZhConversion.txt'
  URL = u'http://svn.wikimedia.org/svnroot/mediawiki/trunk/phase3/includes/ZhConversion.php'
  HEAD = u'*.epub 簡體->繁體'
  BTN1 = u'選擇 *.epub 目錄'
  BTN2 = u'更新詞庫'

  def __init__(self, parent):
    tk.Frame.__init__(self, parent)
    self.parent = parent
    self.initUI()
    self.init()

  def initUI(self):
    self.parent.title(self.TITLE)
    # center window
    w = 600
    h = 300
    sw = self.parent.winfo_screenwidth()
    sh = self.parent.winfo_screenheight()
    x = (sw - w) / 2
    y = (sh - h) / 2
    self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    self.pack(fill=tk.BOTH, expand=1)

    headerLabel = tk.Label(self, text=self.HEAD)
    headerLabel.pack()

    frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)
    frame.pack(fill=tk.BOTH, expand=1)

    self.text = tk.Text(frame, state=tk.DISABLED)
    self.scroll = tk.Scrollbar(self.text, command=self.text.yview)
    self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
    self.text.configure(yscrollcommand=self.scroll.set)
    self.text.pack(fill=tk.BOTH, expand=1)
    
    downloadButton = tk.Button(self, text=self.BTN2, command=self.downloadTXT)
    downloadButton.pack(side=tk.LEFT, padx=5, pady=5)

    self.selectButton = tk.Button(self, text=self.BTN1, state=tk.DISABLED, command=self.select)
    self.selectButton.pack(side=tk.RIGHT, padx=5, pady=5)

  def init(self):
    if not os.path.exists(self.TXT):
      self.println(u'找不到詞庫(%s), 自動下載' % self.TXT)
      self.downloadTXT()
    self.selectButton.configure(state=tk.NORMAL)
    # prepare
    [self.dict_TW, self.dict_HK, self.dict_CN] = self.load_dict()

  def load_dict(self):   
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

  def select(self):
    dirname = tkFileDialog.askdirectory(parent=self.parent, initialdir='/', title='選擇 *.epub 資料夾')
    self.convert(dirname)

  def convert(self, dirname):
    for epub_file in glob.glob(dirname + r'/*.epub'):
      epub_file_name, epub_ext_name = os.path.splitext(epub_file)
      target_dir = epub_file_name
      epub_s2t_file = epub_file_name + '_s2t.epub'
      self.println(u'原檔案: %s' % epub_file_name)
      # extract epub file to temp folder
      zipfile.ZipFile(epub_file).extractall(target_dir)
      # convert s2t
      for base, dirs, files in os.walk(target_dir):
        for file in files:
          self.println(file)
          fn = os.path.join(base, file)
          name, ext = os.path.splitext(fn) 
          if ext in ['.opf', '.xhtml', '.ncx', '.html', '.plist']: # convert
            # rename old file
            os.rename(fn, fn + '_DEL')
            # translate
            lines = open(fn + '_DEL', 'r')
            fout = open(fn, 'wt')
            words = []
            for line in lines:
              words = [self.conv(word, self.dict_TW) for word in re.split(r'(</?[\w][^>]*>)', line) if not word == '\n']
              fout.write(''.join(words))
              fout.write('\n')
            fout.close()
            lines.close()
            # delete old file
            os.remove(fn + '_DEL')
          elif ext in ['', '.css', '.xml', '.jpg', '.png']: # pass
            pass
          else:
            self.println(u'!!!!! FIND UNKNOW EXT FILE: %s%s !!!!!' % (name, ext))
            self.println(u'請聯絡 0_o')
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
      self.println(u'新檔案: %s' % epub_s2t_file)



  def downloadTXT(self):
    self.println(u'下載 %s' % self.TXT)
    response = urllib2.urlopen(self.URL)
    output = open(self.TXT, 'wb')
    output.write(response.read())
    output.close()
    self.println(u'下載完畢')

  def println(self, s):
    self.text.configure(state=tk.NORMAL)
    self.text.insert(tk.END, '> %s\n' % s)
    self.text.configure(state=tk.DISABLED)
    self.text.update()
    self.text.see(tk.END)

  def conv(self, string, dic):
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


def main():
  root = tk.Tk()
  app = App(root)
  root.mainloop()


if __name__ == '__main__':
  main()

