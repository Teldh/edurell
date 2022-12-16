import cv2
from audio_transcription import get_youtube_cap
import os
import time
from pprint import pprint


def progressBar(current, total, barLength = 20):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))

    print('Progress of: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')


def get_keyframes():
    # cap = cv2.VideoCapture(os.path.dirname(os.path.abspath(__file__))+"\\video\\video.mp4")
    cap = get_youtube_cap("https://www.youtube.com/watch?v=0K2qhSTrXtE&ab_channel=DocSpotDocSpot")

    ret, current_frame = cap.read()
    print(current_frame.shape)

    frame_number = 0
    summation = 0

    previous_hist = []
    all_diffs = []

    while True:

        ret, current_frame = cap.read()

        if (frame_number % 1500) == 0:
            print(frame_number)

        if ret:

            current_frame = cv2.resize(current_frame, (320, 240))  # RESIZE IMAGE
            # cv2.imshow("video", current_frame)

            # # a colori
            # image = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
            # hist = cv2.calcHist([image], [0, 1, 2], None, [16, 16, 16], [0, 256, 0, 256, 0, 256])
            # hist = cv2.normalize(hist, hist).flatten()

            image = cv2.cvtColor(current_frame, cv2.COLOR_RGB2GRAY)
            hist = cv2.calcHist([image], [0], None, [64], [0, 256])
            hist = cv2.normalize(hist, hist)

            if frame_number > 0:

                # diff = cv2.compareHist(hist, previous_hist, cv2.HISTCMP_CHISQR)

                diff = 0
                for i, bin in enumerate(hist):
                    diff += abs(bin[0] - previous_hist[i][0])

                all_diffs.append(diff)

                summation += diff
                # print(frame_number)

                previous_hist = hist

            frame_number += 1
            previous_hist = hist

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        else:
            break

    S = 4

    threshold = S * (summation / frame_number)
    print(threshold)

    sec_scene = []

    shot_start = [0]

    fps = cap.get(cv2.CAP_PROP_FPS)

    # è i oppure i+1 oppure i-1 ?
    for i, d in enumerate(all_diffs):
        if d > threshold:
            # shot_start.append(i)
            secondo = i / fps
            # print("cambio scena al frame: ", i, " quindi al secondo: ", secondo)

            if round(secondo) not in sec_scene:

                if sec_scene:
                    if (round(secondo) - sec_scene[-1]) > 5:
                        sec_scene.append(round(secondo))
                        shot_start.append(i)
                else:
                    sec_scene.append(round(secondo))
                    shot_start.append(i)
    shot_start.append(frame_number)

    # for sec in sec_scene:
    #     print(f"{math.floor(sec / 60)}m {sec % 60}s")

    cap.release()
    cv2.destroyAllWindows()

    median_frames = []
    for i in range(0, len(shot_start) - 1):
        median_frames.append(round((shot_start[i + 1] - shot_start[i]) / 2 + shot_start[i]))

    # while f < len(frames) and i < len(clusters):
    #     if clusters[i].end_time > frames[f] / fps:
    #         clusters[i].keyframes.append(frames[f])
    #         f += 1
    #     else:
    #         i += 1

    return median_frames, fps

#https://www.youtube.com/watch?v=FZGugFqdr60
def color_histogram_on_clusters(video_url, cluster_starts, cluster_ends, S, seconds_range):
    """
    Take a list of clusters and compute the color histogram on end and start of the cluster
    :param video_url: video url from youtube
    :param cluster_list
    :param S: scala per color histogram
    :param seconds_range: aggiustare inizio e fine dei segmenti in base a differenza nel color histogram
    """

    if "watch?v=" in video_url:
        video_id = video_url.split("?v=")[-1]
        #print(video_id)
        #video_id = video_url.split('&')[0].split("=")[1]
    else:
        video_id = video_url.split("/")[-1]
    #video_id = video_url.split('&')[0].split("=")[1]

    current_path = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(current_path, "static", "videos", video_id, video_id + ".mp4")
    #cap = get_youtube_cap(video_url)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        video_path = video_path.replace(".mp4",".mkv")
        cap = cv2.VideoCapture(video_path)
    print(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("fps:", fps)

    # cluster_ends = []
    # cluster_starts = []
    # for c in cluster_list:
    #     cluster_ends.append(int(c.end_time * fps))
    #     cluster_starts.append(int(c.start_time * fps))


    #prendo frame iniziali e finali dei segmenti
    cluster_frame_ends = []
    cluster_frame_starts = []
    for i, c in enumerate(cluster_starts):
        cluster_frame_ends.append(int(cluster_ends[i] * fps))
        cluster_frame_starts.append(int(cluster_starts[i] * fps))

    print("PRIMA:")
    print(cluster_frame_starts)
    print(cluster_frame_ends)
    print()

    frame_number = 0
    summation = 0
    frame_to_skip = int(fps)* 10 #guardo un frame al secondo

    previous_hist = []
    all_diffs = []
    images_path = []

    '''Calcolo le dif per trovare threshold con la formula '''
    print("Histograms Progress: ", end="")
    while cap.isOpened():

        ret, current_frame = cap.read()
        cap.set(1, frame_number)

        if ret:
            current_frame = cv2.resize(current_frame, (240, 180))

            image = cv2.cvtColor(current_frame, cv2.COLOR_RGB2GRAY)
            hist = cv2.calcHist([image], [0], None, [32], [0, 128])
            hist = cv2.normalize(hist, hist)

            if frame_number > 0:

                diff = 0
                for i, bin in enumerate(hist):
                    diff += abs(bin[0] - previous_hist[i][0])
                all_diffs.append(diff)
                summation += diff

            frame_number += frame_to_skip
            previous_hist = hist

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        else:
            break
            
    cap.release()
    threshold = S * (summation / frame_number)

    '''
    Controllo se c'è un cambio scena in un intorno di "seconds_range" frames dalla fine ed inizio di ciascun cluster.
    '''

    start_changes = []
    end_changes = []

    for end in cluster_frame_ends:
        change_found = False
        for i in range(seconds_range):
            end_diff = int(end / frame_to_skip)

            if end_diff + i < len(all_diffs) and all_diffs[end_diff + i] > threshold:
                sec = (end + i) / fps
                end_changes.append(sec)
                change_found = True
                break

        if not change_found:
            end_changes.append(-1)



    for j, start in enumerate(cluster_frame_starts):
        change_found = False
        for i in range(seconds_range):
            start_diff = int(start/frame_to_skip)

            if start_diff - i >= 0 and all_diffs[start_diff - i] > threshold:
                sec = (start - i) / fps
                start_changes.append(sec)
                change_found = True
                break

        if not change_found:
            start_changes.append(-1)



    # for i, c in enumerate(cluster_list):
    #     if start_changes[i] != -1:
    #         c.start_time = start_changes[i]
    #     if end_changes[i] != -1:
    #         c.end_time = end_changes[i]

    for i, c in enumerate(cluster_starts):
        if start_changes[i] != -1:
            cluster_starts[i] = start_changes[i]
        if end_changes[i] != -1:
            cluster_ends[i] = end_changes[i]

        cluster_starts[i] = round(cluster_starts[i], 2)
        cluster_ends[i] = round(cluster_ends[i], 2)

    print(cluster_starts)

    # salvo immagini da mostrare nella timeline
    cap = get_youtube_cap(video_url)

    for i, start in enumerate(cluster_frame_starts):

        cap.set(1, start)
        ret, current_frame = cap.read()

        current_path = os.path.dirname(os.path.abspath(__file__))
        image_name = str(i) #str(cluster_starts[i]).replace(".","_")

        saving_position = os.path.join(current_path, "static", "videos", video_id, image_name + ".jpg")
        print(saving_position)
        #saving_position = "videos\\" + video_id + "\\" + str(start) + ".jpg"
        cv2.imwrite(saving_position, current_frame)
        images_path.append("videos/" + video_id + "/" + image_name + ".jpg")

    cap.release()
    #print(images_path)
    ''' Ritorno le path delle immagini della timeline'''
    return images_path, cluster_starts, cluster_ends



# RETURN ROI FROM VIDEO, funziona
# from PIL import Image
# import base64
# import io
# import numpy as np
#
# #https://www.youtube.com/watch?v=sXLhYStO0m8" xywh=percent:9,10,83,80" "00:01:05^^xsd:dateTime"
# def get_image_from_video(video_id, concept, timestamp, x_percent, y_percent, w_percent, h_percent):
#
#     current_path = os.path.dirname(os.path.abspath(__file__))
#
#     video_path = os.path.join(current_path, "static", "videos", video_id, video_id + ".mp4")
#     image_path = os.path.join(current_path, "static", "videos", video_id, "concepts")
#
#     cap = cv2.VideoCapture(video_path)
#
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#     height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#
#     x = int(width * x_percent/100)
#     y = int(height * y_percent/100)
#
#     w = int(width * w_percent/100)
#     h = int(height * h_percent / 100)
#
#
#     cap.set(1, int(fps * timestamp))
#     ret, current_frame = cap.read()
#
#     data = io.BytesIO()
#     encoded_img_data = ""
#     if ret:
#         ROI = current_frame[y:y+h, x:x+w].copy()
#
#         img = cv2.cvtColor(ROI, cv2.COLOR_BGR2RGB)
#         im = Image.fromarray(img)
#         #im.show()
#         im.save(data, "JPEG")
#         encoded_img_data = base64.b64encode(data.getvalue())
#
#         #status = cv2.imwrite(os.path.join(image_path, concept+".jpg"), ROI)
#         #print(status)
#
#     cap.release()
#     return encoded_img_data


if __name__ == "__main__":
    a = time.time()
    #get_image_from_video('sXLhYStO0m8', "auricular_surface", 166, 5,16,29,65)
    #print("Time: ", time.time() - a, " secondi")