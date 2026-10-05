from fastapi.templating import Jinja2Templates

from app.core.formatacao import brl, reais_input

templates = Jinja2Templates(directory="app/templates")
templates.env.filters["brl"] = brl
templates.env.filters["reais_input"] = reais_input