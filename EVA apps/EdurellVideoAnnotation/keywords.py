import string
from gensim.summarization import keywords
import pke
from nltk.corpus import stopwords
import re
from keybert import KeyBERT
import RAKE
from conll import lemmatize


def extract_keywords(text):
    # concateno due metodi di estrazione: bert + multipartite
    model = KeyBERT('distilbert-base-nli-mean-tokens')
    bert_words = model.extract_keywords(text, top_n=8, use_mmr=True, diversity=0.5)

    concepts = [k[0] for k in bert_words]

    multipartite_words = keywords_multipartite(text)
    for k in multipartite_words:
        concepts.append(k[0])

    Rake = RAKE.Rake(RAKE.SmartStopList())
    rake_words = Rake.run(text, maxWords=2, minFrequency=2)

    for j in rake_words[0:8]:
        concepts.append(j[0])


    for i, concept in enumerate(concepts):
        concepts[i] = concept.replace("-", " ").replace("/", " / ")

    return concepts

def keywords_BERT(text):
    model = KeyBERT('distilbert-base-nli-mean-tokens')
    bert_words = model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words=stopwords.words('english'),
                                         top_n=10, use_mmr=True, diversity=0.7)

    concepts = [k[0] for k in bert_words]

    return concepts


def keywords_multipartite(text):
    # 1. create a MultipartiteRank extractor.
    extractor = pke.unsupervised.MultipartiteRank()

    # 2. load the content of the document.
    extractor.load_document(input=text)

    # 3. select the longest sequences of nouns and adjectives, that do
    #    not contain punctuation marks or stopwords as candidates.
    pos = {'NOUN', 'PROPN', 'ADJ'}
    stoplist = list(string.punctuation)
    stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
    stoplist += stopwords.words('english')
    extractor.candidate_selection(pos=pos, stoplist=stoplist)

    # 4. build the Multipartite graph and rank candidates using random walk,
    #    alpha controls the weight adjustment mechanism, see TopicRank for
    #    threshold/method parameters.
    extractor.candidate_weighting(alpha=1.1,
                                  threshold=0.74,
                                  method='average')

    # 5. get the 10-highest scored candidates as keyphrases
    keyphrases = extractor.get_n_best(n=8)

    return keyphrases


def keywords_positionRank(text):
    # define the valid Part-of-Speeches to occur in the graph
    pos = {'NOUN', 'PROPN', 'ADJ'}

    # define the grammar for selecting the keyphrase candidates
    grammar = "NP: {<ADJ>*<NOUN|PROPN>+}"

    # 1. create a PositionRank extractor.
    extractor = pke.unsupervised.PositionRank()

    # 2. load the content of the document.
    extractor.load_document(input=text,
                            language='en',
                            normalization=None)

    # 3. select the noun phrases up to 3 words as keyphrase candidates.
    extractor.candidate_selection(grammar=grammar,
                                  maximum_word_number=3)

    # 4. weight the candidates using the sum of their word's scores that are
    #    computed using random walk biaised with the position of the words
    #    in the document. In the graph, nodes are words (nouns and
    #    adjectives only) that are connected if they occur in a window of
    #    10 words.
    extractor.candidate_weighting(window=10,
                                  pos=pos)

    # 5. get the 10-highest scored candidates as keyphrases
    keyphrases = extractor.get_n_best(n=10)

    return keyphrases


def keywords_singleRank(text):

    pos = {'NOUN', 'PROPN', 'ADJ'}

    # 1. create a SingleRank extractor.
    extractor = pke.unsupervised.SingleRank()

    # 2. load the content of the document.
    extractor.load_document(input=text,
                            language='en',
                            normalization=None)

    # 3. select the longest sequences of nouns and adjectives as candidates.
    extractor.candidate_selection(pos=pos)

    # 4. weight the candidates using the sum of their word's scores that are
    #    computed using random walk. In the graph, nodes are words of
    #    certain part-of-speech (nouns and adjectives) that are connected if
    #    they occur in a window of 10 words.
    extractor.candidate_weighting(window=10, pos=pos)

    # 5. get the 10-highest scored candidates as keyphrases
    keyphrases = extractor.get_n_best(n=10)

    return keyphrases

def keywords_yake(text):
    pos = {'NOUN', 'PROPN', 'ADJ'}

    # 1. create a YAKE extractor.
    extractor = pke.unsupervised.YAKE()

    # 2. load the content of the document.
    extractor.load_document(input=text,
                            language='en',
                            normalization=None)

    # 3. select {1-3}-grams not containing punctuation marks and not
    #    beginning/ending with a stopword as candidates.
    stoplist = stopwords.words('english')
    extractor.candidate_selection(n=3, stoplist=stoplist)

    # 4. weight the candidates using YAKE weighting scheme, a window (in
    #    words) for computing left/right contexts can be specified.
    window = 3
    use_stems = False  # use stems instead of words for weighting
    extractor.candidate_weighting(window=window,
                                  stoplist=stoplist,
                                  use_stems=use_stems)

    # 5. get the 10-highest scored candidates as keyphrases.
    #    redundant keyphrases are removed from the output using levenshtein
    #    distance and a threshold.
    threshold = 0.8
    keyphrases = extractor.get_n_best(n=10, threshold=threshold)

    return keyphrases


if __name__ == '__main__':
    text = "Once you have your skeleton in the lab and you've laid it out in anatomical position and you've recorded all the bones that are present, the first aspect of identity that you want to establish is sex. One of the reasons that you do this first is because some of the other techniques are sex dependent and we only sex the skeletal remains of adult individuals. This is because establishing sex of non adults has been shown to be unreliable. There are a number of techniques that have been developed, but when they've been applied to different populations there, their reliability is not so strong. Part of the reason for this is that sexual dimorphism, so the differences between males and females does vary slightly between different populations, so this can be confusing if you're dealing with juvenile remains. So today we're just going to focus on establishing the sex of adult skeletons. The pelvis is the most accurate part of the skeleton for sex determination and there are a number of morphological differences between males and females. Here we have a male pelvis. The differences between male and female pelvis are the most accurate way of determining sex. In individuals, you will see that the male pelvis overall is much narrower and steeper, whereas the female pelvis is much shallower and broader. If we look at this angle here beneath the pubic bone, you'll see it's much narrower in males than it is in females. There are a number of other individual features and I'll go through each of these. In turn with you for comparison here we have a female pelvis and yet, as you can see, it's much shallower and broader. The subpubic angle is much wider and the length of the pubis is much longer, and this is to increase the size of the pelvic, Inlet and pelvic outlet to facilitate childbirth. The first feature that I want to show you is the sciatic notch and you'll see here on this female pelvis that it's very wide and v-shaped. If we take a look at the male pelvis you'll see that it's deeper, narrower and more u-shaped I've included here an intermediate example. This one I've included because it's important to remember that these features exist on a sliding scale from very feminine to intermediate to very masculine. If you do have an intermediate, sciatic notch and you're, not sure whether it's male or female, it's useful to use the composite arch here you follow the edge of the sciatic notch around the superior surface of the auricular surface in males you'll see that it forms a continuous arch when you try to do this in females, you'll see that it misses the superior surface of the auricular surface and it forms almost two separate arches. This is another female pelvis and the feature that I want to show. You is called the pre auricular sulcus. That's this concavity! Underneath the auricular surface, this feature isn't present in all females, but when it is, it tends to be quite sharp and quite deep on males. You'll rarely see it, but if you do see it, it tends onde to be a very shallow. Concavity here are fragments of a female pubis and a male pubis on the female. You can see that the subpubic angle is quite wide and u-shaped on the male. You can see that it's quite narrow and v-shaped on the female. You can see that the angle extends backwards from the pubic symphysis, whereas on the male it just extends downwards. Another feature to look at is called the ventral arc on females. This is this flattened triangular area here on the anterior or front surface on males this is not present. So overall, the female pelvis is much more graceful than the male in terms of the individual features they tend to be much sharper. Another feature to look at is the length of what's called the iliopubic ramus you'll see that it's much longer if we were comparing it to the diameter of the acetabulum, the hip socket here. This is much longer. We look at the male pelvis it's much shorter and is approximately equal to the diameter of the hip socket over. All these elongated features of the female are about creating a larger space to help with childbirth. The skull is also very useful for determining sex in skeletal remains. Overall, the male skull tends to be more robust and larger than the female skull, whose features tend to be a bit more gray. So I'll go through a number of the individual features of the skull with you that are useful in terms of determining sex. So here we have a male skull and you'll notice that the eye sockets are much squarer than the female on the female. They tend to be more rounded and irregular. The rims of the orbit as well on the male's tends to be thicker and blunter, whereas on the females you can see that they're, actually quite sharp. Another key feature is known as the super orbital Ridge or the brow Ridge, as you can see it's much more defined on the male and here on the female. It's quite smooth. The centre of this Ridge is referred to as the glabella, and you can see that this is quite pronounced here, whereas on the female it tends to be much less pronounced and, as you can see on this female, it's completely absent. Here we have a male and a female skull. Viewed from the side. Now you can see that the female skull is much smaller than the male one feature you can also see is that the forehead of this female tends to be a little bit more upright, whereas the forehead of the male tends to slake slightly further backwards. When we look at the mastoid process, which is this feature here, you can see that the female mastoid process is much smaller than the male. The other feature that you can see is this Ridge here above the mastoid process in the male which is quite pronounced. This is the posterior zygomatic arch. If we look at the female, you can see that it's smooth above the mastoid process and there's no pronounced Ridge. These are the same skulls. Viewed from behind. As you can see on this male goal, we've got a very pronounced region here. This is called the nuchal crest. When we look at the female, you can see that it's very smooth here. These features are related to musculature, so they're, essentially muscle attachment points. As a result of this, you do get a great deal of variety within and between different populations. So much like the pelvis, the features that were looking at form on a sliding scale from very masculine to very feminine, and these differences will vary between different populations as well as a consequence. Sex determination in the skull tends to be less accurate than it is for the pelvis, because it is influenced by factors such as lifestyle, so diet activities and that interaction with genetics, whereas sexual dimorphism in the pelvis, relates to functional morphology linked to childbirth. Here we have two femoral and it's tempting to think that the larger one is going to be male and the smaller one is going to be female in this instance. That is the case, but it's not always. We do have large females and small males, and there is a lot of overlap between males and females within a population when we're measuring the femoral can look at the length and we can look at the diameter of the femoral head and we can look at the width of the condyles and we can look to see whether these fall into a female or a male category. But again, you must be conscious of the fact that there is a lot of overlap between males and females and I would be very cautious about assigning sex on the basis of size alone. So we've gone through the different features for establishing sex from the skeleton one of the things that I think it's really important to remember is that sexual dimorphism does vary slightly between different populations, so you will have to accommodate this difference when you're looking at your own skeletal assemblage. The other thing to remember is that sexual dimorphism is on a sliding scale from very feminine feminine intermediate: probable male. It skeletons. Don't just fall neatly into two discrete categories. So again, if you remember this, when you're establishing sex in your skeletal assemblage in the next section, we're going to focus on estimating the age at death of infant and juvenile skeletal remains, and the variety of techniques that we can use for, estimating age at death, [Music]."

    #text = "Hi there, I’m John Green, this is Crash Course: World History and today we’re going to talk about Islam, which like Christianity and Judaism grew up on the east coast of the Mediterranean but unlike Christianity and Judaism is not terribly well understood in the West. For instance, you probably know what this is and what this is, you probably don’t know what that is. Google it. Mr. Green Mr. Green why do you think people know so little about Islamic history? Did you just ask an interesting non-annoying question, me from the past? I think we don’t know about early Islamic history because we don’t learn about it, me from the past, because we don’t learn about it, because we’re taught that our history is the story of Christianity in Europe, when in fact our history is the story of people on the planet, so let’s try to learn something today. [theme music] So in less than 200 years Islam went from not existing to being the religious and political organizing principal of one of the largest empires in the world. And that story begins in the 7th century CE when the angel Gabriel appeared to Muhammad, a 40-ish guy who made his living as a caravan trader and told him to begin reciting the word of God. Initially, this freaked Muhammad out, as, you know, it would—but then his wife and a couple of other people encouraged him and slowly he came to accept the mantle as prophet. A few things to know about the world Islam entered: First, Muhammad’s society was intensely tribal. He was a member of the Quraysh tribe, living in Mecca and tribal ties were extremely important. Also, at the time, the Arabian peninsula was like this crazy religious melting pot. Like most tribal Arabs worshipped gods very similar to the Mesopotamian gods you’ll remember from episode 3. And by the time of Muhammad, cult statutes of many of those gods had been collected in his hometown of Mecca in this temple-like structure called the Kaaba. But Arabia was also a home for monotheisms like Christianity and Judaism, even a bit of Zoroastrianism. So the message that there was only god wouldn’t have been like as surprising to Muhammad as it was, for instance, to Abraham. Also, and this will become very important, the northern part of Arabia was sandwiched between the Byzantine Empire and the Persian Sassanian Empire—and you’ll remember, those guys were always fighting. They were like snowboarders and skiers, or like the Westboro Baptist Church and everyone else. At its core, Islam is what we call a radical reforming religion—just like Jesus and Moses sought to restore Abrahamic monotheism after what they perceived as straying, so too did Muhammad. Muslims believe that God sent Muhammad as the final prophet to bring people back to the one true religion, which involves the worship of, and submission to, a single and all-powerful God. The Quran also acknowledges Abraham and Moses and Jesus among others as prophets, but it’s very different from the Hebrew and Christian bibles: For one thing it’s much less narrative, but also its the written record of the revelations Muhammad received—which means its not written from the point of view of people, it is seen as the actual word of God. The Quran is a really broad-ranging text, but it returns again and again to a couple themes. One is strict monotheism and the other is the importance of taking care of those less fortunate than you. The Quran, says of the good person spends his substance—however much he himself may cherish it—upon his near of kin, and the orphans, and the needy, and the wayfarer, and the beggars, and for the freeing of human beings from bondage. These revelations also radically increased the rights of women and orphans, which was one of the reasons why Mohammad’s tribal leaders weren’t that psyched about them. To talk more about Islamic faith and practice, let’s go to the Thought Bubble. The five pillars of Islam are the basic acts considered obligatory, at least by Sunni Muslims. First is the shahada or the profession of the faith: There is no god but god and Muhammad is God’s prophet, which is sometimes translated as “There is no god but Allah and Muhammad is Allah’s prophet”, which tries to make Muslims sound other and ignores the fact that the Arabic word for god—whether you are Christian or Jewish or Muslim—is Allah. Second, salat, or ritual prayer five times a day—at dawn, noon, afternoon, sunset, and late evening—which are obligatory unless you haven’t hit puberty, are too sick, or are menstruating. Keep it PG, Thought Bubble. Third, sawm, the month-long fast during the month of Ramadan, in which Muslims do not eat or drink or smoke cigarettes during daylight hours. Since Ramadan is a lunar-calendar month, it moves around the seasons, and obviously it’s most fun during the winter, when days are shorter, and least fun during the summer, when days are both long and hot. Fourth is zakat, or almsgiving, in which non-poor Muslims are required to give a percentage of their income to the poor, and lastly hajj, the pilgrimage to Mecca that Muslims must try to fulfill at least once in their lives, provided they are healthy and have enough money. And there’s also more to understanding Islam than just knowing the Quran. Like Judaism with its Talmud, and Christianity with its lives of saints and writings of Church fathers, Islam has supplementary sacred texts, chief among which is the hadith, a collection of sayings and stories about the Prophet. Thanks Thought Bubble. Oh, it’s time for the open letter? Magic. An Open Letter to the 72 Virgins. Oh, but first let’s check what’s in the Secret Compartment. Huh, it’s Andre the Giant. Did you know that Andre the Giant died a virgin- is a fact that I made up? Dear 72 Virgins, Hey there, it’s me, John Green. Did you know that not all hadiths were created equal? Some sayings of the Prophet are really well sourced. like for instance, a good friend or a relative heard the Prophet say something and then it ended up as a hadith. But some hadiths are terribly sourced like, not to be irreverent, but some of it is like middle school gossip; like Rachel told Rebekah that her sister’s brother’s friend kissed Justin Bieber on the face. And the vast majority of Muslims don’t treat terribly sourced hadiths as scripture. And the idea that you go to heaven and get 72 virgins is not in the Quran; it’s in a terribly sourced hadith so it is my great regret to inform you, 72 Virgins, that in the eyes of almost all Muslims you do not exist. Best wishes, John Green One more thing about Islam: Like Christianity and Judaism, it has a body of law. You might have heard of it - it’s called sharia. Although we tend to think of sharia as this single set of laws that all Muslims follow, that’s ridiculous; there are numerous competing interpretations of sharia, just as there are within any legal tradition. So people who embraced this worldview were called Muslims, because they submitted to the will of God, and they became part of the umma, or community of believers. This would be a good moment for an Uma Thurman joke, but sadly she is no longer famous. I’m sorry if you’re watching this, Uma Thurman. Being part of the umma trumped all other ties, including tribal ties, which got Muhammad into some trouble and brings us, at last, back to history. So as Muhammad’s following in Mecca grew, the umma aroused the suspicion of the most powerful tribe, the Quraysh. And it didn’t matter that Muhammad himself was born into the Quraysh tribe because he wouldn’t shut up about how there was only one God, which was really bad news to the Quraysh tribe because they managed the pilgrimage trade in Mecca, and if all those gods were false, it would be a disaster economically. —although come to think of it, in the end the Meccan pilgrimage business turned out just fine. So the Quraysh forced Muhammad and his followers out of Mecca in 622 CE, and they headed to Yithrab, also known as Medina. This journey, also know as the hijra, is so important that it marks year 0 in the Islamic calendar. In Medina, Muhammad severed the religion’s ties to Judaism, turning the focus of prayer away from Jerusalem to Mecca. Also in Medina, the Islamic community started to look a lot more like a small empire than like a church. Like, Jesus never had a country to run. But Muhammad did almost from the beginning. And in addition to being an important prophet, he was a good general and in 630, the Islamic community took back Mecca. They destroyed the idols in the kabaa, and soon Islam was as powerful a political force in the region as it was a religious one. And it’s because the political and religious coexisted from the beginning, that there’s no separate tradition of civic and religious law like there is in Christianity and Judaism. very different from Judaism and even from Christianity—which you’ll remember debated very different from Judaism and even from Christianity—which you’ll remember debated for generations whether to be inclusive. —and more importantly than separating Islam from other monotheisms, that really separated Islam from the tribalism in Arabia. So then when Muhammad died in 632 CE, there wasn’t a religious vacuum left behind: Muhammad was the final prophet, the revelation of the Quran would continue to guide the umma throughout their lives. But the community did need a political leader, a caliph. And the first caliph was Abu Bakr, Muhammad’s father-in-law, who was not without his opponents: Many people wanted Ali, Muhammad’s son-in-law, to lead the community. And although he did become the fourth caliph, that initial disagreement — to radically oversimplify because we only have ten minutes — began the divide between the two of the major sects of Islam: Suuni and Shi’a. And even today, Sunnis Muslims believe Abu Bakr was rightly elected the first caliph and Shi’a Muslims believe it should’ve been Ali. To Sunnis, the first four caliphs—Abu Bakr, Umar, Uthman, and Ali— are known as the Rightly Guided Caliphs, and many of the conservative movements in the Islamic world today are all about trying to restore the Islamic world to those glory days, which—like most glory days—were not unambiguously glorious. Abu Bakr stabilized the community after Muhammad’s death, and began the process of recording the Quran in writing, And started the military campaigns against the Byzantine and Sassanian Empires that within 116 years would allow the Islamic Empire to go from this to this. His successor Umar was both an uncommonly good general and a brilliant administrator but like so many other great men, he proved terrible at avoiding assassination. Which led to the caliphate of Uthman, who standardized the Quran and continued both his predecessor’s tradition of conquest and his predecessor’s tradition of getting assassinated. Then Ali finally got his turn at caliph, but his ascension was very controversial, and it ultimately led to a civil war. Which eventually led to the emergence of Uthman’s tribe, the Umayyads, as the dynasty ruling over an ever-expanding Islamic Empire for more than a hundred years. It’s common to hear that in these early years Islam quote spread by the sword, and that’s partly true, unless you are — wait for it — the Mongols. Actually, as usual, the truth is more complicated:Many people, including the Mongols but also including lots of people in Central and East Asia, embraced Islam without any military campaigns. And in fact, the Quran says that religion must not be an act of compulsion, but this much is true: The early Islamic empire was really good at winning wars. And situated as they were between two very wealthy empires—the Byzantines and the Sassanians—there was plenty to fight for. First to fall was the Sassanians, the last non-Muslim successor to the Persian Empire. They were relatively easy pickings because they’d been fighting the Byzantines for like 300 years and were super tired. Also they’d been recently struck by plague. Plague, man, I’m telling you; It’s like the red tortoise shell of history. But in those early days they did pry away some valuable territory like Egypt and the holy land and eventually they got into Spain. Where various Muslim dynasties would entrench themselves until being expelled in 1492. But as a good as they were at making war, it’s still tempting to chalk up the Arabs’ success to, you know, the will of God. And certainly a lot of the people they conquered felt that way. Wars in this part of the world didn’t just pit people against each other, they also pitted their gods against each other. So while the Islamic Empire didn’t require its subjects to convert to Islam, their stunning successes certainly convinced a lot of people that this monotheism thing was legit. Once again, John Green proving super hip to the slang of today’s young’ns. Also, you paid lower taxes if you converted, and just as taxes on cigarettes lead to people not wanting to smoke, taxes on worshiping your idols lead to people not wanting to worship them anymore. So in a period of time that was, historically speaking, both remarkably recent and remarkably short, a small group of people from an area of the world with no natural resources managed to create one of the great empires of the world and also one of its great religions. And that very fact may be why people of Western European descent remain largely ignorant about this period. Not only were the Muslims great conquerors, they spawned an explosion of trade and learning that lasted hundreds of years. They saved many of the classical texts that form the basis of the “Western Canon” while Europe was ignoring them and they paved the way for the Renaissance. While it’s important to remember that much of the world between Spain and the Indus River wasn’t Arabized, most of it was so thoroughly Islamized that these days we can’t think of the world we now call the Middle East without thinking of it as Islamic. Perhaps the greatest testimony to Islam’s power to organize peoples lives and their communities is that, in Egypt, 5 times a day millions of people turn away from the Pyramids and toward Mecca. Egypt, birthplace to one of the longest continuous cultures the world has ever known, is now the largest Arab country in the world. Next week we’ll talk about the Dark Ages. Spoiler alert: they were darkest in the evening. Thanks for watching and we’ll see you next time. Crash Course is produced and directed by Stan Muller, our script supervisor is Danica Johnson. The show is written by my high school history teacher Raoul Meyer and myself and our graphics team is Thought Bubble. Last week’s Phrase of the Week was “They Might Be Giants”. If you want to guess this week’s Phrase of the Week or suggest future ones you can do so in Comments where you can also ask questions about today’s video that our team of historians will endeavor to answer. Thank you so much for watching and as they say in my hometown, don’t forget to be awesome."
    print(text)

    # print("GENSIM KEYWORDS: ")
    #
    # gensim_words = keywords(text)
    #
    # print(gensim_words)

    keywords_multipartite(text)


    print("PKE YAKE:")
    print(keywords_yake(text))


    print("\nPKE singleRank:")
    print(keywords_singleRank(text))


    print("\nPKE positionRank:")
    print(keywords_positionRank(text))
    print()

    print("\nPKE MULTIPARTITE")
    keys = keywords_multipartite(text)
    print(keys)

    print("BERT:")
    model = KeyBERT('distilbert-base-nli-mean-tokens')
    bert_words = model.extract_keywords(text, top_n=10)
    concepts = [k[0] for k in bert_words]
    print(concepts)

    bert_words = model.extract_keywords(text, top_n=10, use_mmr=True, diversity=0.5)
    concepts = [k[0] for k in bert_words]
    print(concepts)


    print(keywords_BERT(text))

    print("RAKE")
    Rake = RAKE.Rake(RAKE.SmartStopList())
    rake_words = Rake.run(text, maxWords=2, minFrequency=2)

    print(rake_words[0:10])

    print("MULTIPARTITE + BERT + RAKE")
    print(lemmatize(extract_keywords(text)))


