from dotenv import load_dotenv
from app import create_app

# Load environment variables first
load_dotenv()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)