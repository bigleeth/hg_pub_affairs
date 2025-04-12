import requests

cookies = {
    '_fwb': '224GIbJbv3W2VKbiHHpHIKa.1736910833680',
    '_ga': 'GA1.1.1553764147.1736910835',
    'PCID': '756e904c-0b66-a4a7-6836-589756f10a6e-1736910838628',
    'JSESSIONID': 'KHYMbxRBf39S41H5IaF3ItGp1lVaTFrc5Oa6tAm7pU1kWVnovMhmrtaSEBvSagwl.amV1c19kb21haW4vbmFob21lNA==',
    'PHAROSVISITOR': '00006eb50196285f2f296cc80ac965a6',
    'NetFunnel_ID': '',
    'wcs_bt': '1a0c69697fe3410:1744436809',
    '_ga_8FY090CL6Y': 'GS1.1.1744436364.6.1.1744436810.0.0.0',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Referer': 'https://www.assembly.go.kr/members/22nd/KIMYOUNGJIN',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    # 'Cookie': '_fwb=224GIbJbv3W2VKbiHHpHIKa.1736910833680; _ga=GA1.1.1553764147.1736910835; PCID=756e904c-0b66-a4a7-6836-589756f10a6e-1736910838628; JSESSIONID=KHYMbxRBf39S41H5IaF3ItGp1lVaTFrc5Oa6tAm7pU1kWVnovMhmrtaSEBvSagwl.amV1c19kb21haW4vbmFob21lNA==; PHAROSVISITOR=00006eb50196285f2f296cc80ac965a6; NetFunnel_ID=; wcs_bt=1a0c69697fe3410:1744436809; _ga_8FY090CL6Y=GS1.1.1744436364.6.1.1744436810.0.0.0',
}

params = {
    'monaCd': '5765663F',
    'st': '22',
    'viewType': 'CONTBODY',
}

response = requests.get(
    'https://www.assembly.go.kr/portal/assm/assmMemb/member.do',
    params=params,
    cookies=cookies,
    headers=headers,
)
print(response.text)    