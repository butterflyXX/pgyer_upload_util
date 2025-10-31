# -*- coding: utf-8 -*-

import sys
import os
import time
import requests

API_KEY = 'api_key'
SUPPORTED_TYPES = {'ipa': 'ios', 'apk': 'android', 'hap': 'harmony'}
GET_COSTOKEN_URL = 'https://api.pgyer.com/apiv2/app/getCOSToken'
GET_BUILD_INFO_URL = 'https://api.pgyer.com/apiv2/app/buildInfo'
def _get_build_type(file_path):
    if not os.path.exists(file_path):
        return None
    file_ext = os.path.splitext(file_path)[1][1:].lower()
    return SUPPORTED_TYPES.get(file_ext, None)

def _get_cos_token(path: str, desc: str):
    build_type = _get_build_type(path)
    if build_type is None:
        print(f'文件错误: {path}')
        return (False,None)
    payload = {'_api_key': API_KEY, 'buildType': build_type, 'buildUpdateDescription': desc}
    r = requests.post(GET_COSTOKEN_URL, data=payload)
    if r.status_code != 200:
        print('getCOSToken error', r.text)
        return (False,None)
    token_json = r.json()
    if 'data' not in token_json or 'endpoint' not in token_json['data']:
        print('getCOSToken结果无data', token_json)
        return (False,None)
    return (True,token_json['data'])

def _upload_file(path: str, token_json: dict):
    files = None
    with open(path, 'rb') as f:
        files = {'file': f}
        headers = {'enctype': 'multipart/form-data'}
        up = requests.post(token_json['endpoint'], data=token_json['params'], files=files, headers=headers)
    if up.status_code != 204:
        print('upload error', up.status_code, up.text)
        return False
    return True

def _get_build_info(build_key: str):
    for _ in range(10):
        time.sleep(3)
        binfo = requests.get(
            GET_BUILD_INFO_URL,
            params={'_api_key': API_KEY, 'buildKey': build_key}
        )
        resj = binfo.json()
        if resj['code'] not in (1246, 1247):
            if resj['code'] == 0 and 'data' in resj and 'buildKey' in resj['data']:
                return f"https://www.pgyer.com/{resj['data']['buildKey']}"
            else:
                print('获取build info失败', resj)
                return None
    print("等待超时")
    return None


def upload_to_pgyer_sync(path, desc):
    success, token_json = _get_cos_token(path, desc)
    if not success:
        return None

    success = _upload_file(path, token_json)
    if not success:
        return None
    
    build_key = token_json['params']['key']
    return _get_build_info(build_key)

if __name__ == "__main__":
    path = sys.argv[1]
    desc = sys.argv[2]
    url = upload_to_pgyer_sync(path, desc)
    if url:
        print(url)