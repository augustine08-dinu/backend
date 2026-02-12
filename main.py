from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

from database import engine, SessionLocal
import models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ SECURITY CONFIG ------------------

SECRET_KEY = "CHANGE_THIS_TO_RANDOM_SECRET_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")


# ------------------ DATABASE ------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------ TOKEN CREATION ------------------

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ------------------ LOGIN ROUTE ------------------

@app.post("/admin/login")
def admin_login(credentials: schemas.AdminLogin):

    username = credentials.username
    password = credentials.password

    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token({"sub": username})
    return {"token": token}


# ------------------ TOKEN VERIFY ------------------

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username != ADMIN_USERNAME:
            raise HTTPException(status_code=401, detail="Invalid user")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ------------------ PUBLIC REVIEW SUBMIT ------------------

@app.post("/review", response_model=schemas.ReviewResponse)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    new_review = models.Review(**review.dict())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


# ------------------ PROTECTED REVIEWS ------------------

@app.get("/reviews", response_model=list[schemas.ReviewResponse])
def get_reviews(
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    return db.query(models.Review) \
        .order_by(models.Review.created_at.desc()) \
        .all()



