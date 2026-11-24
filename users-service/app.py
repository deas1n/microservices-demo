from fastapi import FastAPI, HTTPException

app = FastAPI(title="Users Service")

USERS = {
    1: {"id": 1, "name": "Олена", "role": "Developer"},
    2: {"id": 2, "name": "Максим", "role": "QA"},
    3: {"id": 3, "name": "Ірина", "role": "Product Manager"},
}


@app.get("/health")
def health():
    return {"status": "ok", "service": "users-service"}


@app.get("/users")
def get_users():
    return list(USERS.values())


@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user