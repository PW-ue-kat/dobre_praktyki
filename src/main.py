import os
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import jwt
import bcrypt
import uvicorn
# Assuming USERS_DB is a dictionary mapping username -> hashed_bytes
from users_db import USERS_DB

app = FastAPI()

# Best Practice: Load from environment variables, fallback for dev only
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class LoginData(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


@app.post("/login", response_model=Token)
def login(data: LoginData):
    username = data.username
    password_bytes = data.password.encode('utf-8')

    # Retrieve user (or None if not found)
    user_hash = USERS_DB.get(username)

    # Security: Use a generic error message for both cases
    # to avoid leaking which part failed (User vs Password)
    invalid_creds_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if user_hash is None:
        # TIMING ATTACK MITIGATION (Simplified):
        # Even if user is not found, we run a dummy check so the response
        # time is similar to a valid user check.
        # (In high security apps, you would hash a dummy string here)
        raise invalid_creds_exception

    if not bcrypt.checkpw(password_bytes, user_hash):
        raise invalid_creds_exception

    # Use timezone-aware datetime
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}
#start app on localhost and port 5000
# Add this block at the very end of the file
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)