import oauth2 as oauth
import urllib2 as urllib
import json
import re
import string
import operator
import sys
import sched, time
import datetime
from datetime import datetime
##import nltk
##from nltk.corpus import stopwords

# See assignment1.html instructions or README for how to get these credentials

api_key = "miQnY8GxsL2moScOsDKGSj7Ft"
api_secret = "QwY1bcDsuLrcIsU2Yze1VN1MgQz3HYkMkwdH6D1QjuR7zBen1g"
access_token_key = "807266716879306752-wsiIuSZQze5wmlMO3bGgpoCUCxiulBR"
access_token_secret = "df2iPMxlQuHbmcG5XaJl9MhdT9dhMbRHULccxBR1eLN3P"

_debug = 0

oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=api_key, secret=api_secret)

signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

http_method = "GET"


http_handler  = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)

'''
Construct, sign, and open a twitter request
using the hard-coded credentials above.
'''
def twitterreq(url, method, parameters):
  req = oauth.Request.from_consumer_and_token(oauth_consumer,
                                             token=oauth_token,
                                             http_method=http_method,
                                             http_url=url,
                                             parameters=parameters)

  req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

  headers = req.to_header()

  if http_method == "POST":
    encoded_post_data = req.to_postdata()
  else:
    encoded_post_data = None
    url = req.to_url()

  opener = urllib.OpenerDirector()
  opener.add_handler(http_handler)
  opener.add_handler(https_handler)

  response = opener.open(url, encoded_post_data)

  return response

def create_dutch_dictionary():
    file = open('Dutch_Words.txt')
    dictionary = {}
    for line in file:
        line_t = line.strip()
        lista = line_t.split('\t')
        if lista[0] in dictionary:
            print "No deberia haber palabras repetidas"

        dictionary[lista[0]] = []
        dictionary[lista[0]] = float(lista[2]) - float(4) # 4 is neutral

    return dictionary

def words_counter(tweet,time, dictionary):

    texto = []
    texto = tweet['text']
    if tweet['entities']['hashtags']:
        hashtags = tweet['entities']['hashtags']
        for hashtag in hashtags:
            texto = texto + ' ' + hashtag['text'].encode('ascii','ignore')

    replace_punctuation = []
    replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
    texto = texto.encode('ascii','ignore')
    texto = texto.translate(replace_punctuation)
    texto = texto.lower()

    texto_partido = texto.split()
    tweets_words = []
    aa = []
    aa = time[1]+' '+time[2] + ' ' + time[5] + ' ' + time[3]
    tiempo_t = []
    tiempo_t = datetime.strptime(aa, '%b %d %Y %H:%M:%S')

    sentiment = 0
    chars_to_remove = ['.', '#', '!','?', '/']
    for word in texto_partido:
        if word:
            #word = word.replace('#','')
            word = word.translate(None, ''.join(chars_to_remove))
            c = 0
            for i, _ in enumerate(tweets_words):
                if word in tweets_words[i]:
                    c = 1
            if c == 0:
                tweets_words.append([tiempo_t, word])

            if word in dictionary:
                sentiment += dictionary[word]

    user_id = tweet['user']['id']
    s_tuple = []
    s_tuple = tiempo_t, user_id, sentiment, texto_partido

    #return tweets_words, s_tuple
    return s_tuple

def analyse_response(response):

    ## Load dictionary
    dictionary = {}
    dictionary = create_dutch_dictionary()

    s_tuple = []

    for line in response:
        line2 = line.strip()
        tweet = []
        tweet = json.loads(line2)
        # time
        time = []
        time = tweet.get('created_at')

        if 'lang' in tweet:
            if tweet['lang'] == 'nl' and time is not None:
                ##print tweet['lang']
                time = time.split()
                #if time[0] != 'Fri' or time[1] != 'Feb' or time[2] != '17':
                #    print "Wrong date!"
                #e#lse:
                try:
                    if len(tweet.get('text')) > 0 or len((tweet.get('entities')).get('hashtags')) > 0:
                        #tweets_words = []
                        s_tuple = words_counter(tweet,time,dictionary)
                        #with open('output_dutch.txt','a') as f:
                                                    #    for i, _ in enumerate(tweets_words):
                            #        f.write("%s\t %s\t\n" % (tweets_words[i][0], tweets_words[i][1]))
                        with open('sentiment_output_dutch_stream.txt','a') as f:
                            #    if s_tuple[1] != 0:
                            f.write("%s\t %d\t %f\t" % (s_tuple[0], s_tuple[1],s_tuple[2]))
                            for item in s_tuple[3]:
                                f.write("%r\t" % item)
                            f.write("%s\t\n" % "END")
                        with open('raw_data_dutch_stream.txt', 'a') as f:
                            f.write("%s\n" % line2)
                except:
                    pass

def fetchsamples():
    url = "https://stream.twitter.com/1.1/statuses/sample.json"
    ##url = "https://stream.twitter.com/1.1/statuses/filter.json?language=en"
    parameters = []
    response = twitterreq(url, "GET", parameters)
    analyse_response(response)

if __name__ == '__main__':
    fetchsamples()
