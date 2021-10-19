import youtube_dl
import os

def download(url):

    
    url_parsed = url.split('&')[0]
    print(url_parsed)

    video_id = url_parsed.split("=")[1]

    "creo cartella"
    current_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_path, "static", "videos", video_id)
    if not os.path.exists(path):
        os.mkdir(path)

    video_path = os.path.join(path, '%(id)s.%(ext)s')

    #ydl = youtube_dl.YoutubeDL({'outtmpl': current_path + '\\static\\videos\\'+video_id+'\\%(id)s.%(ext)s'})
    ydl = youtube_dl.YoutubeDL({'outtmpl': video_path})

    with ydl:
        result = ydl.extract_info(url_parsed, download=True)

    #print(result)

    return video_id, result["title"], result["channel"], result["duration"]

if __name__ == '__main__':
    download("https://www.youtube.com/watch?v=UuzKYffpxug&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=5")