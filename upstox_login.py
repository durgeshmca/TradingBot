# upstox_login.py
from upstox_api.api import Upstox
from config import API_KEY, API_SECRET, REDIRECT_URI

print("Generate login URL:")
login_url = f"https://api.upstox.com/index/dialog/authorize?apiKey={API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code"
print(login_url)

# Once authorized, you’ll get a ?code=... in the URL
# Paste it here to get access token

code = input("Paste the authorization code: ")

u = Upstox(API_KEY, API_SECRET)
u.get_access_token(code)
print("Access Token:", u.get_access_token())
print("Login successful")

# Save this token to use in your trading script
