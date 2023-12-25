import json
import re
import sys

import requests

from config import CHATGPT_API_KEY


def generate_prompt(lyrics_list):
    lyrics = '\n'.join([lyric for lyric in lyrics_list if not re.search(r'[:：]', lyric)])
    content = f'以下是一首歌的歌词：{lyrics}\n' + '请你根据每句歌词含义生成10个画面，给出这几个画面的关键词，关键词用中文表示。返回结果格式示例： {"歌词1": ["关键词1", 关键词2", "关键词3"],"歌词2": ["关键词1", 关键词2", "关键词3"]}'
    try:
        prompt_dict = json.loads(chat(content))
        print(prompt_dict)
        return prompt_dict
    except Exception as e:
        print(f"ChatGPT API异常：{e}")


def chat(content):
    url = "https://api.chatanywhere.com.cn/v1/chat/completions"
    payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    })
    headers = {
        'Authorization': f'Bearer {CHATGPT_API_KEY}',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return data['choices'][0]['message']['content']
    else:
        print(f"ChatGPT API异常:\n{response.text}")
        sys.exit()
