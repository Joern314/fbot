# copied from NicholasBots
# written by Nicholas Schwab
# License:
#     not exactly specified,
#     but "I can use it if he doesn't get blamed"

from bs4 import BeautifulSoup
import requests
import urllib

def ud_parser(term):
    return 'http://www.urbandictionary.com/define.php?term=' + urllib.parse.quote_plus(term)

    url='http://www.urbandictionary.com/define.php?term='
    s=requests.session()
    try:
        res=s.get(url+term)
    except e:
        return 'Fail'
    soup=BeautifulSoup(res.text, features='html.parser')
    body=soup.find('body')
    meaning=[i for i in body.findAll('div') if i.has_attr('class') and i['class']==['meaning'] ][0]
    return meaning.text
