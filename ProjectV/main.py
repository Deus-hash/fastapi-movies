from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from models import Movietop
import os
import shutil
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI()

sessions = {}
SESSION_LIFETIME = 30

movie_top_10 = [
    Movietop(name="Всеведущий читатель", id=1, cost=23, director="Ким Бён-у"),
    Movietop(name="Пятый элемент", id=2, cost=90, director="Люк Бессон"),
    Movietop(name="Точка ноль", id=3, cost=5, director="Сергей Пикалов"),
    Movietop(name="Министерство неджентльменских дел", id=4, cost=60, director="Гай Ричи"),
    Movietop(name="Мстители: Война бесконечности", id=5, cost=321, director="Энтони и Джо Руссо"),
    Movietop(name="Достать ножи", id=6, cost=40, director="Райан Джонсон"),
    Movietop(name="Король Лев", id=7, cost=45, director="Джон Фавро"),
    Movietop(name="Майор Гром", id=8, cost=5, director="Олег Трофим"),
    Movietop(name="Тихое место", id=9, cost=19, director="Джон Красински"),
    Movietop(name="Сто лет тому вперёд", id=10, cost=150, director="Александр Андрющенко")
]

USERS = {
    "admin": "password",
    "user": "pass"
}

MOVIES_FILE = "movies.json"
USERS_FILE = "users.json"
LOGIN_LOG_FILE = "login_log.json"


def get_movies():
    if os.path.exists(MOVIES_FILE):
        with open(MOVIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_movies(movies):
    with open(MOVIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)


def get_next_id():
    movies = get_movies()
    if not movies:
        return 1
    return max(movie['id'] for movie in movies) + 1


def log_login(username: str, session_token: str, ip_address: str = None):

    login_data = {
        "username": username,
        "session_token": session_token,
        "login_time": datetime.now().isoformat(),
        "ip_address": ip_address
    }

    logs = get_login_logs()
    logs.append(login_data)

    with open(LOGIN_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2, default=str)


def get_login_logs():
    if os.path.exists(LOGIN_LOG_FILE):
        with open(LOGIN_LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def get_user_login_history(username: str, limit: int = 10):

    logs = get_login_logs()
    user_logs = [log for log in logs if log["username"] == username]
    user_logs.sort(key=lambda x: x["login_time"], reverse=True)
    return user_logs[:limit]


def create_session(username: str) -> str:
    session_token = str(uuid.uuid4())
    now = datetime.now()
    expires_at = now + timedelta(seconds=SESSION_LIFETIME)

    sessions[session_token] = {
        "username": username,
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "last_accessed": now.isoformat()
    }

    print(f"Создана сессия для {username}: {session_token}")
    return session_token


def validate_session(session_token: str) -> Optional[dict]:
    if not session_token or session_token not in sessions:
        return None

    session = sessions[session_token]
    expires_at = datetime.fromisoformat(session["expires_at"])

    if datetime.now() > expires_at:
        del sessions[session_token]
        return None

    now = datetime.now()
    new_expires_at = now + timedelta(seconds=SESSION_LIFETIME)
    session["expires_at"] = new_expires_at.isoformat()
    session["last_accessed"] = now.isoformat()

    return session


os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

DARK_THEME_STYLE = """
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background-color: #1a1a1a; 
            color: #e0e0e0; 
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
        }
        h1, h2, h3 { 
            color: #ffffff; 
        }
        a { 
            color: #4dabf7; 
            text-decoration: none; 
        }
        a:hover { 
            color: #74c0fc; 
            text-decoration: underline; 
        }
        .card { 
            background-color: #2d2d2d; 
            border: 1px solid #404040; 
            border-radius: 8px; 
            padding: 20px; 
            margin: 15px 0; 
        }
        .movie-card { 
            display: flex; 
            gap: 20px; 
            background-color: #2d2d2d; 
            border: 1px solid #404040; 
            border-radius: 8px; 
            padding: 20px; 
            margin: 15px 0; 
        }
        .btn { 
            background: #1971c2; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            text-decoration: none; 
            display: inline-block; 
        }
        .btn:hover { 
            background: #1864ab; 
        }
        .btn-success { 
            background: #2b8a3e; 
        }
        .btn-success:hover { 
            background: #2f9e44; 
        }
        input, textarea, select { 
            width: 100%; 
            padding: 10px; 
            border: 1px solid #404040; 
            border-radius: 6px; 
            background-color: #2d2d2d; 
            color: #e0e0e0; 
            box-sizing: border-box; 
        }
        input:focus, textarea:focus { 
            border-color: #1971c2; 
            outline: none; 
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: bold; 
            color: #ffffff; 
        }
        .checkbox { 
            width: auto; 
            margin-right: 10px; 
        }
        img { 
            border-radius: 6px; 
        }
        .error { 
            color: #ff6b6b; 
            background: #2d1a1a; 
            padding: 10px; 
            border-radius: 6px; 
            margin: 10px 0; 
        }
        .success { 
            color: #51cf66; 
            background: #1a2d1a; 
            padding: 10px; 
            border-radius: 6px; 
            margin: 10px 0; 
        }
        .log-entry { 
            background-color: #2d2d2d; 
            border: 1px solid #404040; 
            border-radius: 6px; 
            padding: 15px; 
            margin: 10px 0; 
        }
        .log-time { 
            color: #74c0fc; 
            font-weight: bold; 
        }
        .log-user { 
            color: #51cf66; 
        }
        .login-history { 
            margin-top: 20px; 
            padding: 15px; 
            background-color: #2d2d2d; 
            border-radius: 8px; 
        }
        .history-item { 
            padding: 8px; 
            border-bottom: 1px solid #404040; 
        }
        .history-item:last-child { 
            border-bottom: none; 
        }
    </style>
"""


@app.get("/")
async def root():
    return {"message": "Hello World", "status": "success"}


@app.get("/study")
async def study_info():
    return {
        "university": "Брянский государственный инженерно-технологический университет",
        "photo_url": "/static/SUx182_2x.jpg"
    }


@app.get("/study/page", response_class=HTMLResponse)
async def study_page():
    return f"""
    <html>
        <head>
            <title>Университет</title>
            {DARK_THEME_STYLE}
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <h1>Брянский государственный инженерно-технологический университет</h1>
                    <img src="/static/SUx182_2x.jpg" alt="Университет" style="max-width: 500px; height: auto;">
                    <p style="margin-top: 20px;">
                        <a href="/" class="btn">На главную</a>
                    </p>
                </div>
            </div>
        </body>
    </html>
    """


@app.get("/movietop/{movie_name}")
async def get_movie_info(movie_name: str):
    movie = next((m for m in movie_top_10 if m.name.lower() == movie_name.lower()), None)
    if movie:
        return movie
    raise HTTPException(status_code=404, detail="Movie not found")


@app.get("/movietop/")
async def get_all_movies():
    return {"movies": movie_top_10}


@app.post("/login")
async def login(
        request: Request,
        response: Response,
        username: str = Form(...),
        password: str = Form(...)
):
    if username not in USERS or USERS[username] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_token = create_session(username)

    client_host = request.client.host if request.client else "unknown"

    log_login(username, session_token, client_host)

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=SESSION_LIFETIME
    )

    redirect_response = RedirectResponse(url="/user", status_code=303)
    redirect_response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=SESSION_LIFETIME
    )

    return redirect_response


@app.get("/login", response_class=HTMLResponse)
async def login_form():
    return f"""
    <html>
    <head>
        <title>Вход в систему</title>
        {DARK_THEME_STYLE}
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1>Вход в систему</h1>
                <form action="/login" method="post">
                    <div class="form-group">
                        <label>Имя пользователя:</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>Пароль:</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-success">Войти</button>
                </form>
                <br>
                <p><strong>Тестовые пользователи:</strong></p>
                <ul>
                    <li>admin / password</li>
                    <li>user / pass</li>
                </ul>
                <a href="/" class="btn">На главную</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/user")
async def user_info(request: Request):
    session_token = request.cookies.get("session_token")

    if not session_token:
        return JSONResponse(
            status_code=401,
            content={"message": "Unauthorized"}
        )

    session = validate_session(session_token)
    if not session:
        return JSONResponse(
            status_code=401,
            content={"message": "Unauthorized"}
        )

    username = session["username"]
    all_movies = get_movies()

    login_history = get_user_login_history(username, limit=10)

    formatted_history = []
    for log in login_history:
        login_time = datetime.fromisoformat(log["login_time"])
        formatted_history.append({
            "login_time": login_time.isoformat(),
            "ip_address": log.get('ip_address', 'unknown'),
            "session_token": log['session_token'][:8] + "..."
        })

    user_data = {
        "username": username,
        "session_info": {
            "created_at": session["created_at"],
            "last_accessed": session["last_accessed"],
            "expires_at": session["expires_at"],
            "current_time": datetime.now().isoformat()
        },
        "login_history": formatted_history,
        "movies": {
            "top_10": [movie.model_dump() for movie in movie_top_10],
            "custom_movies": all_movies
        }
    }

    return user_data


@app.get("/add-movie-form", response_class=HTMLResponse)
async def add_movie_form():
    return f"""
    <html>
    <head>
        <title>Добавить фильм</title>
        {DARK_THEME_STYLE}
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1>Добавить новый фильм</h1>
                <form action="/add-movie" method="post" enctype="multipart/form-data">
                    <div class="form-group">
                        <label>Название фильма:</label>
                        <input type="text" name="title" required>
                    </div>
                    <div class="form-group">
                        <label>Режиссер:</label>
                        <input type="text" name="director" required>
                    </div>
                    <div class="form-group">
                        <label>Год выпуска:</label>
                        <input type="number" name="year" required>
                    </div>
                    <div class="form-group">
                        <label>Бюджет (в млн):</label>
                        <input type="number" name="budget" required>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" name="oscar" value="true" class="checkbox">
                            Получил Оскар
                        </label>
                    </div>
                    <div class="form-group">
                        <label>Описание фильма:</label>
                        <textarea name="description" rows="4"></textarea>
                    </div>
                    <div class="form-group">
                        <label>Обложка фильма:</label>
                        <input type="file" name="poster" accept="image/*" required>
                    </div>
                    <button type="submit" class="btn btn-success">Добавить фильм</button>
                </form>
                <br>
                <a href="/movies" class="btn">Посмотреть все добавленные фильмы</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.post("/add-movie")
async def add_movie(
        title: str = Form(...),
        director: str = Form(...),
        year: int = Form(...),
        budget: int = Form(...),
        oscar: bool = Form(False),
        description: str = Form(""),
        poster: UploadFile = File(...)
):
    movies = get_movies()
    next_id = get_next_id()

    poster_filename = f"poster_{next_id}.jpg"
    poster_path = f"static/{poster_filename}"

    with open(poster_path, "wb") as buffer:
        shutil.copyfileobj(poster.file, buffer)

    movie_data = {
        "id": next_id,
        "title": title,
        "director": director,
        "year": year,
        "budget": budget,
        "oscar": oscar,
        "description": description,
        "posterurl": f"/static/{poster_filename}"
    }

    movies.append(movie_data)
    save_movies(movies)

    return RedirectResponse(url="/movies", status_code=303)


@app.get("/movies", response_class=HTMLResponse)
async def get_all_movies_page():
    movies = get_movies()

    if not movies:
        return f"""
        <html>
            <head>
                <title>Фильмы</title>
                {DARK_THEME_STYLE}
            </head>
            <body>
                <div class="container">
                    <div class="card">
                        <h1>Добавленные фильмы</h1>
                        <p>Пока нет добавленных фильмов.</p>
                        <a href="/add-movie-form" class="btn btn-success">Добавить первый фильм</a>
                    </div>
                </div>
            </body>
        </html>
        """

    movies_html = ""
    for movie in movies:
        oscar = "*" if movie["oscar"] else ""
        movies_html += f"""
        <div class="movie-card">
            <img src="{movie['posterurl']}" alt="{movie['title']}" style="width: 120px; height: 180px; object-fit: cover;">
            <div style="flex-grow: 1;">
                <h2>{movie['title']} {oscar}</h2>
                <p><strong>Режиссер:</strong> {movie['director']}</p>
                <p><strong>Год:</strong> {movie['year']}</p>
                <p><strong>Бюджет:</strong> ${movie['budget']} млн</p>
                <p><strong>Оскар:</strong> {'Да' if movie['oscar'] else 'Нет'}</p>
                <p><strong>Описание:</strong> {movie['description'] or 'Нет описания'}</p>
                <p><strong>ID:</strong> {movie['id']}</p>
            </div>
        </div>
        """

    return f"""
    <html>
    <head>
        <title>Добавленные фильмы</title>
        {DARK_THEME_STYLE}
    </head>
    <body>
        <div class="container">
            <h1>Все добавленные фильмы</h1>
            <a href="/add-movie-form" class="btn btn-success">+ Добавить фильм</a>
            <a href="/" class="btn" style="margin-left: 10px;">На главную</a>
            {movies_html}
        </div>
    </body>
    </html>
    """


@app.get("/logout")
async def logout(response: Response):
    response.delete_cookie("session_token")
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8167, reload=True)