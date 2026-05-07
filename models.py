from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    keywords = Column(String) # Comma separated
    sources = relationship("Source", back_populates="project")

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String) # e.g., 'Reddit', 'Forum', 'X'
    url = Column(String)
    latency_metric = Column(String) # 'Real-time', 'Daily', 'Weekly'
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="sources")
    data_items = relationship("AcquiredData", back_populates="source")

class AcquiredData(Base):
    __tablename__ = "acquired_data"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    url = Column(String)
    
    source = relationship("Source", back_populates="data_items")
    analysis_result = relationship("AnalysisResult", back_populates="data_item", uselist=False)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True, index=True)
    data_id = Column(Integer, ForeignKey("acquired_data.id"))
    sentiment_score = Column(Float) # -1.0 to 1.0
    entities = Column(String) # JSON string
    safety_issue_flag = Column(Boolean, default=False)
    pii_flag = Column(Boolean, default=False)
    explainability_text = Column(Text)
    
    data_item = relationship("AcquiredData", back_populates="analysis_result")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
