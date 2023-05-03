import urllib.request
import json
import re
from bs4 import BeautifulSoup
import time
############################################################################
#path of the wiki page (top page)
wiki_start = 'https://wiki.defillama.com/w/index.php?title=Category:Protocols'
wiki_root = 'https://wiki.defillama.com/'

# for saving 
save_raw_path = './raw_data'
############################################################################
def download_page(url):
    try:
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        req = urllib.request.Request(url, headers = headers)
        resp = urllib.request.urlopen(req)
        respData = str(resp.read())
        return respData
    except Exception as e:
        print(str(e))

def string_handler(str):
    str = str.replace('<p>', '')
    str = str.replace('</p>', '')
    str = str.replace('\\n', ' ')
    str = str.replace('\n', ' ')
    return str

def manual_tag_remove(str, tag):
    indices = []
    for match in re.finditer('<' + tag, str):
        first_index = match.start()        
        end_index = str[first_index:].find('</' + tag + '>')
        indices.append((first_index, first_index + end_index))
    indices.reverse()
    tag_length = len('</'+tag+'>')

    for ind in indices:
        first_index = ind[0]
        end_index = ind[1]
        segment = BeautifulSoup(str[first_index:end_index+tag_length], 'html.parser')
        str = str.replace(str[first_index:end_index+tag_length], segment.getText())
    return str

def manual_remove_set(str, tags):
    for tag in tags:
        str = manual_tag_remove(str, tag)
    return str


# main content-collecting function
def collector(raw_data:dict, a_tags:list, handled_tags:list, time_sleep:float):
    for entry in a_tags:
        raw_data['protocol'].append(entry.string) # protocol title
        
        # getting short descriptions of each protocol
        protocol_page = download_page(wiki_root + entry['href'])
        parsed = BeautifulSoup(protocol_page, 'html.parser')
        p_tags = parsed.find_all('p')

        # concat p_tags
        concat = []
        for entry in p_tags:

            string = str(entry)
            string = string_handler(string) # takes care of p tags and some delimiters
            string = manual_remove_set(string, handled_tags) # a tags
            concat.append(string)

        concat = str.join('', concat)
        raw_data['description'].append(concat)
        # introduce time delay to prevent "too many request" error 
        time.sleep(time_sleep)
        print('retrieved ' + raw_data['protocol'][-1])

#############################################################
# get a list of Dapps in DeFillamma
res = download_page(wiki_start)
soup = BeautifulSoup(res, 'html.parser')

# get body(html)
body = soup.find("div", {"id":"mw-pages"})
a_tags = body.find_all('a')

# handling pagination (website specific)
next_page = wiki_root + a_tags[0]['href'] # use it later
a_tags.pop(0)
a_tags.pop(-1)
################################################################
# tags that must be handled separately. Only the formatting strings will be stripped (contents will be preserved)
handled_tags = ['a', 'sup', 'b'] 

# collection dict
raw_data ={}
raw_data['protocol']=[]
raw_data['description']=[]
#################################################################
# collect contents
collector(raw_data, a_tags, handled_tags, 0.5)


# save the crawled first page info
with open(save_raw_path+ '/raw_data.json', 'w') as fp:
    json.dump(raw_data, fp)

# load 
with open(save_raw_path+ '/raw_data.json', 'r') as fp:
    raw_data = json.load(fp)

################################################################
# next page (same drill)
res = download_page(next_page)
soup = BeautifulSoup(res, 'html.parser')
# get body 
body = soup.find("div", {"id":"mw-pages"})
a_tags = body.find_all('a')
a_tags.pop(0)
a_tags.pop(-1)

collector(raw_data, a_tags, handled_tags, 0.5)

# save again 
with open(save_raw_path+ '/raw_data.json', 'w') as fp:
    json.dump(raw_data, fp)










