from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    gemini_api_key: str
    groq_api_key: str = ""  
    slack_webhook_url: str
    webhook_secret_token: str
    notion_api_key: str = ""      
    notion_database_id: str = ""  

    class Config:
        env_file = ".env"
        extra = "ignore"  

settings = Settings()