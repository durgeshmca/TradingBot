from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Configuration (Replace with your actual keys and URL)
CLIENT_ID = os.getenv("UPSTOX_CLIENT_ID")
CLIENT_SECRET = os.getenv("UPSTOX_CLIENT_SECRET")
REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI")
AUTH_URL = "https://api.upstox.com/v2/login/authorization/dialog"
TOKEN_URL = "https://api.upstox.com/v2/login/authorization/token"

# Mount templates and static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI})

def update_env(env_path:str,key,value):
    os.environ[key] = value
    # update env file as well
    with open(env_path,'r') as fp:
        lines = fp.readlines()
    with open(env_path,'w') as fp:
        for line in lines:
            if line.startswith(f'{key}'):
                fp.write(f"{key} = '{value}'\n")
            else:
                fp.write(line)

@app.get("/callback")
async def callback(code: str, state: str = None):
    """Handle redirect from Upstox and fetch access token"""
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, data=data, headers=headers)
        token_data = response.json()
        with open("token.json",'wb') as f:
            f.write(response.content)
        # update token in env
        data = response.json()
        if data.get('access_token'):
            update_env('../.env','ACCESS_TOKEN',data.get('access_token'))
        return token_data