import os
import re

import requests


def getSongId(keyword):
    url = f'http://music.163.com/api/search/get/web?type=1&s={keyword}&limit=1'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()['result']['songs'][0]
        print("查询成功")
        return data["id"], data["name"]
    else:
        print("查询失败")


def getSong(song_id, song_name, temp_dir):
    url = f'http://music.163.com/song/media/outer/url?id={song_id}.mp3'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    audio_response = requests.get(url, headers=headers)

    # 保存音频文件
    if audio_response.status_code == 200:
        os.makedirs(f"{temp_dir}/song")
        with open(f"{temp_dir}/song/{song_name}.mp3", 'wb') as f:
            f.write(audio_response.content)
        print(f"歌曲下载成功")
    else:
        print("歌曲下载失败")


def getLyrics(song_id):
    url = f'http://music.163.com/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        lyric = data['lrc']['lyric']
        print("歌词下载成功")
        return lyric
    else:
        print("歌词下载失败")


def parseLyrics(lyrics):
    # 定义正则表达式解析歌词
    pattern = re.compile(r'\[(\d+:\d+\.\d+)\](.+)')
    matches = pattern.findall(lyrics)
    # 分别存储歌词和对应的时长
    lyrics_list = []
    durations_list = []
    # 计算相邻歌词的时长
    for i in range(len(matches) - 1):
        timestamp1, lyric1 = matches[i]
        timestamp2, lyric2 = matches[i + 1]
        # 转换时间戳为毫秒
        time1 = int(timestamp1.split(':')[0]) * 60 * 1000 + float(timestamp1.split(':')[1]) * 1000
        time2 = int(timestamp2.split(':')[0]) * 60 * 1000 + float(timestamp2.split(':')[1]) * 1000
        # 计算相邻歌词的时长
        duration = int(time2 - time1)
        lyrics_list.append(lyric1.strip())
        durations_list.append(duration)
    # 添加最后一句歌词及其时长为1000毫秒
    last_lyric = matches[-1][1]
    lyrics_list.append(last_lyric.strip())
    durations_list.append(1000)
    print("歌词解析成功")
    return lyrics_list, durations_list
