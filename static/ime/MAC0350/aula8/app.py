from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory=["templates"])
curtidas = {"curtidas": 0}

@app.get("/",response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.post("/curtir", response_class=HTMLResponse)
async def curtir():
    global curtidas
    curtidas["curtidas"] += 1
    return f"<p>Curtidas: {curtidas['curtidas']}</p>"

@app.delete("/curtir", response_class=HTMLResponse)
async def deletar_curtidas():
    global curtidas
    curtidas["curtidas"] = 0
    return f"<p>Curtidas: {curtidas['curtidas']}</p>"