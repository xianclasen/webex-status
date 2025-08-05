from flask import Flask, render_template, Response
import httpx
from dotenv import load_dotenv
import os
import random
from pydantic import BaseModel, ValidationError
from typing import List

load_dotenv()
app = Flask(__name__)

headers = {"Authorization": f"Bearer {os.getenv('webex_token')}"}
user = os.getenv("person")
status_dict = {
    "call": "call.html",
    "meeting": "meeting.html",
    "presenting": "presenting.html",
}

class PersonItem(BaseModel):
    status: str

class PeopleResponse(BaseModel):
    items: List[PersonItem]

def random_image_response(refresh_header: str) -> Response:
    images_path = os.path.join(app.static_folder, "images")
    images = [
        img
        for img in os.listdir(images_path)
        if img.lower().endswith(("png", "jpg", "jpeg", "gif"))
    ]
    random_image = random.choice(images) if images else ""
    return Response(
        refresh_header
        + f'<div style="display: flex; justify-content: center; align-items: center; height: 100vh;"><img src="/static/images/{random_image}" style="max-width:100%;"></div>',
        mimetype="text/html",
    )

@app.route("/")
def index():
    refresh_header = "<meta http-equiv='refresh' content='5'>"
    resp = httpx.get(f"https://webexapis.com/v1/people?email={user}", headers=headers)
    try:
        data = PeopleResponse.parse_obj(resp.json())
        status = data.items[0].status
        print(f"Status: {status}")
        template = status_dict.get(status)
        if template:
            return Response(
                refresh_header + render_template(template), mimetype="text/html"
            )
    except (KeyError, IndexError, ValueError, ValidationError) as e:
        print(f"Failed to get status: {resp.content} ({e})")
    return random_image_response(refresh_header)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)