from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from config import read_config


# Loading environment variables before local imports:
load_dotenv()

# Declaring FastAPI instance before local imports to avoid circular imports:
app = FastAPI()

from routers import messages

# Declaring routers (sub-applications) that are a part of the app:
app.include_router(messages.router)


# Cross-Origin Resource Sharing is a browser security feature, preventing 
# malicious domains from accessing data from another domain without permission.
# To make the API accessible from web applications hosted on different 
# domains, we need to add the domains that are permitted:
origins = read_config("cors_origins")

# allow_credentials permits credentials from trusted IPs (e.g. cookies, auth headers).
# '*' indicates all HTTP methods and headers are allowed.
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, 
                   allow_methods=['*'], allow_headers=['*'])


"""
TODO: IMPLEMENT IF THERE IS TIME:
INFO ABOUT THE EXHIBITS IN DB

DB with client (museum) - registration from PGadmin4
Auth endpoint automatically triggered?

"""


"""
cd FastAPI
source venv/bin/activate
uvicorn main:app --reload
"""

