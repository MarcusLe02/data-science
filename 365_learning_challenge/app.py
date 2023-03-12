import json
import requests
headers = {
    "Authorization":"Bearer ya29.a0AVvZVsqVJG5POmVsLlU6lr-ymdLD_nnEQECszTvM0GKwqKKH8W66g84vuSGShrA0B_Bd3nq56KA1-wdPKu2VMbcxnIWWDrmtxTMieguAU8bNPccJh2dJJbq5i9IAV_LHOyddK4ZMlw-ltfUmhwKQ2l6j1JO1YMIaCgYKARQSAQASFQGbdwaIR_Pxcc6bKkgSaVtm9eZyEA0166"
}

para = {
    "name":"demo.py",
    "parents":["1PhlRUhup-90_Qte7g9IhVEpYpebnyufZ"]
}

files = {
    'data':('metadata',json.dumps(para),'application/json;charset=UTF-8'),
    'file':open('./demo.py','rb')
}

r = requests.post("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
    headers=headers,
    files=files
)