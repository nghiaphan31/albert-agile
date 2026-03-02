# serve.py — Exposition LangServe du graphe Agile
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from langserve import add_routes

from graph.graph import graph

app = FastAPI(title="Agile Graph")
add_routes(app, graph, path="/agile")
