from typing import Optional
from fastapi import FastAPI, Request, Header, Depends
from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import uvicorn

from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="sql_app/templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup_populate_db():
    db = SessionLocal()
    num_films = db.query(models.Film).count()
    if num_films == 0:
        films = [
            {"name": "Blade Runner", "director": "Ridley Scott"},
            {"name": "Pulp Fiction", "director": "Questin Tarantino"},
            {"name": "Mulholland Drive", "director": "David Lynch"},
            {"name": "Jurassic Park", "director": "Steven Spielberg"},
            {"name": "Tokyo Story", "director": "Yasujiro Ozu"},
            {"name": "Chungking Express", "director": "Kar-Wai Wong"},
        ]
        for film in films:
            db.add(models.Film(**film))
        db.commit()
    else:
        print(f"{num_films} already in DB")
    
    db.close()



@app.get('/index/', response_class=HTMLResponse)
def movielist(
    request: Request, 
    hx_request: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    page: int = 1
    ):
    N = 2
    OFFSET = (page - 1) * N
    films = db.query(models.Film).offset(OFFSET).limit(N)
    context = {'request': request, "films": films, "page": page}
    
    if hx_request:
        return templates.TemplateResponse("partials/table.html", context)
    return templates.TemplateResponse("index.html", context)





if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
    
    