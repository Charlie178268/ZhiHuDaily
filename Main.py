#encoding=utf-8
import  requests
import urllib2
import HTMLParser   #解析网页
import json
import re
#出现以下错误引用sys
#'ascii' codec can't decode byte 0xe8 in position 0: ordinal not in range(128)
import sys
reload(sys)
sys.setdefaultencoding('utf-8')#设置输出的格式为utf-8

#爬取知乎日报的内容
#注意知乎日报网页有反爬虫机制，如果只是
#url = "http://daily.zhihu.com/"
#r = requests.get(url)
#print (r.text)
#这样是请求不到信息的，必须模拟浏览器发送请求，也就是发送头部信息


#根据给定的url获取源码
def getHtml(url):
    #在f12的任意一个元素的headers的users-agent，然后注意加双引号
    header={
        "User - Agent": "Mozilla / 5.0(Windows NT 6.1;    WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 57.0.2987.133Safari / 537.36"
    }
    request = urllib2.Request(url, headers=header)  #用地址创建一个对象
    response = urllib2.urlopen(request) #打开网址
    text = response.read()  #获取源代码
    return text

#从给定的网页源码中获得所有日报的链接，如<a href="/story/9422488"
def getUrls(htmlStr):
    #正则规则，(.*?)表示所有字符，其实要匹配的是7位数字，re.S表示匹配换行符
    pattern = re.compile('<a href="/story/(.*?)" ', re.S)
    allHref = re.findall(pattern, htmlStr)
    urls = []   #创建存放具体网址的列表
    for item in allHref:
        urls.append("http://daily.zhihu.com/story/"+item)
        #print(urls[-1]) #-1表示打印列表最后的元素
    return urls

#从给定的url中获取标题
def getTitle(url):
    html = getHtml(url)
    #获取标题
    pattern = re.compile('<title>(.*?)</title>',re.S)
    title = re.findall(pattern, html)
    return title

#从给定的url中获取正文内容
def getContent(url):
    html = getHtml(url)
    # 获取内容
    pattern = re.compile('<div class="content">(.*?)</div>', re.S)
    content = re.findall(pattern, html)
    contentStr = ""
    #去掉文本中的所有html标签
    for item in content:
        for con in deleteHtmlLabel(item):
            contentStr += con

    return contentStr

#去掉文本中所有html标签
def deleteHtmlLabel(htmlContent):
    htmlParser = HTMLParser.HTMLParser()
    pattern = re.compile('<p>(.*?)</p>|<li>(.*?)</li>.*?', re.S)
    items = re.findall(pattern, htmlContent)
    result = []
    for index in items:
        if index != '':
            for content in index:
                tag = re.search('<.*?>', content)
                http = re.search('<.*?http.*?>', content)
                html_tag = re.search('&', content)
                if html_tag:
                    content = htmlParser.unescape(content)
                if http:
                    continue
                elif tag:
                    pattern = re.compile('(.*?)<.*?>(.*?)</.*?>(.*)')
                    items = re.findall(pattern, content)
                    content_tag = ''
                    if len(items)>0:
                        for item in items:
                            if len(item)>0:
                                for item_s in item:
                                    content_tag = content_tag+item_s
                            else:
                                content_tag = content_tag+item_s
                        content_tag = re.sub('<.*?>', '', content_tag)
                        result.append(content_tag)
                    else:
                        continue
                else:
                    result.append(content)
    return result

def main():
    url = "http://daily.zhihu.com/"
    sourceCode = getHtml(url)
    dailyLink = getUrls(sourceCode)
    for item in dailyLink:
        try:
            title = getTitle(item)
            print "\n***********标题："+title[0]+"*************\n"   #如果直接输出content，输出的是unicode编码，
                            #这是因为中文在可迭代对象里面是unicode编码，如果把它取出就是中文状态，也可以用for in输出
            content = getContent(item)
            print content
        except Exception,e:
            print e

if __name__ == '__main__':#判断文件入口
    main()