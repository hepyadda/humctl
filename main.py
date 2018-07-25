#!/usr/bin/python
from __future__ import absolute_import, print_function
import signal
import sys
from datetime import datetime
from time import sleep
import Adafruit_DHT
import RPi.GPIO as GPIO
import tweepy

def signal_handler(sig, frame):
    GPIO.output(3, GPIO.HIGH)
    GPIO.output(5, GPIO.HIGH)
    GPIO.cleanup()
    f.close()
    sys.exit(0)
    
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

log      = '/root/script/humctl/reading.txt'
sensor   = Adafruit_DHT.AM2302
pin      = 4
temp_min = 21.25
temp_max = 21.75
sleep_t  = 60
consumer_key = "yyz"
consumer_secret = "yyz"
access_token = "yyz"
access_token_secret = "yyz"
tweet_ctl = 10

def main():
    init_sensor()
    f = open(log,'a')
    tweet_cnt = 0
    send_twitter(0, 0, "starting")
    while 1:
        tweet_cnt = tweet_cnt + 1
        rh, temp = read_sensor()
        while temp > temp_max:
            f.write("on," + str(temp) + "," + str(rh) + "," + str(datetime.now()) + "\n")
            f.flush()
            cooling_on()
            if tweet_cnt >= tweet_ctl:
                send_twitter(temp, rh, "on")
                tweet_cnt = 0
            sleep(sleep_t)
            tweet_cnt = tweet_cnt + 1
            rh, temp = read_sensor()
        cooling_off()
        f.write("off," + str(temp) + "," + str(rh) + "," + str(datetime.now()) + "\n")        
        f.flush()
        if tweet_cnt >= tweet_ctl:
            send_twitter(temp, rh, "off")
            tweet_cnt = 0
        sleep(sleep_t)
    f.close()
        
def init_sensor():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(3, GPIO.OUT)
    GPIO.setup(5, GPIO.OUT)
    # start off
    GPIO.output(3, GPIO.HIGH)
    GPIO.output(5, GPIO.HIGH)    
    return

def cooling_on():
    GPIO.output(3, GPIO.LOW)
    GPIO.output(5, GPIO.LOW)
    return

def cooling_off():
    GPIO.output(3, GPIO.HIGH)
    GPIO.output(5, GPIO.HIGH)
    return

def read_sensor():
    rh, temp = Adafruit_DHT.read_retry(sensor, pin)
    return rh, temp

def read_twitter(temp, rh):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api  = tweepy.API(auth)
    text = api.direct_messages()[0].text
    if text == 'get_status':
        api.send_direct_message('@yyz', "temp: " + str(temp) + " rh: " + str(rh) )
    
def send_twitter(temp, rh, status):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    api.send_direct_message(user='@yyz', text="temp: " + str(temp) + " rh: "  + str(rh) + " status: " + status)
    
if __name__ == "__main__":
    main()
