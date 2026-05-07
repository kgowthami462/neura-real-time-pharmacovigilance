import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Social Listening API")

from passlib.context import CryptContext
from jose import jwt
import datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

SECRET_KEY = "super-secret-key-for-hackathon"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password[:72], hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password[:72])

def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

class UserCreate(BaseModel):
    email: str
    password: str

@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Mount static files for the frontend
import os
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.on_event("startup")
def populate_demo_data():
    db = next(get_db())
    if db.query(models.Project).count() == 0:
        demo_proj = models.Project(name="Ozempic Safety Monitoring", description="Monitoring adverse events for Ozempic", keywords="Ozempic, Wegovy, Semaglutide, nausea, vomiting")
        db.add(demo_proj)
        db.commit()
        db.refresh(demo_proj)
        
        demo_source = models.Source(project_id=demo_proj.id, type="Reddit", url="https://www.reddit.com/r/Ozempic/", latency_metric="Real-time")
        db.add(demo_source)
        db.commit()
        db.refresh(demo_source)
        
        data1 = models.AcquiredData(source_id=demo_source.id, content="I've been on Ozempic for 3 weeks. Lost 10 pounds! No side effects at all. Feeling great.", url="https://reddit.com/r/Ozempic/mock1")
        db.add(data1)
        db.commit()
        db.refresh(data1)
        db.add(models.AnalysisResult(data_id=data1.id, sentiment_score=0.9, entities='{"drugs": ["Ozempic"], "symptoms": []}', safety_issue_flag=False, explainability_text="Patient reports positive weight loss and explicitly states no side effects.", pii_flag=False))
        
        data2 = models.AcquiredData(source_id=demo_source.id, content="Woke up in the middle of the night with severe stomach pain and vomiting after my increased dose of Semaglutide. Going to the ER.", url="https://reddit.com/r/Ozempic/mock2")
        db.add(data2)
        db.commit()
        db.refresh(data2)
        db.add(models.AnalysisResult(data_id=data2.id, sentiment_score=-0.95, entities='{"drugs": ["Semaglutide"], "symptoms": ["severe stomach pain", "vomiting"]}', safety_issue_flag=True, explainability_text="CRITICAL: Patient reports severe stomach pain and vomiting requiring an ER visit.", pii_flag=False))
        
        data3 = models.AcquiredData(source_id=demo_source.id, content="Does anyone know if taking Ozempic makes you slightly tired in the afternoon?", url="https://reddit.com/r/Ozempic/mock3")
        db.add(data3)
        db.commit()
        db.refresh(data3)
        db.add(models.AnalysisResult(data_id=data3.id, sentiment_score=-0.2, entities='{"drugs": ["Ozempic"], "symptoms": ["tiredness"]}', safety_issue_flag=False, explainability_text="Mild fatigue reported, common and not a critical safety concern.", pii_flag=False))
        
        db.commit()

# Pydantic models for request/response
class ProjectCreate(BaseModel):
    name: str
    description: str
    keywords: str

class SourceCreate(BaseModel):
    project_id: int
    type: str
    url: str
    latency_metric: str

@app.post("/projects/")
def create_project(project: ProjectCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/")
def read_projects(skip: int = 0, limit: int = 100, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects

@app.post("/sources/")
def create_source(source: SourceCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_source = models.Source(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

@app.get("/sources/{project_id}")
def read_sources(project_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Source).filter(models.Source.project_id == project_id).all()

class CrawlRequest(BaseModel):
    pass

@app.post("/trigger-crawl/{source_id}")
def trigger_crawl(source_id: int, crawl_req: CrawlRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    source = db.query(models.Source).filter(models.Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    project = db.query(models.Project).filter(models.Project.id == source.project_id).first()
    
    content = ""
    post_url = ""
    
    # Real Reddit Scraping
    if source.type.lower() == "reddit":
        try:
            import requests
            headers = {'User-agent': 'NEURA-Bot 1.0'}
            # Format Reddit URL to fetch JSON
            url = source.url.rstrip('/') + "/new.json?limit=5"
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            data = r.json()
            
            for child in data['data']['children']:
                post = child['data']
                if post.get('selftext'):
                    content = post['title'] + "\n" + post['selftext']
                    post_url = "https://reddit.com" + post['permalink']
                    break
            
            if not content:
                content = "Could not find any recent text posts on this subreddit."
                post_url = source.url
        except Exception as e:
            content = f"Error fetching from Reddit: {str(e)}"
            post_url = source.url
            
    # Generic Fallback Scraper if not Reddit or Reddit failed to populate content
    if not content or source.type.lower() != "reddit":
        import requests
        from bs4 import BeautifulSoup
        headers = {'User-agent': 'NEURA-Agent 1.0'}
        try:
            r = requests.get(source.url, headers=headers, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            content = soup.get_text(separator=' ', strip=True)[:3000] # Cap at 3k chars for prompt limits
            post_url = source.url
        except Exception as e:
            # Fallback to mock data if even the generic scraper fails
            content = f"I've been taking one of the drugs mentioned ({project.keywords}) and I feel terrible nausea. Is this normal?"
            post_url = f"{source.url}/post/mock123"
    
    data_item = models.AcquiredData(
        source_id=source.id,
        content=content,
        url=post_url
    )
    db.add(data_item)
    db.commit()
    db.refresh(data_item)
    
    # Real LLM Analysis using Gemini
    sentiment_score = 0.0
    entities = "{}"
    safety_issue_flag = False
    explainability_text = "No API Key provided. Mock analysis used."
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "YOUR_API_KEY_HERE":
        try:
            from google import genai
            from google.genai import types
            import json
            
            client = genai.Client(api_key=api_key)
            
            prompt = f"""
            Analyze the following social media post for pharmacovigilance and patient safety.
            The project keywords being monitored are: {project.keywords}
            
            Post:
            "{content}"
            
            Return ONLY a valid JSON object with these exact keys:
            - sentiment_score: a float between -1.0 (very negative) and 1.0 (very positive)
            - entities: a JSON string containing arrays of "symptoms" and "drugs" found.
            - safety_issue_flag: boolean true if there is an adverse event or safety concern reported.
            - explainability_text: a short sentence explaining why you flagged it or didn't.
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            
            result = json.loads(response.text)
            sentiment_score = float(result.get("sentiment_score", 0))
            entities = result.get("entities", "{}") or "{}"
            if isinstance(entities, dict):
                entities = json.dumps(entities)
            safety_issue_flag = bool(result.get("safety_issue_flag", False))
            explainability_text = result.get("explainability_text", "AI Analysis complete.")
            
        except Exception as e:
            explainability_text = f"LLM Error: {str(e)}"
            safety_issue_flag = True
    else:
        sentiment_score = -0.8
        entities = '{"symptom": ["nausea"]}'
        safety_issue_flag = True
        explainability_text = "Mock analysis: High confidence adverse event due to mention of nausea."

    analysis = models.AnalysisResult(
        data_id=data_item.id,
        sentiment_score=sentiment_score,
        entities=entities,
        safety_issue_flag=safety_issue_flag,
        pii_flag=False,
        explainability_text=explainability_text
    )
    db.add(analysis)
    db.commit()
    
    return {"message": "Crawl completed successfully", "data_id": data_item.id}

@app.get("/signals/")
def get_signals(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    signals = db.query(models.AnalysisResult).join(models.AcquiredData).all()
    results = []
    for s in signals:
        results.append({
            "id": s.id,
            "content": s.data_item.content,
            "url": s.data_item.url,
            "sentiment": s.sentiment_score,
            "entities": s.entities,
            "safety_issue": s.safety_issue_flag,
            "explanation": s.explainability_text,
            "timestamp": s.data_item.timestamp
        })
    return results

class AgenticRequest(BaseModel):
    url: str

@app.post("/agentic-onboard")
def agentic_onboard(req: AgenticRequest, current_user: models.User = Depends(get_current_user)):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        raise HTTPException(status_code=500, detail="Server misconfiguration: GEMINI_API_KEY not found in environment.")
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {'User-agent': 'NEURA-Agent 1.0'}
        r = requests.get(req.url, headers=headers, timeout=10)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, 'html.parser')
        
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
            
        text_content = soup.get_text(separator=' ', strip=True)[:10000]
        
        from google import genai
        from google.genai import types
        import json
        
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        You are an expert AI Data Engineer. I am providing you with the text content of a website: {req.url}
        Analyze the structure and content to generate a Web Scraping Configuration for a social listening project.
        
        Website Content Snippet:
        "{text_content}"
        
        Return a JSON object with:
        - "platform_type": What kind of site is this? (e.g. "Forum", "Blog", "Social Media", "News")
        - "suggested_selectors": A JSON object mapping standard fields (title, body, author, date) to CSS selectors you guess might work based on standard structures, or explain how it should be scraped.
        - "pagination_strategy": How would a crawler likely paginate this site?
        - "confidence_score": Float 0-1 on how confident you are that we can scrape this reliably.
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        result = json.loads(response.text)
        return {"status": "success", "configuration": result}
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agentic Analysis failed: {str(e)}")

@app.get("/")
def read_root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")

@app.get("/portal")
def read_portal():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/portal.html")
