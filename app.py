from tqdm import tqdm
import base64
import json
import yarl
from Cryptodome.Cipher import AES
import requests
from bs4 import BeautifulSoup
import re
from termcolor import colored
import random
import os
from datetime import date,datetime
import platform
import sys

#global lists
anime_links = []
animes = []

headers = {"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
main_url = "https://www1.gogoanime.pe/"

#create a download directory
if not os.path.exists("downloads"):
    os.mkdir("downloads")

#function to set mpv executable
if platform.system() == "Windows":
    mpv_executable ="mpv.exe"
else:
    mpv_executable = "mpv"
#clear function
def clear():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

#write a function to print colored text
def colored_print(message):
    colors = ['red','green','blue','yellow','magenta','cyan']
    color = random.choice(colors)
    print(colored(message,color,attrs=["bold"]))


#padding
def pad(data):
    length = 16-(len(data)%16)
    return data+chr(length)*length

#function for get final shit link
def parse_url(embade_url):
    qualities = []
    links=[]
    s = b"257465385929383"b"96764662879833288"
    p_url = yarl.URL(embade_url)
    next_host = "https://{}/".format(p_url.host)
    encrypted_ajax = base64.b64encode(AES.new(s, AES.MODE_CBC, iv=b'4206913378008135').encrypt(pad(p_url.query.get('id').replace('%3D', '=')).encode()))
    c=(requests.get(
        "{}encrypt-ajax.php".format(next_host),
        params={
            'id':encrypted_ajax.decode(),
            'time':'69420691337800813569'
        },
        headers={'x-requested-with':'XMLHttpRequest'}
    ))
    j = json.loads(c.text)
    for i in range(4):
        try:
            link = j['source'][i]['file']
            links.append(link)
            q = j['source'][i]['label']
            qualities.append(q)
        except:
            pass
    colored_print("[*]Availabel qualities")
    for i in range(len(qualities)):
        colored_print("["+str(i+1)+"]"+qualities[i])
    x = int(input("[*]Enter Index: "))
    x -= 1
    return links[x]



#function to search anime
def search_anime(name):
    if len(name) > 1:
        name = name.replace(" ","-")
    search_url = main_url + "//search.html?keyword="+name
    r = requests.get(search_url,headers=headers)
    src = r.content
    soup = BeautifulSoup(src,'lxml')
    hrefs = soup.find_all("p",attrs={'class':'name'})


    #get all the links
    for h in hrefs:
        tags = str(h)
        link = tags.split('/')[2].split('"')[0]
        anime_links.append(link)

    #for the names
    for href in hrefs:
        href = str(href)
        anime_name = re.sub('<[^>]*>', '', href)
        animes.append(str(anime_name))

#function to search last and first episode
def search_episode(name):
    ep_url = main_url + "/category/"+name
    #print(ep_url)
    k = requests.get(ep_url,headers=headers)
    src2 = k.content
    soup2 = BeautifulSoup(src2,'lxml')
    eps = soup2.find("a",attrs={'href':'#',"class":"active"}).text
    first_episode = eps.split("-")[0]
    first_episode = int(first_episode)+1
    try:
        last_episode = eps.split("-")[1]
        last_episode = int(last_episode)
    except:
        last_episode = 1
    return(first_episode,last_episode)

#create a watch log
def create_log(name,ep_number,last_ep):
    current_date = date.today()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    with open("watch_log.txt","a") as f:
        f.write("["+str(current_date) + ":" + current_time + "] Starting " + name+": episode-"+ep_number+":"+str(last_ep)+"\n")
    f.close()

#create a download log
def download_log(name,ep_number,last_ep):
    current_date = date.today()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    with open("download_log.txt","a") as f:
        f.write("["+str(current_date) + ":" + current_time + "] Downloaded " + name+": episode-"+ep_number+":"+str(last_ep)+"\n")
    f.close()


#get embade url
def get_embade_link(name,ep_num):
    link = main_url + "/"+name+"-episode-"+ep_num
    try:
        m = requests.get(link,headers=headers)
    except:
        main_url + "/"+name+"-episode-0"
        m=requests.get(link,headers=headers)
    src3 = m.content
    soup3 = BeautifulSoup(src3,'lxml')
    
    for item in soup3.find_all('a', attrs={'href':'#',"rel":"100",'data-video' : True}):
        url = str(item['data-video'])
    url = "https:" + url
    return url

#function to stream episode
def stream_episode(name,ep_num,last_ep):
    clear()
    colored_print("[*]Streaming episode: " +name+":"+ep_num)
    
    embade_url = get_embade_link(name,ep_num)
    link = parse_url(embade_url)
    #print(link)
    command = ' "'+link+'"'
    os.system(mpv_executable+command)
    if (int(ep_num) + 1 <= int(last_ep)):
        opt = input(("[*]Want to start next episode[y/n]: "))
    

        if (opt == "y"):
            
            ep_num = int(ep_num)+1
            create_log(name,str(ep_num),str(last_ep))
            stream_episode(name,str(ep_num),last_ep)
        else:
            exit()
    else:
        exit()

#fucntion to download episode
def download_episode(path,name,ep_num,last_ep):
    clear()
    colored_print("[*]Downloading episode: " +name+":"+ep_num)
    embade_url = get_embade_link(name,ep_num)
    link = parse_url(embade_url)
    r=requests.get(link,headers={'referer':"https://gogoplay.io"},stream=True)
    total_size_in_bytes= int(r.headers.get('content-length', 0))
    block_size = 1024 #1 kilobyte data
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(path+"\\"+name+"_"+ep_num+".mp4", 'wb') as f:
        for data in r.iter_content(block_size):
            progress_bar.update(len(data))
    
            f.write(data)
    f.close()
    progress_bar.close()

    

    if (int(ep_num) + 1 <= int(last_ep)):
        opt = input(("[*]Want to start next episode[y/n]: "))
    

        if (opt == "y"):
            
            ep_num = int(ep_num)+1
            download_log(name,str(ep_num),str(last_ep))
            download_episode(path,name,str(ep_num),last_ep)
        else:
            exit()
    else:
        exit()

#function for continue streaming
def continue_stream():
    anime = {}
    anime_last = {}
    names = []
    if not os.path.exists("watch_log.txt"):
        print("[*]No watch log found")
        exit()
    else:
        #parse the watch log
        with open("watch_log.txt","r") as f:
           

            for line in f.readlines():
                #print(line)
                p = line.strip("\n")
               
                if len(p) > 1:
                    s= p.split(" ")
                    name = s[2]
                    name = name.replace(":","")
                    names.append(name)
                    episode_watched = s[-1].split("-")[-1].split(":")[0]
                    
                    last_episode = s[-1].split("-")[-1].split(":")[1]
                    
                    if str(episode_watched) != str(last_episode):
                        anime[name] = str(episode_watched)
                        anime_last[name] = str(last_episode)

                       
                    else:
                        anime[name] = "watched"
        f.close()
        #delete duplicate names
        n=set(names)
        names = list(n)

        #delete already finished anime names
        for i in names:
            if anime[i] == "watched":
                names.remove(i)
        
        #take user input
        colored_print("[*]Continue Watching...........")
        for n in range(len(names)):
            colored_print("["+str(n+1)+"] "+names[n])
        
        x=int(input("[*]Enter index of anime to watch: "))
        x-=1
        anime_to_watch = names[x]
        episode_to_watch = int(anime[anime_to_watch]) + 1
        
        create_log(anime_to_watch,str(episode_to_watch),str(anime_last[anime_to_watch]))
        stream_episode(anime_to_watch,str(episode_to_watch),str(anime_last[anime_to_watch]))

#function for continue downloading
def continue_download():
    anime = {}
    anime_last = {}
    names = []
    if not os.path.exists("download_log.txt"):
        colored_print("[*]No watch log found")
        exit()
    else:
        #parse the watch log
        with open("download_log.txt","r") as f:
           

            for line in f.readlines():
                #print(line)
                p = line.strip("\n")
               
                if len(p) > 1:
                    s= p.split(" ")
                    name = s[2]
                    name = name.replace(":","")
                    names.append(name)
                    episode_watched = s[-1].split("-")[-1].split(":")[0]
                    
                    last_episode = s[-1].split("-")[-1].split(":")[1]
                    
                    if str(episode_watched) != str(last_episode):
                        anime[name] = str(episode_watched)
                        anime_last[name] = str(last_episode)

                       
                    else:
                        anime[name] = "downloaded"
        f.close()
        #delete duplicate names
        n=set(names)
        names = list(n)

        #delete already finished anime names
        for i in names:
            if anime[i] == "downloaded":
                names.remove(i)
        
        #take user input
        colored_print("[*]Continue Downloading...........")
        for n in range(len(names)):
            colored_print("["+str(n+1)+"] "+names[n])
        
        x=int(input("[*]Enter index of anime to download: "))
        x-=1
        anime_to_watch = names[x]
        episode_to_watch = int(anime[anime_to_watch]) + 1
        path = "downloads\\" + anime_to_watch
        download_log(anime_to_watch,str(episode_to_watch),str(anime_last[anime_to_watch]))
        download_episode(path,anime_to_watch,str(episode_to_watch),str(anime_last[anime_to_watch]))


#main function
def main():
    if len(sys.argv) == 1:
        try:
            #get anime name
            name = input("[*]Enter Anime Name: ")
            search_anime(name)

            #print all the names
            for i in range(len(animes)):
                colored_print("["+str(i+1)+"] "+animes[i])
            
            #take input
            opt = input("[*]Enter the index of the anime you want to watch: ")
            animes_to_watch = anime_links[int(opt)-1]

            #get first and last episode
            first_ep,last_ep = search_episode(animes_to_watch)
            

            colored_print("[*]Available Episode: [" + str(first_ep) + "-"+str(last_ep)+"]")

            #take episode num as input
            ep_num = input("[*]Enter the episode number you want to watch: ")

            if((int(ep_num) >= 0) and (int(ep_num) <= last_ep)):
                clear()
                colored_print('[S]tream Episode')
                colored_print('[D]ownload Episode')
                x = input("[*]Enter your choice: ")
                if(x == "D" or x == "d"):
                    path = "downloads\\" + animes_to_watch
                    if not os.path.exists(path):
                        os.makedirs(path)
                    download_log(animes_to_watch,ep_num,last_ep)
                    download_episode(path,animes_to_watch,ep_num,last_ep)
                else:
                    create_log(animes_to_watch,ep_num,last_ep)
                    stream_episode(animes_to_watch,ep_num,last_ep)
            else:
                colored_print("[*]Invalid episode number")
                exit()
        except Exception as e:
            colored_print(e)
            exit()
    else:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            colored_print("[*]Usage: python app.py --help [for help]")
            colored_print("[*]Usage: python app.py [for normal usage]")
            colored_print("[*]Usage: python app.py --continue_stream [continue watch animes]")
            colored_print("[*]Usage: python app.py --continue_download [continue download animes]")
            
            exit()
        if sys.argv[1] == "--continue_stream" :
            continue_stream()
        if sys.argv[1] == "--continue_download":
            continue_download()
        
main()