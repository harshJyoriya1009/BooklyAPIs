from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import logging


logger = logging.getLogger('uvicorn.access')
logger.disabled = True

def register_middleware(app:FastAPI):
    
    @app.middleware('http')
    async def custom_logging(request:Request, call_next):
        start_time = time.time()
       
        response = await call_next(request)

        proccessing_time = time.time()-start_time 
        message =f'{request.client.host}:{request.client.port} {request.method} - {request.url.path} - {response.status_code} = Completed after {proccessing_time}s'   # Custom log middleware
        print(message)

        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],       
        allow_methods=["*"],    
        allow_headers=["*"], 
        allow_credentials=True,
    )