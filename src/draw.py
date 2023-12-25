import json
import os

import requests
from tencentcloud.aiart.v20221229 import aiart_client, models
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

from config import TENCENT_SECRET_ID, TENCENT_SECRET_KEY


def generate_image(prompt_dict, style, size, temp_dir):
    # 限制图片数量
    if len(prompt_dict) > 15:
        prompt_dict = {k: prompt_dict[k] for k in list(prompt_dict)[:15]}
    os.makedirs(f"{temp_dir}/image")
    img_id = 1
    lrc_img_dict = {}
    for lrc, keyword_list in prompt_dict.items():
        drawPic(','.join(keyword_list), style, size, temp_dir, img_id)
        print(f"image {img_id}生成成功")
        lrc_img_dict[lrc] = img_id
        img_id += 1
    print(lrc_img_dict)
    return lrc_img_dict


def drawPic(prompt, style, size, temp_dir, img_id):
    try:
        cred = credential.Credential(TENCENT_SECRET_ID, TENCENT_SECRET_KEY)
        client = aiart_client.AiartClient(cred, "ap-guangzhou")
        req = models.TextToImageRequest()
        params = {
            "Action": "TextToImage",
            "Version": "2022-12-29",
            "Region": "ap-guangzhou",
            "LogoAdd": 0,
            "RspImgType": "url",
            "Prompt": prompt,
            "Styles": [style],
            "ResultConfig": {"Resolution": size}
        }
        req.from_json_string(json.dumps(params))
        resp = client.TextToImage(req)
        with open(f"{temp_dir}/image/{img_id}.png", 'wb+') as f:
            f.write(requests.get(resp.ResultImage).content)
    except TencentCloudSDKException as err:
        print(err)
