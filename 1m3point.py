import requests
import re
from bs4 import BeautifulSoup

def write_file(string):
      rpt = open('1p3m.rpt', 'a')
      rpt.write(string+'/n')
      rpt.close()


def parse_content(url):
      response = requests.get(url)
      soup = BeautifulSoup(response.text, 'lxml')

      title = soup.find('span', {'id':'thread_subject'}).get_text()
      postlist = soup.find('div', {'id':'postlist'})
#      postlist = postlist.find_all('div', {'id':re.compile(r"post_.*")})
      tag = 'test'
      tags = postlist.find('div',{'class':'pcb'}).find('u').find_all('b')
      tag = tags[3].get_text()
      print(tag)
      postlist = postlist.find_all('td',{'class':'t_f'})
      context = postlist[0].get_text()

      write_file("title:{}    tag:{} \n{}".format(title,tag,context))
      write_file('*'*100)


def get_listpage(url):
      response = requests.get(url)
      soup = BeautifulSoup(response.text, 'lxml')
      thread_table = soup.find('table', {'summary':'forum_145'})
      threads = thread_table.find_all('tbody')

      for thread in threads:
            if thread.get('id').find('normalthread')==-1:
                  continue
            link = thread.find('th',{'class':'new'}).find('a', {"class":'s','class':'xst'}).get('href')
            parse_content(link) 


def main():
      response = requests.get('http://www.1point3acres.com/bbs/forum-145-1.html')
      soup = BeautifulSoup(response.text, 'lxml')
      url = 'http://www.1point3acres.com/bbs/forum.php?mod=forumdisplay&fid=145&sortid=311&%1=&sortid=311&page={}'

      page_range = soup.find('span', {'id':'fd_page_bottom'})
      pages = page_range.find_all('a')
      total = 0
      for page in pages:
            try:
               page = int(re.sub('\D','',page.get_text()))
            except:
               page = 0 
            if page > total:
               total = page
      print(total)

      for i in range(1, 2):
            get_listpage(url.format(i))

if __name__=="__main__":
      main()


