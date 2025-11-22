from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from models import Movietop
import os

app = FastAPI()

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

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

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
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <h1>Брянский государственный инженерно-технологический университет</h1>
                    <img src="/static/SUx182_2x.jpg" alt="Университет" style="max-width: 500px; height: auto;">
                    <div class="nav">
                        <a href="/" class="btn">На главную</a>
                    </div>
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
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Movie not found")

@app.get("/movietop/")
async def get_all_movies():
    return {"movies": movie_top_10}


@app.get("/movietop", response_class=HTMLResponse)
async def get_all_movies_page():
    movies_html = ""
    for movie in movie_top_10:
        movies_html += f"""
        <div class="movie-card">
            <div style="flex-grow: 1;">
                <h2>{movie.name}</h2>
                <p><strong>Режиссер:</strong> {movie.director}</p>
                <p><strong>Бюджет:</strong> ${movie.cost} млн</p>
                <p><strong>ID:</strong> {movie.id}</p>
            </div>
        </div>
        """

    return f"""
    <html>
    <head>
        <title>Топ-10 фильмов</title>
    </head>
    <body>
        <div class="container">
            <h1>Топ-10 фильмов</h1>
            <div class="nav">
                <a href="/" class="btn">На главную</a>
            </div>
            {movies_html}
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8165, reload=True)