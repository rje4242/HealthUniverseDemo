import functools
import glob
import json
import logging
import os
import random
import uuid
from collections import Counter
from enum import Enum
from pathlib import Path
from typing import Annotated, Callable, Optional

import uvicorn
from fastapi import (Depends, FastAPI, File, Form, Header, Cookie, HTTPException,
                     Query, Request, Response, UploadFile, status)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import (FileResponse, HTMLResponse, JSONResponse,
                               PlainTextResponse, RedirectResponse,
                               StreamingResponse)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw, ImageFont
import io


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastapi-logger")
logger.setLevel(logging.INFO)  # Set the logging level

# Create file handler which logs even debug messages
fh = logging.FileHandler('fastapi-logger.log')

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s -  %(message)s')
fh.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(fh)


app = FastAPI()

templates = Jinja2Templates(directory="templates_fastapi")
def create_session_token():
    return str(uuid.uuid4())


@app.get("/get_my_ip")
async def get_my_ip(
    request:Request,
    x_forwarded_for: str = Header(None, alias='X-Forwarded-For'),
    x_real_ip: str = Header(None, alias='X-Real-IP')
):
    return {"X-Forwarded-For": x_forwarded_for, "X-Real-Ip": x_real_ip, "client_host": request.client.host }


@app.get("/image/{text}")
async def image_endpoint(text: str):
    # Create an image with red background
    img = Image.new('RGB', (800, 800), color='red')
    d = ImageDraw.Draw(img)

    # Add text to the image
    font = ImageFont.load_default()  # Loads default font
    text_width, text_height = d.textsize(text, font=font)

    # Calculate position to center the text
    x = (img.width - text_width) / 2
    y = (img.height - text_height) / 2
    d.text((x, y), text, fill='black', font=font)

    # Save image to a bytes buffer
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Return the response
    return StreamingResponse(io.BytesIO(img_byte_arr), media_type="image/png")


import time
import asyncio
from datetime import datetime
from typing import Iterator


list1 = range(0,20)
list2 = "apple banana cherry pear apricot strawberry".split()
list3 = [ (x, x**2, x**3) for x in range(0,10) ]

@app.get("/get_list1")
async def get_list1():
    async def event_generator():
        for num in list1:
            yield f"data: {num}\n\n"
            asyncio.sleep(2)
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/get_list2")
async def get_list2():
    async def event_generator():
        for fruit in list2():
            yield f"data: {fruit}\n\n"
            asyncio.sleep(2)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

def sse_format(data: str) -> str:
    return f"data: {data}\n\n"


async def generate_random_data(request: Request) -> Iterator[str]:
    """
    Generates random value between 0 and 100

    :return: String containing current timestamp (YYYY-mm-dd HH:MM:SS) and randomly generated data.
    """
    client_ip = request.client.host

    logger.info("Client %s connected", client_ip)

    while True:
        json_data = json.dumps(
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "value": random.random() * 100,
            }
        )
        yield f"data:{json_data}\n\n"
        await asyncio.sleep(1)


@app.get("/chart-data")
async def chart_data(request: Request) -> StreamingResponse:
    response = StreamingResponse(generate_random_data(request), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@app.get("/htmx2")
async def htmx2(request: Request, hx_request:Optional[str] = Header(None) ):

    films = [
        {"name":"blade runner", "director":"ridley scott"},
        {"name": "star wars", "director": "george lucas"},
        {"name": "history of the world", "director": "mel brooks"},
    ]

    if hx_request:
        print("hx_request recieved")
        response = templates.TemplateResponse("table.html", context={"request": request, "films":   films  })
    else:
        raise HTTPException("htmx event handler called incorrectly")
    return response


@app.get("/", response_class=HTMLResponse)
async def Htmx1(request: Request, hx_request:Optional[str] = Header(None) ):

    blanks = [
    ]

    films = [
        {"name":"blade runner", "director":"ridley scott"},
        {"name": "star wars", "director": "george lucas"},
        {"name": "history of the world", "director": "mel brooks"},
    ]

    if hx_request:
        print("hx_request recieved")
        response = templates.TemplateResponse("table.html", context={"request": request, "films":   films  })
    else:
        print("no HTMX")
        response = templates.TemplateResponse("traversy_htmx.html", context={"request": request, "films":   blanks  })
    return response



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)

