from fastapi import FastAPI, Depends, HTTPException, status, Cookie, Response, Request
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Annotated
from pydantic import BaseModel


app = FastAPI()

class User(BaseModel):
    name: str
    password: str
    bio: str

class LoginModel(BaseModel):
    user: str
    password: str

users = {}

@app.get("/", response_class=HTMLResponse)
async def root_route():
    return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js" integrity="sha384-/TgkGk7p307TH7EXJDuUlgG3Ce1UVolAOFopFekQkkXihi5u/6OCvVKyz1W+idaz" crossorigin="anonymous"></script>
            <script src="https://unpkg.com/htmx.org@1.9.12/dist/ext/json-enc.js"></script>
            <title>Requests</title>
            <style>
                body {
                    display: flex;
                    gap: 2.5vw;
                    justify-content: center;
                    min-height: 90vh;
                    background-color: #292827;
                    color: #e0e0e0;
                }

                .secao-interacao, .secao-respostas {
                    border: 2px solid #ff690a;
                    border-radius: 15px;
                    padding: 20px;
                    width: 50%;
                    height: auto;
                }

                .secao-interacao, form {
                    display: flex;
                    flex-direction: column;
                }

                @media(orientation: portrait) {
                    body {
                        flex-direction: column;
                        gap: 2.5vh;
                        min-height: auto;
                    }

                    .secao-interacao, .secao-respostas {
                        min-height: 30vh;
                        width: auto;
                    }
                }

                #json-insert {
                    color: #ff690a;
                    font-size: xx-large;
                }

                /* Estilização dos elementos de interação com inputs */
                label {
                    margin-top: 15px;
                    margin-bottom: 5px;
                    font-weight: bold;
                    font-size: 0.9rem;
                    color: #ff690a;
                }

                input[type="text"], 
                input[type="number"] {
                    background-color: #1e1e1e;
                    border: 1px solid #444;
                    border-radius: 8px;
                    padding: 12px 15px;
                    color: #e0e0e0;
                    font-size: 1rem;
                    transition: all 0.3s ease;
                    outline: none;
                }

                input[type="text"]:hover, 
                input[type="number"]:hover {
                    border-color: #666;
                }

                input[type="text"]:focus, 
                input[type="number"]:focus {
                    border-color: #ff690a;
                    box-shadow: 0 0 8px rgba(255, 105, 10, 0.3);
                    background-color: #252525;
                }

                input[type="submit"], button {
                    margin-top: 20px;
                    padding: 12px;
                    border-radius: 8px;
                    border: none;
                    background-color: #ff690a;
                    color: #fff;
                    font-weight: bold;
                    cursor: pointer;
                    transition: transform 0.1s, background-color 0.2s;
                }

                input[type="submit"]:hover, button:hover {
                    background-color: #e55a00;
                }

                input[type="submit"]:active, button:active {
                    transform: scale(0.98);
                }

                hr {
                    border: 0;
                    border-top: 1px solid #444;
                    margin: 25px 0;
                    width: 100%;
                }
            </style>
        </head>
        <body>
            <div class="secao-interacao">
                <h1>Requests</h1>
                <form hx-post="/users"
                    hx-trigger="submit"
                    hx-target="#json-insert"
                    hx-swap="innerHTML"
                    hx-ext="json-enc">  
                    <label for="name">Nome do usuário</label>
                    <input type="text" name="name">
                    <label for="password">Senha</label>
                    <input type="text" name="password">
                    <label for="bio">Bio do Usuario></label>
                    <textarea id="bio" name="bio"></textarea>
                    <input type="submit">
                </form>
                <hr>
                <input type="number"
                    name="index"
                    hx-get="/users"
                    hx-trigger="input changed"
                    hx-target="#json-insert"
                    hx-swap="innerHTML"
                    placeholder="Índice do usuário">
                <hr>
                <button hx-get="/users"
                        hx-target="#json-insert"
                        hx-swap="innerHTML">
                    Obter todos os usuários
                </button>
                <hr>
                <button hx-delete="/users"
                        hx-target="#json-insert"
                        hx-swap="innerHTML">
                    Apagar todos os usuários
                </button>
            </div>

            <div class="secao-respostas">
                <h1>Respostas</h1>
                <div id="json-insert"></div>
            </div>
        </body>
        </html>
    """

@app.post("/users")
async def create_user(user: User):
    if user.name not in users.keys():
        users[user.name] = user
    else:
        raise HTTPException(status_code=401, detail=f"Cannot overwrite an existing user that has the password {user.password}")
    return JSONResponse(status_code=200, content={"message": f"Successfully created and stored user {user.name}"})

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js" integrity="sha384-/TgkGk7p307TH7EXJDuUlgG3Ce1UVolAOFopFekQkkXihi5u/6OCvVKyz1W+idaz" crossorigin="anonymous"></script>
            <script src="https://unpkg.com/htmx.org@1.9.12/dist/ext/json-enc.js"></script>
            <title>Requests</title>
            <style>
                body {
                    display: flex;
                    gap: 2.5vw;
                    justify-content: center;
                    min-height: 90vh;
                    background-color: #292827;
                    color: #e0e0e0;
                }

                .secao-interacao, .secao-respostas {
                    border: 2px solid #ff690a;
                    border-radius: 15px;
                    padding: 20px;
                    width: 50%;
                    height: auto;
                }

                .secao-interacao, form {
                    display: flex;
                    flex-direction: column;
                }

                @media(orientation: portrait) {
                    body {
                        flex-direction: column;
                        gap: 2.5vh;
                        min-height: auto;
                    }

                    .secao-interacao, .secao-respostas {
                        min-height: 30vh;
                        width: auto;
                    }
                }

                #json-insert {
                    color: #ff690a;
                    font-size: xx-large;
                }

                /* Estilização dos elementos de interação com inputs */
                label {
                    margin-top: 15px;
                    margin-bottom: 5px;
                    font-weight: bold;
                    font-size: 0.9rem;
                    color: #ff690a;
                }

                input[type="text"], 
                input[type="number"] {
                    background-color: #1e1e1e;
                    border: 1px solid #444;
                    border-radius: 8px;
                    padding: 12px 15px;
                    color: #e0e0e0;
                    font-size: 1rem;
                    transition: all 0.3s ease;
                    outline: none;
                }

                input[type="text"]:hover, 
                input[type="number"]:hover {
                    border-color: #666;
                }

                input[type="text"]:focus, 
                input[type="number"]:focus {
                    border-color: #ff690a;
                    box-shadow: 0 0 8px rgba(255, 105, 10, 0.3);
                    background-color: #252525;
                }

                input[type="submit"], button {
                    margin-top: 20px;
                    padding: 12px;
                    border-radius: 8px;
                    border: none;
                    background-color: #ff690a;
                    color: #fff;
                    font-weight: bold;
                    cursor: pointer;
                    transition: transform 0.1s, background-color 0.2s;
                }

                input[type="submit"]:hover, button:hover {
                    background-color: #e55a00;
                }

                input[type="submit"]:active, button:active {
                    transform: scale(0.98);
                }

                hr {
                    border: 0;
                    border-top: 1px solid #444;
                    margin: 25px 0;
                    width: 100%;
                }
            </style>
        </head>
        <body>
            <div class="secao-interacao">
                <h1>Requests</h1>
                <form hx-post="/login"
                    hx-trigger="submit"
                    hx-target="#json-insert"
                    hx-swap="innerHTML"
                    hx-ext="json-enc">  
                    <label for="user">User</label>
                    <input type="text" name="user">
                    <label for="password">Senha</label>
                    <input type="text" name="password">
                    <input type="submit">
                </form>
            </div>
            <div class="secao-respostas">
                <h1>Respostas</h1>
                <div id="json-insert"></div>
            </div>
        </body>
        </html>
    """

@app.post("/login")
def login_flow(user: LoginModel, response: Response):
    if user.user not in users.keys():
        raise HTTPException(status_code=401, detail=f"User does not exist, please use one of the following existing users: {list(users.keys())}")
    if user.password != users[user.user].password:
        raise HTTPException(status_code=401, detail=f"Have you forgotten your password? Your password is {users[user.user].password}")
    response = JSONResponse(status_code=200, content={"message": "Successfully logged in!"})
    response.set_cookie(key="SESSUSR", value=user.user)
    return response

def get_logged_user(SESSUSR: Annotated[str | None, Cookie()] = None):
    if not SESSUSR:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado: você não está logado."
        )
    try:
        return users[SESSUSR]
    except KeyError:
        raise HTTPException(
            status_code=418,
            detail="Usuario nao existe mais?"
        )

@app.get("/home", response_class=HTMLResponse)
def profile_page(current_user: User = Depends(get_logged_user)):
    return f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    background-color: #292827;
                    color: #e0e0e0;
                    font-family: sans-serif;
                    display: flex;
                    justify-content: center;
                    padding: 40px;
                }}
                .card {{
                    border: 2px solid #ff690a;
                    border-radius: 15px;
                    padding: 30px;
                    width: 400px;
                }}
                h1 {{ color: #ff690a; }}
                p {{ margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Nome: {current_user.name}</h1>
                <p>Bio: {current_user.bio}</p>
            </div>
        </body>
        </html>"""

