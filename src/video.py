import random
import uuid

from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import *


def find_optimal_font_size(draw, text, font_path, target_width, max_height, initial_font_size=1):
    # 采用二分查找算法优化字体大小
    lower_size = initial_font_size
    upper_size = 2 * initial_font_size

    while draw.textbbox((0, 0), text, font=ImageFont.truetype(font_path, upper_size))[2] < target_width:
        lower_size = upper_size
        upper_size *= 2

    while upper_size - lower_size > 1:
        mid_size = (lower_size + upper_size) // 2
        if draw.textbbox((0, 0), text, font=ImageFont.truetype(font_path, mid_size))[2] < target_width:
            lower_size = mid_size
        else:
            upper_size = mid_size

    text_width, text_height = draw.textsize(text, font=ImageFont.truetype(font_path, lower_size))
    # 如果超高，则等比缩放
    return lower_size if text_height < max_height else int(lower_size * (max_height / text_height))


def add_lyrics_to_image(image_path, output_path, lyrics, font_path=os.path.abspath("../resource/font/msyh.ttc")):
    # 打开图片
    img = Image.open(image_path)

    # 创建Draw对象
    draw = ImageDraw.Draw(img)

    # 设置目标宽度、最大高度
    target_width = img.size[0] * 0.8
    max_height = img.size[1] * 0.1

    # 选择字体大小
    font_size = find_optimal_font_size(draw, lyrics, font_path, target_width, max_height)

    # 选择字体
    font = ImageFont.truetype(font_path, font_size)

    # 计算文字位置
    text_width, text_height = draw.textbbox((0, 0), lyrics, font=font)[2:]
    text_x = (img.width - text_width) / 2
    text_y = img.height - text_height - 30  # 调整底部边距

    # 绘制黑色边缘文字
    draw.text((text_x - 2, text_y - 2), lyrics, font=font, fill="black")
    draw.text((text_x + 2, text_y - 2), lyrics, font=font, fill="black")
    draw.text((text_x - 2, text_y + 2), lyrics, font=font, fill="black")
    draw.text((text_x + 2, text_y + 2), lyrics, font=font, fill="black")
    # 绘制白色文字
    draw.text((text_x, text_y), lyrics, font=font, fill="white")

    # 保存输出图片
    img.save(output_path)


def addLyrics(lyrics_list, lrc_img_dict, temp_dir):
    os.makedirs(f"{temp_dir}/img_lrc")
    ids = list(lrc_img_dict.values())
    for lrc_img_id, lyric in enumerate(lyrics_list):
        if lyric not in lrc_img_dict:
            # 非歌词、未生图歌词，用随机图片
            add_lyrics_to_image(f"{temp_dir}/image/{random.choice(ids)}.png", f"{temp_dir}/img_lrc/{lrc_img_id + 1}.png", lyric)
        else:
            # 生图歌词，用对应图片
            add_lyrics_to_image(f"{temp_dir}/image/{lrc_img_dict[lyric]}.png", f"{temp_dir}/img_lrc/{lrc_img_id + 1}.png", lyric)
    print("图片添加歌词成功")


def compositeVideo(song_name, durations, temp_dir):
    # 设置图片路径
    image_folder_path = f"{temp_dir}/img_lrc/"
    image_files = [f for f in os.listdir(image_folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    image_files = sorted(image_files, key=lambda x: int(x.split('.')[0]))  # 将文件名转换为数字并按数字大小排序
    image_paths = [os.path.join(image_folder_path, img) for img in image_files]

    # 拼接图片序列
    image_clips = []
    for i, img_path in enumerate(image_paths):
        img_clip = ImageClip(img_path).set_duration(durations[i] / 1000)
        image_clips.append(img_clip)
    video_clip = concatenate_videoclips(image_clips, method="compose")

    # 添加背景音乐
    audio_path = f'{temp_dir}/song/{song_name}.mp3'
    audio_clip = AudioFileClip(audio_path)
    video_clip = video_clip.set_audio(audio_clip)

    # 输出视频文件
    video_dir_path = os.path.abspath('../resource/video')
    os.makedirs(video_dir_path, exist_ok=True)
    video_id = uuid.uuid4()
    output_path = f'{video_dir_path}/{video_id}.mp4'
    video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=24)
    print("MV合成成功")
    return video_id
