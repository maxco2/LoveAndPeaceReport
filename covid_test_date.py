import datetime
import json
import time
from typing import Tuple
import requests
from datetime import datetime

headers_jsstm = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}
headers_jshscx = {'Content-Type': 'application/json;charset=UTF-8'}

def get_abc(token:str,uuid:str) -> Tuple[str,str]:
    data = {
            'token': token,
            'uuid': uuid 
            }
    user_auth_token = 'https://jsstm.jszwfw.gov.cn/jkm/2/userAuth_token'
    with requests.post(user_auth_token, headers=headers_jsstm, data=data) as res:
        abc = res.json()['res']['userdetail']['abc']
        name = res.json()['res']['userdetail']['name']
        return abc,name


def get_secret(abc: str) -> str:
    query_drhs = 'https://jsstm.jszwfw.gov.cn/jkm/2/queryDrHs'
    data = {'idType': '1', 'abc': abc}
    with requests.post(query_drhs, headers=headers_jsstm, data=data) as res:
        url = str(res.json()['res']['url'])
        return url.split('?secret=')[-1]


def auth_secret(secret: str) -> dict:
    rna_auth = 'https://jshscx.jsehealth.com:8002/app-backend/rna/authentication'
    data = {'secret': secret}
    with requests.post(rna_auth, headers=headers_jshscx, data=json.dumps(data)) as res:
        id_type = res.json()['data']['idType']
        id_card = res.json()['data']['idCard']
        headers_jshscx['secret'] = secret
        return {'idType': id_type, 'idCard': id_card}


def query_report(data: dict) -> list:
    query_rna_report = 'https://jshscx.jsehealth.com:8002/app-backend/rna/queryRnaReport'
    with requests.post(query_rna_report, headers=headers_jshscx, data=json.dumps(data)) as res:
        report_list = res.json()['data']['reportList']
        return report_list

def get_sw_hs(abc: str,name:str) -> str:
    query_drhs = 'https://jsstm.jszwfw.gov.cn/jkm/2/queryHskt'
    data = {"userName":name,'abc': abc}
    with requests.post(query_drhs, headers=headers_jsstm, data=data) as res:
        res = str(res.json()["res"]["hs"]["data"]["hsjcsj"])
        return res


def get_covid_test_date(token,uuid) -> str:
    if token=='' or uuid=='' or token is None or uuid is None:
        raise Exception("invaild token or uuid")
    abc,name = get_abc(token,uuid)
    sw_hs_date = get_sw_hs(abc,name)
    sw_hs_date = datetime.strptime(sw_hs_date,'%Y-%m-%d %H:%M:%S')
    secret = get_secret(abc)
    auth_info = auth_secret(secret)
    report = query_report(auth_info)
    # print(f"report:{report},type:{type(report)}")
    hs_date = report[0]['collectTime']
    hs_date = datetime.strptime(hs_date,'%Y-%m-%d %H:%M')
    hs_date = max(hs_date,sw_hs_date)
    hs_date = hs_date.strftime("%Y-%m-%d %-H")
    return hs_date


if __name__ == '__main__':
    token = '?'
    uuid = '?'
    hs_date = get_covid_test_date(token,uuid)
    print(type(hs_date))
    print(hs_date)
