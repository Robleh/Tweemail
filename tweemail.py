#!/user/bin/env python

'''A Twitter Search API Email Harvester'''

import os
import tweepy
import socks, socket
import urllib2
import re
import MySQLdb
import argparse

email_regex = "[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}" 

#Command line parser
parser = argparse.ArgumentParser()
parser.add_argument('-q', '--query', action='store', dest='query',
                    default=False, required=True,
                    help="Twitter Search API query")
parser.add_argument('-t', '--tor', action='store_true', dest='tor',
                    default=False, help="Use TOR Browser as proxy.")
parser.add_argument('-m', '--mysql', action='store_true', dest='mysql',
                    default=False, help="Store results in MySQL database.")
flags = parser.parse_args()

'''To store results in MySQL database enter the credentials below.
   Eventually this will be dynamic but for now it is hard-coded to store
   tweets which match our criteria into a table named test.
'''

#MySQL command check for test table if it doesn't exist create it
check_table = '''CREATE TABLE IF NOT EXISTS test (
                 id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                 time DATETIME,
                 username VARCHAR(16),
                 name VARCHAR(50),
                 email VARCHAR(50),
                 followers INT(11),
                 following INT(11),
                 verified VARCHAR(1),
                 tweet VARCHAR(255),
                 bio VARCHAR(255),
                 location VARCHAR(140))
                 CHARACTER SET utf8mb4 COLLATE utf8mb4_bin''' 

#Enter MySQL credentials below
if flags.mysql is True:
    try:
        db = MySQLdb.connect(host='',
                             user='',
                             passwd='',
                             db='',
                             use_unicode=True,
                             charset='utf8mb4') #utf8mb4 allows emojis
        cur = db.cursor()
        cur.execute(check_table)
    except:
        print "\n" + "[x] Could not connect to MySQL database." + "\n"
        os._exit(1)

'''Next, obsfucate the connection origin by using TOR Browser as proxy.
   TOR Browser has to be running on default port 9150. Again this will be made
   dynamic in the future. Pointless when using API keys from a known account.
   Needs more testing.
''' 

#Proxy through TOR browser default port. Urllib2 necessary for check?
if flags.tor is True:
    try:    
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9150, True)
        socket.socket = socks.socksocket
        urllib2.urlopen("http://www.twitter.com")
    except:
        print "\n" + "[x] Could not connect to TOR Browser." + "\n"
        os._exit(1)

'''API keys from a Twitter account are required. App-only will suffice.'''

#Enter API keys below    
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api_auth = tweepy.API(auth)

'''This is where the data gets processed. Maybe better alternatives?'''
	
class TweetDbObject(object):
    
    found_email = True
    duplicate = False
    
    def __init__(self, username, name, time, followers,
                 following, verified, tweet, tweet_id, bio, location):
        self.time = time
        self.username = username
        self.name = name
        self.followers = followers
        self.following = following
        self.verified = verified
        self.tweet = tweet
        self.tweet_id = tweet_id
        self.bio = bio
        self.location = location

    def email_check(self):
        if re.search(email_regex, self.tweet) is not None:
            self.email = re.search(email_regex, self.tweet).group(0)
        elif re.search(email_regex, self.bio) is not None:
            self.email = re.search(email_regex, self.bio).group(0)
        else:
            self.found_email = False           
    
    #API is reverse chronological. Expermient with [::-1]
    def duplicate_check(self):
        if self.found_email is True:
            if cur.execute('''SELECT email FROM test
               WHERE email = "%s" ''' % self.email) != 0:
                self.duplicate = True
    
    def print_tweet(self):
        if self.found_email is True:
            print "\n"
            print self.time
            print "@" + self.username
            print "Name:", self.name
            print "Email Contact:", self.email
            print "Followers:", self.followers
            print "Verified User:", self.verified
            print "Says:", self.tweet
    
    def store_tweet(self):
        if self.found_email is True and self.duplicate is False:    
            cur.execute("""INSERT INTO test
                        (time, username, name, email,
                        followers, following, verified,
                        tweet, bio, location)
	                VALUES
                        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""" , (
                        self.time, self.username, self.name,
                        self.email, self.followers, self.following,
                        self.verified, self.tweet, self.bio, self.location))


#Search, check, print, store. Better way?
def search(api):
    for tweet in api.search(q=flags.query, result_type='recent', count=100):
        if hasattr(tweet, 'retweeted_status') is False:
            tweet_object = TweetDbObject(tweet.user.screen_name,
                                         tweet.user.name,
                                         tweet.created_at,
                                         tweet.user.followers_count,
                                         tweet.user.following,
                                         tweet.user.verified,
                                         tweet.text,
                                         tweet.id,
                                         tweet.user.description,
                                         tweet.user.location)
            tweet_object.email_check()
            tweet_object.print_tweet()
            if flags.mysql is True:
                tweet_object.duplicate_check()
                tweet_object.store_tweet()

def main():
    search(api_auth)
    if flags.mysql is True:
        db.commit()
        db.close()
    	
if __name__ == "__main__":
    main()
