from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
import json
from datetime import datetime

app = FastAPI()

MOVIES_FILE = "movies.json"

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

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

DARK_THEME_STYLE = """
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #1a1a1a; color: #e0e0e0; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1, h2, h3 { color: #ffffff; }
        .card { background-color: #2d2d2d; border: 1px solid #404040; border-radius: 8px; padding: 20px; margin: 15px 0; }
        .movie-card { display: flex; gap: 20px; background-color: #2d2d2d; border: 1px solid #404040; border-radius: 8px; padding: 20px; margin: 15px 0; }
        .btn { background: #1971c2; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }
        .btn-success { background: #2b8a3e; }
        input, textarea { width: 100%; padding: 10px; border: 1px solid #404040; border-radius: 6px; background-color: #2d2d2d; color: #e0e0e0; box-sizing: border-box; margin-bottom: 10px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #ffffff; }
        .checkbox { width: auto; margin-right: 10px; }
        img { border-radius: 6px; }
        .nav { display: flex; gap: 10px; margin: 20px 0; flex-wrap: wrap; }
    </style>
"""

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
                        <label>Бюджет (в млн $):</label>
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
                        <textarea name="description" rows="4" placeholder="Введите описание фильма..."></textarea>
                    </div>
                    <div class="form-group">
                        <label>Обложка фильма:</label>
                        <input type="file" name="poster" accept="image/*" required>
                    </div>
                    <button type="submit" class="btn btn-success">Добавить фильм</button>
                </form>
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
        "posterurl": f"/static/{poster_filename}",
        "added_at": datetime.now().isoformat()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8166, reload=True)