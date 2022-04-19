import requests
import os
from termcolor import colored
from tqdm import tqdm
import random
import sys
from codebase.search import *
from codebase.log import *
from codebase.link_gen import *
from codebase.parselog import *


#sexy logo
logo ='''
\033[95m  ___          _                          ______  _  _       
\033[95m / _ \        (_)                         |  ___|| |(_)      
\033[95m/ /_\ \ _ __   _  _ __ ___    ___  ______ | |_   | | _ __  __
\033[95m|  _  || '_ \ | || '_ ` _ \  / _ \|______||  _|  | || |\ \/ /
\033[95m| | | || | | || || | | | | ||  __/        | |    | || | >  < 
\033[95m\_| |_/|_| |_||_||_| |_| |_| \___|        \_|    |_||_|/_/\_\\
\033[0m                                                             
'''                                                          


#create download directory
if not os.path.exists('downloads'):
    os.mkdir('downloads')

#set mpv executable
mpv_executable = "mpv.exe" if os.name == "nt" else "mpv"
ffmpeg_executable = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"

#clear screen function
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

#fnction to do updates
def update():
    r=requests.get("https://raw.githubusercontent.com/alpha-hexor/animeflix/main/codebase/link_gen.py")
    with open("codebase/link_gen.py","wb") as f:
        f.write(r.content)
    f.close()
    
    colored_print("[*]Update is done, please restart the program")
    sys.exit()
    
#function to check for upate
def check_update():
    p=open("version.txt","r")
    v=p.read()
    r=requests.get("https://raw.githubusercontent.com/alpha-hexor/animeflix/main/version.txt").text.strip("\n")
    if v!=r:
        #update is required
        update()
 
    
#write a function to print colored text
def colored_print(message):
    colors = ['red','green','blue','yellow','magenta','cyan']
    color = random.choice(colors)
    print(colored(message,color,attrs=["bold"]))

#function to get final link
def get_final_link(embade_url):
    qualities,links = generate_links(embade_url) 

    colored_print("[*]Available Qualities: ")
    for i in range(len(qualities)):
        colored_print("["+str(i+1)+"] "+qualities[i])
    opt = int(input("[*]Enter index of the quality: "))
    return links[opt-1]

#stream function
def stream_episode(name,ep_num,last_ep):
    clear()
    colored_print("[*]Streaming Episode: "+name+": episode-"+ep_num)

    embade_url = get_embade_link(name,ep_num)
    link = get_final_link(embade_url)
    
    #stream episode
    
    command = ' --referrer="https://gogoplay.io" "'+link+'"'
    os.system(mpv_executable+command)

    #for next episode
    if (int(ep_num) + 1 <= int(last_ep)):
        opt = input(("[*]Want to start next episode[y/n]: "))
        

        if (opt == "n"):
            exit()
                
        ep_num = int(ep_num)+1
        watch_log(name,str(ep_num),str(last_ep))
        stream_episode(name,str(ep_num),last_ep)
    
    else:
        exit()

#download function
def download_episode(path,name,ep_num,last_ep):
    clear()
    colored_print("[*]Downloading Episode: "+name+": episode-"+ep_num)
    embade_url = get_embade_link(name,ep_num)
    link = get_final_link(embade_url)

    #download process
    # r=requests.get(link,headers={'referer':"https://gogoplay.io"},stream=True)
    # total_size_in_bytes= int(r.headers.get('content-length', 0))
    # block_size = 1024
    # progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    # with open(path+"\\"+name+"_"+ep_num+".mp4", 'wb') as f:
    #     for data in r.iter_content(block_size):
    #         progress_bar.update(len(data))
    #         f.write(data)
    # f.close()
    # progress_bar.close()
    
    #download process with ffmpeg
    command = " -referrer=\"https://gogoplay.io\" -i "+link+" -c copy "+path+"\\"+name+"_"+ep_num+".mp4"
    os.system(ffmpeg_executable+command)

    #for next episode
    if (int(ep_num) + 1 <= int(last_ep)):
        opt = input(("[*]Want to download next episode[y/n]: "))
        

        if (opt == "n"):
            exit()
                
        ep_num = int(ep_num)+1
        download_log(name,str(ep_num),str(last_ep))
        download_episode(path,name,str(ep_num),last_ep)
    else:
        exit()

def main():
    if len(sys.argv) == 1:
        check_update()
        clear()
        print(logo)
        name = input("[*]Enter anime name: ")
        animes,anime_links =search_anime(name)

        for i in range(len(animes)):
            colored_print("["+str(i+1)+"] "+animes[i])
        
        #take input from user
        opt = int(input("[*]Enter index of the anime: "))
        anime_to_watch = anime_links[opt-1]
        
        #get episode list
        first_episode,last_episode = search_episode(anime_to_watch)

        colored_print("[*]Available Episode: [" + str(first_episode) + "-"+str(last_episode)+"]")

        #take episode num input
        ep_num = input("[*]Enter episode number: ")

        if int(ep_num) >= 0 and int(ep_num) <= last_episode:
            clear()
            colored_print('[S]tream Episode')
            colored_print('[D]ownload Episode')
            x = input("[*]Enter your choice: ")
            if x == 'd' or x == 'D':
                path = "downloads\\" + anime_to_watch
                if not os.path.exists(path):
                    os.makedirs(path)
                download_log(anime_to_watch,ep_num,last_episode)
                download_episode(path,anime_to_watch,ep_num,last_episode)
            else:
                watch_log(anime_to_watch,ep_num,last_episode)
                stream_episode(anime_to_watch,ep_num,last_episode)
        else:
            colored_print("[*]Invalid episode number")
            exit()

    else:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            '''
            --help implementation
            '''
            clear()
            print(logo)
            colored_print("[*]Usage: python app.py --help [for help]")
            colored_print("[*]Usage: python app.py [for normal usage]")
            colored_print("[*]Usage: python app.py --continue_stream [continue watch animes]")
            colored_print("[*]Usage: python app.py --continue_download [continue download animes]")
            colored_print("[*]Usage: python app.py --update [update app]")
            
            exit()
        
        
        if sys.argv[1] == "--continue_stream" :

            '''
            --continue_stream implementation
            '''
            check_update()
            clear()
            print(logo)
            #check for log file
            if not os.path.exists("watch_log.txt"):
                colored_print("[*]No watch log found")
                exit()

            anime,anime_last,names=parse_log("watch_log.txt")
            
            #take user input
            colored_print("[*]Continue Watching.........")
            for n in range(len(names)):
                colored_print("["+str(n+1)+"] "+names[n])
            
            x=int(input("[*]Enter index of anime to watch: "))
            anime_to_watch = names[x-1]
            episode_to_watch = int(anime[anime_to_watch]) + 1

            watch_log(anime_to_watch,str(episode_to_watch),anime_last[anime_to_watch])
            stream_episode(anime_to_watch,str(episode_to_watch),anime_last[anime_to_watch])
        
        
        if sys.argv[1] == "--continue_download":
            '''
            --continue_download implementation
            '''
            check_update()
            clear()
            print(logo)
            #check for log file
            if not os.path.exists("download_log.txt"):
                colored_print("[*]No download log found")
                exit()
                
            anime,anime_last,names=parse_log("download_log.txt")

            #take user input
            colored_print("[*]Continue Downloading.........")
            for n in range(len(names)):
                colored_print("["+str(n+1)+"] "+names[n])
            
            x=int(input("[*]Enter index of anime to download: "))
            anime_to_download = names[x-1]
            episode_to_download = int(anime[anime_to_download]) + 1
            path = "downloads\\" + anime_to_download

            download_log(anime_to_download,str(episode_to_download),anime_last[anime_to_download])
            download_episode(path,anime_to_download,str(episode_to_download),anime_last[anime_to_download])
        
        if sys.argv[1] == "--update":
            update()


if __name__ == "__main__":
    main()