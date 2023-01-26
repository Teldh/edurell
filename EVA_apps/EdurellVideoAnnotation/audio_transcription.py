import pysrt
import os
#import pafy
import cv2
from youtube_transcript_api import YouTubeTranscriptApi
from nltk import tokenize



#def subs_from_srt():
#    srt = pysrt.open(os.path.dirname(os.path.abspath(__file__)) + "\\video\\subtitles.srt")
#    subs = []
#
#    for sub in srt:
#        # new_sentence = Subtitle(sub.text, (sub.start, sub.end))
#        subs.append({"text": sub.text,
#                     "start": sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds + sub.start.milliseconds / 1000,
#                     "end": sub.end.hours * 3600 + sub.end.minutes * 60 + sub.end.seconds + sub.end.milliseconds / 1000})
#
#    return subs
#
#
#def text_from_srt():
#    srt = pysrt.open(
#        os.path.dirname(os.path.abspath(__file__)) + "\\video\\subtitles.srt")
#    text = ""
#
#    for sub in srt:
#        text += sub.text + " "
#
#    return text
#
#
#def get_sentences_from_punto(subs):
#    temp_list = []
#    temp_sentence = ""
#    for s in subs:
#        temp_sentence += " " + s["text"].replace("\n", " ")
#        if s["text"][-1] == ".":
#            temp_list.append(temp_sentence)
#            temp_sentence = ""
#    return temp_list


#def get_youtube_cap(url):
#    # solve problem with pafy if appears 'like_count' in console
#    # https://stackoverflow.com/questions/70297028/i-have-a-problem-with-dislike-error-when-creating-an-pafy-new-url-perhaps-its
#    # go to your env installation folder /lib/python3.7/site-packages/pafy/backend_youtube_dl.py and comment lines 53 and 54
#    # comment line with self._likes and self._dislikes
#    # print('\033[91m'+"REMAINDER FROM get_youtube_cap() TO COMMENT LINES"+'\033[0m')
#    play = pafy.new(url).streams[0]  # we will take the lowest quality stream
#    assert play is not None  # makes sure we get an error if the video failed to load
#    return cv2.VideoCapture(play.url)


def speech_from_youtube(yt_video_id:str):
    """Get the speech from a youtube video id"""

    transcript_list = YouTubeTranscriptApi.list_transcripts(yt_video_id)

    autogenerated = False
    try:
        transcript = transcript_list.find_manually_created_transcript(['en'])
    except:
        transcript = transcript_list.find_generated_transcript(['en'])
        autogenerated = True

    subs_dict = []
    for sub in transcript.fetch():

        subs_dict.append(
            {"text": sub["text"],
             "start": sub["start"],
             "end": sub["start"] + sub["duration"]}
        )

    # if autogenerated:
    #     print("subtitle are autogenerated")

    return subs_dict, autogenerated


def get_timed_sentences(subtitles, sentences):
    '''For each sentence, add its start and end time obtained from the subtitles'''

    # Compute the number of words for each sentence and for each sub
    num_words_sentence = []
    num_words_sub = []

    for s in sentences:
        num_words_sentence.append(len(s.split()))
    for s in subtitles:
        num_words_sub.append(len(s["text"].split()))

    # Get start and end time of the punctuated sentences from the subtitles
    timed_sentences = [{"text": sentences[0], "start": subtitles[0]["start"]}]

    i = 0
    j = 0

    while i < len(num_words_sentence) and j < len(num_words_sub):
        if num_words_sentence[i] > num_words_sub[j]:
            num_words_sentence[i] = num_words_sentence[i] - num_words_sub[j]
            j += 1  # qui manca controllo su j, ma non serve

        elif num_words_sentence[i] < num_words_sub[j]:
            timed_sentences[i]["end"] = subtitles[j]["end"]
            num_words_sub[j] = num_words_sub[j] - num_words_sentence[i]
            i += 1
            if i < len(num_words_sentence) and j < len(num_words_sub):
                timed_sentences.append({"text": sentences[i], "start": subtitles[j]["start"]})
        else:
            timed_sentences[i]["end"] = subtitles[j]["end"]
            num_words_sentence[i] = 0
            num_words_sub[j] = 0
            i += 1
            j += 1
            if i < len(num_words_sentence) and j < len(num_words_sub):
                timed_sentences.append({"text": sentences[i], "start": subtitles[j]["start"]})

    timed_sentences[len(timed_sentences)-1]["end"] = subtitles[len(subtitles)-1]["end"]

    """
    for i in range(0, len(timed_sentences)):

        start_to_fix = []

        j = i
        tot_length = timed_sentences[j]["start"]

        while j+1 < len(timed_sentences) and timed_sentences[j]["start"] == timed_sentences[j+1]["start"]:
            start_to_fix.append(j)
            if j+1 not in start_to_fix:
                start_to_fix.append(j+1)
                tot_length += len(timed_sentences[j]["text"])
            j+=1

        for k in range(1,len(start_to_fix)):
            time_to_add = len(timed_sentences[k-1]["text"])/tot_length
            timed_sentences[k - 1]["end"] -= time_to_add
            timed_sentences[k]["start"] = timed_sentences[k - 1]["end"]
    """




    return timed_sentences


if __name__ == '__main__':
    pass
    #objj = get_youtube_cap("https://www.youtube.com/watch?v=sXLhYStO0m8")
    #cap = get_youtube_cap("https://www.youtube.com/watch?v=sXLhYStO0m8")
    # print(subs_from_srt())
    #text = "Once you have your skeleton in the lab and you've laid it out in anatomical position and you've recorded all the bones that are present, the first aspect of identity that you want to establish is sex. One of the reasons that you do this first is because some of the other techniques are sex dependent and we only sex the skeletal remains of adult individuals. This is because establishing sex of non adults has been shown to be unreliable. There are a number of techniques that have been developed, but when they've been applied to different populations there, their reliability is not so strong. Part of the reason for this is that sexual dimorphism, so the differences between males and females does vary slightly between different populations, so this can be confusing if you're dealing with juvenile remains. So today we're just going to focus on establishing the sex of adult skeletons. The pelvis is the most accurate part of the skeleton for sex determination and there are a number of morphological differences between males and females. Here we have a male pelvis. The differences between male and female pelvis are the most accurate way of determining sex. In individuals, you will see that the male pelvis overall is much narrower and steeper, whereas the female pelvis is much shallower and broader. If we look at this angle here beneath the pubic bone, you'll see it's much narrower in males than it is in females. There are a number of other individual features and I'll go through each of these. In turn with you for comparison here we have a female pelvis and yet, as you can see, it's much shallower and broader. The subpubic angle is much wider and the length of the pubis is much longer, and this is to increase the size of the pelvic, Inlet and pelvic outlet to facilitate childbirth. The first feature that I want to show you is the sciatic notch and you'll see here on this female pelvis that it's very wide and v shaped. If we take a look at the male pelvis you'll see that it's deeper, narrower and more u shaped I've included here an intermediate example. This one I've included because it's important to remember that these features exist on a sliding scale from very feminine to intermediate to very masculine. If you do have an intermediate, sciatic notch and you're, not sure whether it's male or female, it's useful to use the composite arch here you follow the edge of the sciatic notch around the superior surface of the auricular surface in males you'll see that it forms a continuous arch when you try to do this in females, you'll see that it misses the superior surface of the auricular surface and it forms almost two separate arches. This is another female pelvis and the feature that I want to show. You is called the pre auricular sulcus. That's this concavity! Underneath the auricular surface, this feature isn't present in all females, but when it is, it tends to be quite sharp and quite deep on males. You'll rarely see it, but if you do see it, it tends onde to be a very shallow. Concavity here are fragments of a female pubis and a male pubis on the female. You can see that the subpubic angle is quite wide and u shaped on the male. You can see that it's quite narrow and v shaped on the female. You can see that the angle extends backwards from the pubic symphysis, whereas on the male it just extends downwards. Another feature to look at is called the ventral arc on females. This is this flattened triangular area here on the anterior or front surface on males this is not present. So overall, the female pelvis is much more graceful than the male in terms of the individual features they tend to be much sharper. Another feature to look at is the length of what's called the iliopubic ramus you'll see that it's much longer if we were comparing it to the diameter of the acetabulum, the hip socket here. This is much longer. We look at the male pelvis it's much shorter and is approximately equal to the diameter of the hip socket over. All these elongated features of the female are about creating a larger space to help with childbirth. The skull is also very useful for determining sex in skeletal remains. Overall, the male skull tends to be more robust and larger than the female skull, whose features tend to be a bit more gray. So I'll go through a number of the individual features of the skull with you that are useful in terms of determining sex. So here we have a male skull and you'll notice that the eye sockets are much squarer than the female on the female. They tend to be more rounded and irregular. The rims of the orbit as well on the male's tends to be thicker and blunter, whereas on the females you can see that they're, actually quite sharp. Another key feature is known as the super orbital Ridge or the brow Ridge, as you can see it's much more defined on the male and here on the female. It's quite smooth. The centre of this Ridge is referred to as the glabella, and you can see that this is quite pronounced here, whereas on the female it tends to be much less pronounced and, as you can see on this female, it's completely absent. Here we have a male and a female skull. Viewed from the side. Now you can see that the female skull is much smaller than the male one feature you can also see is that the forehead of this female tends to be a little bit more upright, whereas the forehead of the male tends to slake slightly further backwards. When we look at the mastoid process, which is this feature here, you can see that the female mastoid process is much smaller than the male. The other feature that you can see is this Ridge here above the mastoid process in the male which is quite pronounced. This is the posterior zygomatic arch. If we look at the female, you can see that it's smooth above the mastoid process and there's no pronounced Ridge. These are the same skulls. Viewed from behind. As you can see on this male goal, we've got a very pronounced region here. This is called the nuchal crest. When we look at the female, you can see that it's very smooth here. These features are related to musculature, so they're, essentially muscle attachment points. As a result of this, you do get a great deal of variety within and between different populations. So much like the pelvis, the features that were looking at form on a sliding scale from very masculine to very feminine, and these differences will vary between different populations as well as a consequence. Sex determination in the skull tends to be less accurate than it is for the pelvis, because it is influenced by factors such as lifestyle, so diet activities and that interaction with genetics, whereas sexual dimorphism in the pelvis, relates to functional morphology linked to childbirth. Here we have two femoral and it's tempting to think that the larger one is going to be male and the smaller one is going to be female in this instance. That is the case, but it's not always. We do have large females and small males, and there is a lot of overlap between males and females within a population when we're measuring the femoral can look at the length and we can look at the diameter of the femoral head and we can look at the width of the condyles and we can look to see whether these fall into a female or a male category. But again, you must be conscious of the fact that there is a lot of overlap between males and females and I would be very cautious about assigning sex on the basis of size alone. So we've gone through the different features for establishing sex from the skeleton one of the things that I think it's really important to remember is that sexual dimorphism does vary slightly between different populations, so you will have to accommodate this difference when you're looking at your own skeletal assemblage. The other thing to remember is that sexual dimorphism is on a sliding scale from very feminine feminine intermediate: probable male. It skeletons. Don't just fall neatly into two discrete categories. So again, if you remember this, when you're establishing sex in your skeletal assemblage in the next section, we're going to focus on estimating the age at death of infant and juvenile skeletal remains, and the variety of techniques that we can use for, estimating age at death, [Music]. "

    #subtitles, autogenerated = speech_from_youtube("https://www.youtube.com/watch?v=sXLhYStO0m8")
    #sentences = tokenize.sent_tokenize(text)
    '''For each sentence, add its start and end time obtained from the subtitles'''
    #timed_sentences = get_timed_sentences(subtitles, sentences)

