ENVIRONMENTS = {
  "streaming": {
    "real": "stream-fxtrade.oanda.com",
    "practice": "stream-fxpractice.oanda.com",
    "sandbox": "stream-sandbox.oanda.com"
  },
  "api": {
    "real": "api-fxtrade.oanda.com",
    "practice": "api-fxpractice.oanda.com",
    "sandbox": "api-sandbox.oanda.com"
  }
}

DOMAIN = "practice"
STREAM_DOMAIN = ENVIRONMENTS["streaming"][DOMAIN]
API_DOMAIN = ENVIRONMENTS["api"][DOMAIN]
ACCESS_TOKEN = 'abcdef0123456abcdef0123456-abcdef0123456abcdef0123456'
ACCOUNT_ID = '12345678'
