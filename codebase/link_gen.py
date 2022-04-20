import requests
from bs4 import BeautifulSoup
import json
import base64
from Cryptodome.Cipher import AES
import yarl
from .m3u8 import *



#huge help from animedl

#some global things
headers = {"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
main_url = "https://gogoanime.fi/"

s=b'37911490979715163134003223491201'
s_2 = b'54674138327930866480207815084989'
iv= b'3134003223491201'


#pad_data="\x08\x0e\x03\x08\t\x03\x04\t"

def get_embade_link(name,ep_num):
    '''
    function to get emabde url
    '''
    link = main_url + name +"-episode-"+ep_num
    try:

        r=requests.get(link,headers=headers)
    except:
        link = main_url+name+"-episode-0"
        r=requests.get(link,headers=headers)
    
    src = r.content
    soup = BeautifulSoup(src,'lxml')

    for item in soup.find_all('a', attrs={'href':'#',"rel":"1",'data-video' : True}):
        url = str(item['data-video'])
    url = "https:" + url
    return url

def get_crypto(url):
    '''
    function to get crypto data
    '''
    r=requests.get(url,headers=headers)
    src = r.content
    soup = BeautifulSoup(src,'lxml')
    for item in soup.find_all('script',attrs={'data-name':'episode','data-value':True}):
        crypto = str(item['data-value'])
    return crypto
    
def pad(data):
    '''
    helper function
    '''
    return data + chr(len(data) % 16) * (16 - len(data) % 16)


def decrypt(key,data):
    '''
    function to decrypt data
    '''
    return AES.new(key, AES.MODE_CBC, iv=iv).decrypt(base64.b64decode(data))

def generate_links(url):
    '''
    function to generate streaminhg urls and get qualities
    '''
    qualities = []
    links = []

    crypto_data=get_crypto(url)
    # #get the decrypted crypto value
    decrypted_crypto = decrypt(s,crypto_data)
    new_id = decrypted_crypto[decrypted_crypto.index(b"&"):].strip(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10").decode()
    
    
    p_url = yarl.URL(url)
    
    #construct the key
    #key = (base64.b64decode(p_url.query.get('id'))+iv).hex()[:32].encode()
    
    
    ajax_url = "https://{}/encrypt-ajax.php".format(p_url.host)
    encrypted_ajax = base64.b64encode(
        AES.new(s,AES.MODE_CBC,iv=iv).encrypt(
            pad(p_url.query.get('id')).encode()
        )
    )

    #send the request
    r =requests.get(
        f'{ajax_url}?id={encrypted_ajax.decode()}{new_id}&alias={p_url.query.get("id")}',
        
        headers={'x-requested-with': 'XMLHttpRequest'}
    )

    j = json.loads(
        decrypt(s_2,r.json().get("data")).strip(
            b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10"
        )
    )
    #print(j)
    if j['source'][0]['type'] == "hls" or j['source'][0]['file'].split(".")[-1] == "m3u8":
        qualities,links = get_m3u8_quality(j['source'][0]['file'])
        return qualities,links
    else:
        #maximum 4 links
        for i in range(4):
            try:
                link = j['source'][i]['file']
                links.append(link)
                q = j['source'][i]['label']
                qualities.append(q)
            except:
                pass


        return qualities, links
