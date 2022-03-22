from datetime import datetime
from fastapi import Request, Depends, APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# TODO import PyOpenGraph

from database.blog import MessagesDatabase
from models import Message
from dependencies import MessageForm
import security

router = APIRouter(
    prefix="/blog",
    tags=["blog"],
    default_response_class=HTMLResponse,
)

router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

database_name = "sqlite.db"
message_database = MessagesDatabase(database_name=database_name)


@router.get("/", response_class=HTMLResponse)
async def blog_list(request: Request):
    current_user = security.get_current_user(request)
    messages = message_database.get_all_messages()
    return templates.TemplateResponse("blog/list.html", {"request": request,
                                                         "current_user": current_user,
                                                         "messages": messages})


@router.get("/new_message", response_class=HTMLResponse)
async def get_new_message(request: Request):
    current_user = security.get_current_user(request)
    return templates.TemplateResponse("blog/new_message.html", {"request": request,
                                                                "current_user": current_user})


@router.post("/new_message", response_class=HTMLResponse)
async def post_new_message(request: Request,
                           form_data: MessageForm = Depends()):
    current_user = security.get_current_user(request)
    author = current_user
    if form_data.message_is_empty():
        status = "You need to feel one of the field for new Post!"
    else:
        message = Message(
            author=author,
            published=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            body=form_data.body,
            link=form_data.link
        )
        message_database.insert_new_message(message)
        status = "New message was added!"
    return templates.TemplateResponse("blog/new_message.html", {"request": request,
                                                                "current_user": current_user,
                                                                "status": status})


@router.get("/{message_id}", response_class=HTMLResponse)
async def get_message_detail(request: Request,
                             message_id: int):
    current_user = security.get_current_user(request)
    db_result = message_database.get_message_details(message_id=message_id)
    if db_result:
        message = Message(**db_result)
        return templates.TemplateResponse("blog/detail.html", {"request": request,
                                                               "current_user": current_user,
                                                               "message": message})
    else:
        return RedirectResponse(url='/blog/')


@router.get("/delete/{message_id}", response_class=HTMLResponse)
async def get_delete_message(request: Request,
                             message_id: int):
    current_user = security.get_current_user(request)
    message_author = message_database.is_author(message_id=message_id)
    if message_author == current_user:
        message_database.delete_message(message_id=message_id)
    return RedirectResponse(url='/blog/')
