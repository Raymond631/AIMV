import os
import tempfile
import threading

from flask import Flask, request, jsonify, send_from_directory

from draw import generate_image
from email_notice import send_email
from prompt import generate_prompt
from song import getSongId, getLyrics, getSong, parseLyrics
from video import addLyrics, compositeVideo

app = Flask(__name__)


@app.route('/generate', methods=['POST'])
def draw():
    data = request.get_json()
    song = data['song']
    style = data['style']
    size = data['size']
    email = data['email']

    thread = threading.Thread(target=service, args=(song, style, size, email))
    thread.start()

    return jsonify({
        'code': 200,
        'msg': '任务提交成功，请等待邮件通知'
    })


@app.route('/static/video/<path:filename>')
def serve_video(filename):
    video_dir = os.path.abspath('../resource/video/')
    return send_from_directory(video_dir, filename)


def service(song, style, size, email):
    temp_dir_path = os.path.abspath('../resource/temp')
    os.makedirs(temp_dir_path, exist_ok=True)
    temp_dir = tempfile.mkdtemp(prefix='temp_', dir=temp_dir_path)
    print(f'随机目录已创建：{temp_dir}')

    # 调用网易云API
    song_id, song_name = getSongId(song)
    getSong(song_id, song_name, temp_dir)
    lyrics = getLyrics(song_id)
    # 解析歌词
    lyrics_list, durations_list = parseLyrics(lyrics)
    # 调用人工智能API
    prompt_dict = generate_prompt(lyrics_list)
    lrc_img_dict = generate_image(prompt_dict, style, size, temp_dir)
    # 合成视频
    addLyrics(lyrics_list, lrc_img_dict, temp_dir)
    compositeVideo(song_name, durations_list, temp_dir)
    # 邮件通知
    send_email(f"http://localhost:5000/static/video/{song_name}.mp4", email)

    # shutil.rmtree(temp_dir)
    # print(f'随机目录已删除：{temp_dir}')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
