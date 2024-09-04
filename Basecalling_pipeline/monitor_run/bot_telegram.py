import os
import requests

def telegram_send_file(path_to_file, caption) :
    token = str(os.environ.get('BC_TOKEN_BOT'))
    chat_id = "-4531622913"
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
    chat_id = "-4531622913"
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
    chat_id = "-4531622913"
    
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

