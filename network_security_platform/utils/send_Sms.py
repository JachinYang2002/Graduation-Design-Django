import json
from ronglian_sms_sdk import SmsSDK
from django.conf import settings

accId = '2c94811c8853194e0188616ffbeb0324'
accToken = '35a494f497cd4f37989b879a61a35602'
appId = '2c94811c8853194e0188616ffd23032b'

def send_sms_code(smscode, phone):
    # sdk = SmsSDK(settings.accId, settings.accToken, settings.appId)
    sdk = SmsSDK(accId, accToken, appId)
    tid = '1'
    mobile = phone
    datas = (smscode, '5')
    resp = sdk.sendMessage(tid, mobile, datas)
    return json.loads(resp)
