from fastapi import FastAPI
api = FastAPI()

@api.get("/")
def root():
    return {"ok": True, "msg": "B3 works"}
