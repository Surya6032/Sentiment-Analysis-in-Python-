from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener


from tweepy import OAuthHandler #Responsible for authenticating all the credentials we store in other file associated with twitter app
from tweepy import Stream

from textblob import TextBlob


import twitter_credentials
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt


### TWITTER CLIENT ####
print("                           SENTIMENT ANALYSISm       ")
class TwitterClient():
	def __init__(self,twitter_user=None):
		self.auth=TwitterAuthenticator().authenticate_twitter_app()
		self.twitter_client=API(self.auth)

		self.twitter_user = twitter_user
	def get_twitter_client_api(self):
		return self.twitter_client
	def get_user_timeline_tweets(self,num_tweets):
		tweets=[]
		for tweet in Cursor(self.twitter_client.user_timeline,id=self.twitter_user).items(num_tweets):
			tweets.append(tweet)
		return tweets
	def get_friend_list(self,num_friends):
		friend_list=[]
		for friend in Cursor(self.twitter_client.friends,id=self.twitter_user).items(num_friends):
			friend_list.append(friend)
		return friend_list

	def get_home_timeline_tweets(self,num_tweets):
		home_timeline_tweets=[]
		for tweet in Cursor(self.twitter_client.home_timeline,id=self.twitter_user).items(num_tweets):
			home_timeline_tweets.append(tweet)
		return home_timeline_tweets
class TwitterAuthenticator():
	def authenticate_twitter_app(self):
		auth = OAuthHandler(twitter_credentials.CONSUMER_KEY,twitter_credentials.CONSUMER_SECRET)               #authenticating the credentials
		auth.set_access_token(twitter_credentials.ACCESS_TOKEN,twitter_credentials.ACCESS_TOKEN_SECRET)	
		return auth


### Twitter Streamer ####
class TwitterStreamer():
	"""	
	Class for streaming and processinhg live tweets
	"""
	def __init__(self):
		self.twitter_authenticator=TwitterAuthenticator()
	def stream_tweets(self,fetched_tweets_filename,hash_tag_list):
		listener=TwitterListener(fetched_tweets_filename)
		auth=self.twitter_authenticator.authenticate_twitter_app()
		
		stream = Stream(auth, listener)

		#This line filters Twitter 
		stream.filter(track=hash_tag_list)	

#### Twitter Stream Listener
class TwitterListener(StreamListener): 			#StreamListener provides method that we can directly override 
	"""
   This a basic listener class that just prints received tweets to stdout
   """
	def __init__(self,fetched_tweets_filename):
		self.fetched_tweets_filename=fetched_tweets_filename
	def on_data(self,data):				#take in the data that is streamed from the stream listener i.e listening for tweets
		try:
			print(data)
			with open(self.fetched_tweets_filename,'a') as tf:
				tf.write(data)
			return True
		except BaseException as e:
			print("Error on data: %s" % str(e))
			return True
	def on_error(self,status):			#if error occurs what we will do
		#Returning False on data methods in case you violate twitter guidelines of accessing data(in case rate limits occurs)
		if status==420:
			return False
		print(status)

class TweetAnalyzer():
	"""
	Functionality for analyzing and categorizing content from tweets.
	"""
	def clean_tweet(self, tweet):
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
	def analyze_sentiment(self, tweet):
		analysis=TextBlob(self.clean_tweet(tweet))

		if analysis.sentiment.polarity > 0:				 #Will use sentiment analysis engine and polarity tells us weather the tweet is positivie or not in nature
			return 1									 #positive sentiment
		elif analysis.sentiment.polarity == 0:
			return 0								    #0 is neutral
		else:		
			return -1            						#negative sentiment 	 
	
	def tweets_to_data_frame(self,tweets):
		df = pd.DataFrame(data=[tweet.text for tweet in tweets],columns =['tweets'])
		df['id'] = np.array([tweet.id for tweet in tweets])    #Looping through all the tweets and getting their id's
		df['len']= np.array([len(tweet.text)for tweet in tweets]) 
		df['date']=np.array([tweet.created_at for tweet in tweets])
		df['source']=np.array([tweet.source for tweet in tweets])
		df['likes']=np.array([tweet.favorite_count for tweet in tweets])   
		df['retweets']=np.array([tweet.retweet_count for tweet in tweets]) 
		return df

if __name__=="__main__":
	twitter_client=TwitterClient()
	tweet_analyzer=TweetAnalyzer()
	api= twitter_client.get_twitter_client_api()
	name=input("Enter user ID:")
	tweets = api.user_timeline(screen_name=name,count=200)       #user_timeline is provided by the twitter client API
	#print(tweets[0].retweet_count)
	#df = tweet_analyzer.tweets_to_data_frame(tweets)
	#print(dir(tweets[0]))
	#print(df.head(10))
	df = tweet_analyzer.tweets_to_data_frame(tweets)
	df['sentiment']=np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']]) 
	Number=int(input("Enter how many tweets you wanna analyze:"))
	print(df.head(Number))
	#print(df.head(10))
	#Get average length over all tweets.
	#print(np.mean(df['len']))
	#Get the number of likes for the most liked tweet
	#print(np.max(df['likes']))
	#Get the number of retweets for the most retweeted tweet
	#print(np.max(df['retweets']))

	#Time Series
	#time_likes = pd.Series(data=df['likes'].values, index= df['date'])
	#time_likes.plot(figsize=(16,4), color='r')
	#plt.show()

	#time_retweets = pd.Series(data=df['retweets'].values, index= df['date'])
	#time_retweets.plot(figsize=(16,4), color='r')
	#plt.show()
	#time_likes = pd.Series(data=df['likes'].values, index= df['date'])
	#time_likes.plot(figsize=(16,4), label="likes",legend = True)

	#time_retweets = pd.Series(data=df['retweets'].values, index= df['date'])
	#time_retweets.plot(figsize=(16,4), label='retweets',legend=True)

	#plt.show()

