#__author__      ="Rodolfo Tolloi"
#__subject__     ="Nastro Pipeline"
#__tags__        ="Bioinformatics, Nanopore, Dorado"
#__copyright__   ="Copyright 2021, AREA SCIENCE PARK - RIT"
#__credits__     =
#__license__     ="Apache License 2.0"
#__version__     =
#__maintainer__  =
#__status__      ="Development"

import os
import requests

def telegram_send_file(path_to_file, caption) :
    token = str(os.environ.get('BC_TOKEN_BOT'))
    chat_id = "-4523992444"
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    files = {'document': open(path_to_file, 'rb')}
    data = {'chat_id': chat_id,'caption': caption}
    results = requests.post(url, files=files, data=data)

    if results.status_code == 200:
        #print('Message sent successfully!')
        error_message = 'Message sent successfully!'
    else:
        error_message = f'Failed to send message. Status code: {results.status_code}, Response: {results.text}'
        print(error_message)        

def telegram_send_message(message) :
    token = str(os.environ.get('BC_TOKEN_BOT'))
    chat_id = "-4523992444"
    url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + message + "&parse_mode=MarkdownV2"
    results = requests.get(url_req)
    
    if results.status_code == 200:
        #print('Message sent successfully!')
        error_message = 'Message sent successfully!'
    else:
        error_message = f'Failed to send message. Status code: {results.status_code}, Response: {results.text}'
        print(error_message)   

def telegram_send_bar(message):
    token = str(os.environ.get('BC_TOKEN_BOT'))
    chat_id = "-4523992444"
    
    # Escape special characters for Telegram MarkdownV2
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        message = message.replace(char, '\\' + char)
    
    url_req = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}&parse_mode=MarkdownV2"
    results = requests.get(url_req)

    if results.status_code == 200:
        #print('Message sent successfully!')
        error_message = 'Message sent successfully!'
    else:
        error_message = f'Failed to send message. Status code: {results.status_code}, Response: {results.text}'
        print(error_message)       

class Telegram_bar:
    def __init__(self):
        self.last_message_id = None  # Store message ID per instance

    def telegram_send_bar(self, message):
            token = str(os.environ.get('BC_TOKEN_BOT'))
            chat_id = "-4523992444"
            
            # Escape special characters for Telegram MarkdownV2
            escape_chars = ['_', '*', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            for char in escape_chars:
                message = message.replace(char, '\\' + char)
            
            if self.last_message_id is None:
                # Send a new message
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                data = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'MarkdownV2'
                }
                response = requests.post(url, data=data)
                
                if response.status_code == 200:
                    self.last_message_id = response.json()['result']['message_id']
                else:
                    print(f'Failed to send message. Status code: {response.status_code}, Response: {response.text}')
            else:
                # Try to update the existing message
                url = f"https://api.telegram.org/bot{token}/editMessageText"
                data = {
                    'chat_id': chat_id,
                    'message_id': self.last_message_id,
                    'text': message,
                    'parse_mode': 'MarkdownV2'
                }
                response = requests.post(url, data=data)
                
                if response.status_code != 200:
                    # Failed to update the message, send a new one
                    print(f'Failed to update message. Status code: {response.status_code}, Response: {response.text}')
                    self.last_message_id = None  # Reset message ID to send a new message
                    
                    # Send a new message
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    data = {
                        'chat_id': chat_id,
                        'text': message,
                        'parse_mode': 'MarkdownV2'
                    }
                    response = requests.post(url, data=data)
                    
                    if response.status_code == 200:
                        self.last_message_id = response.json()['result']['message_id']
                    else:
                        print(f'Failed to send new message after update failure. Status code: {response.status_code}, Response: {response.text}')