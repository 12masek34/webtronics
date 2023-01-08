import uvicorn

from database import create_db
from app import app


if __name__ == '__main__':
    create_db()
    uvicorn.run(app, host='0.0.0.0', port=8000)
