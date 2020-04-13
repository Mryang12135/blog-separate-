# 一分钟发一次短信频率限制
from rest_framework.throttling import SimpleRateThrottle
class SMSRateThrottle(SimpleRateThrottle):
    scope = 'sms'
    def get_cache_key(self, request, view):
        phone = request.data.get('phone')
        if phone:
            return 'sms_throttle_%s' % phone

