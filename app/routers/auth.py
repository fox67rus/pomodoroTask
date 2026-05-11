from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import create_access_token
from app.crud.users import authenticate_user, create_user, get_user_by_email, get_user_by_username
from app.schemas.users import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


def templates(request: Request):
    return request.app.state.templates


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates(request).TemplateResponse(request, "auth/register.html", {"request": request})


@router.post("/register")
def register(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    email: Annotated[str, Form()],
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    if get_user_by_email(db, email) or get_user_by_username(db, username):
        return templates(request).TemplateResponse(
            request,
            "auth/register.html",
            {"request": request, "error": "Пользователь с таким email или именем уже существует."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    user = create_user(db, UserCreate(email=email, username=username, password=password))
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie("access_token", create_access_token(user.id), httponly=True, samesite="lax")
    return response


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates(request).TemplateResponse(request, "auth/login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    login_name: Annotated[str, Form(alias="login")],
    password: Annotated[str, Form()],
):
    user = authenticate_user(db, login_name, password)
    if not user:
        return templates(request).TemplateResponse(
            request,
            "auth/login.html",
            {"request": request, "error": "Неверный логин или пароль."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie("access_token", create_access_token(user.id), httponly=True, samesite="lax")
    return response


@router.post("/logout")
def logout():
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response
