#!/usr/bin/env python
#_*_ coding: utf-8 _*_
import os
import sys
import json
from random import randint
import requests
from flask import Flask, request
import apiai

app = Flask(__name__)

CLIENT_ACCESS_TOKEN = '13563fb8a99b41c2a0d5d28f6425c0eb'


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    #message_text = if messaging_event["message"]["text"].encode('UTF8') else ''  # the message's text
                    if "text" in messaging_event["message"].keys():
                        if messaging_event["message"]["text"].encode('UTF8') in ['天氣','幹','靠','你老師']:
                            ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
                            req = ai.text_request()
                            req.resetContexts = False
                            req.lang = 'zh-TW'
                            req.query=messaging_event["message"]["text"].encode('UTF8')
                            response = req.getresponse()
                            print '@@@@',response.read(),type(response.read())
                            nr = response.read() #json.loads(response.read())#.decode('utf8'))
                            print '~~',nr
                            answers = 'aa'#nr["result"]["fulfillment"]["messages"][0]["speech"]
                            send_message(sender_id, answers)

                        else:
                            print 'message_text',messaging_event["message"]["text"].encode('UTF8')
                            print 'senderid',sender_id
                            print 'recipient_id',recipient_id
                            answers=['haha','朕乏了','快宣太醫','大膽','Hi 我是天皇','怎麼了嗎','哈哈哈','比較遠的廁所在哪','你知道嗎東湖的水真的很涼','我都8 9點才下班QQ',\
                                     '我想一下','該怎麼說好呢','喂','嘎比舉','天氣好心情也會好 不是嗎','等一下我先去泡個茶','想喝茶嗎','.....什麼鬼拉XD','也不是不可以拉','我真是榮幸= ='\
                                     '誒 別鬧啊','我看得五味雜陳','手下留琴','饒了我吧','什麼巫術','用windows系統做開發好難','不要把我玩壞>///<','好茶好茶','有什麼建議嗎','我會幫你跟小編說']
                            a=randint(0,len(answers)-1)
                            send_message(sender_id, answers[a])
                            return "ok", 200

                    elif "attachments" in messaging_event["message"].keys():
                        if messaging_event["message"]["attachments"][0]['type']=='image':
                            if 'sticker_id' in messaging_event["message"]["attachments"][0]['payload']:
                                print 'senderid',sender_id
                                print 'recipient_id',recipient_id
                                send_message(sender_id, '不要用貼圖敷衍我')
                                return "ok", 200
                            else:
                                print 'senderid',sender_id
                                print 'recipient_id',recipient_id
                                answers=['好圖好圖','這照片是在哪裡拍的','這是誰啊']
                                a=randint(0,len(answers)-1)
                                send_message(sender_id, answers[a])
                                return "ok", 200

                        elif messaging_event["message"]["attachments"][0]['type']=='location':
                            longitude=messaging_event["message"]["attachments"][0]['payload']['coordinates']['long']
                            latitude=messaging_event["message"]["attachments"][0]['payload']['coordinates']['lat']
                            print 'longitude',longitude
                            print 'latitude',latitude
                            data={}
                            data['longitude']=longitude
                            data['latitude']=latitude
                            #headers = {"Content-Type": "application/json"}
                            r = requests.post("http://139.162.43.239/store/storeNearby", data=data)#headers=headers,
                            print 'r',json.loads(r.text)
                            storename = json.loads(r.text)['top10'][0].encode('UTF8')
                            print 'senderid',sender_id
                            print 'recipient_id',recipient_id
                            #send_message(sender_id, 'done')
                            print 'storename',storename
                            send_message(sender_id, storename)
                            return "ok", 200

                        elif messaging_event["message"]["attachments"][0]['payload']==None and 'title' in messaging_event["message"]["attachments"][0]:
                            if messaging_event["message"]["attachments"][0]['title']=='Location sharing ended':
                                send_message(sender_id, 'Location Sharing ended')
                                return "ok", 200
                            else:
                                send_message(sender_id, 'in else')


                        # elif 'coordinates' in messaging_event["message"]["attachments"][0]['payload']:
                        #     longitude=messaging_event["message"]["attachments"][0]['payload']['coordinates']['long']
                        #     latitude=messaging_event["message"]["attachments"][0]['payload']['coordinates']['lat']
                        #     print 'longitude',longitude
                        #     print 'latitude',latitude
                        #     data={}
                        #     data['longitude']=longitude
                        #     data['latitude']=latitude
                        #     #headers = {"Content-Type": "application/json"}
                        #     r = requests.post("http://139.162.43.239/store/storeNearby", data=data)#headers=headers,
                        #     print 'r',json.loads(r.text)
                        #     storename = json.loads(r.text)['top10'][0].encode('UTF8')
                        #     print 'senderid',sender_id
                        #     print 'recipient_id',recipient_id
                        #     #send_message(sender_id, 'done')
                        #     print 'storename',storename
                        #     send_message(sender_id, storename)
                        #     return "ok", 200

                        # elif 'sticker_id' in messaging_event["message"]["attachments"][0]['payload']:
                        #     print 'senderid',sender_id
                        #     print 'recipient_id',recipient_id
                        #     send_message(sender_id, '不要傳貼圖敷衍我')
                        #     return "ok", 200

                        else:
                            send_message(sender_id, 'in else')

                    else:
                        print 'no text'
                        send_message(sender_id, 'in else')
                    #print 'messaging_event["message"]',messaging_event["message"]

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
