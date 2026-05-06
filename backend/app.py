if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    from main import app

    app.root_path = None

import logging

import uvicorn
from scripts.config import Service

if __name__ == "__main__":
    logging.info(f"App Starting at {Service.HOST}:{Service.PORT}")
    uvicorn.run("main:app", host=Service.HOST, port=int(Service.PORT))
