import os
from dotenv import load_dotenv
load_dotenv()

print("DATABASE_URL:", os.getenv('DATABASE_URL'))
print("SECRET_KEY:", os.getenv('SECRET_KEY'))