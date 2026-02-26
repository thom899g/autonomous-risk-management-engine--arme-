"""
ARME Configuration Manager
Centralized configuration with validation and environment-aware defaults
"""
import os
import logging
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ARMEConfig(BaseSettings):
    """Validated configuration schema for ARME"""
    
    # Firebase Configuration
    firebase_credentials_path: str = Field(
        default="./serviceAccountKey.json",
        description="Path to Firebase service account credentials"
    )
    firebase_database_url: str = Field(
        ...,
        description="Firebase Realtime Database URL"
    )
    
    # Trading Parameters
    default_exchange: str = Field(
        default="binance",
        description="Default cryptocurrency exchange"
    )
    max_position_size: float = Field(
        default=0.1,
        ge=0.01,
        le=0.5,
        description="Maximum position size as fraction of portfolio (1-50%)"
    )
    max_daily_drawdown: float = Field(
        default=0.05,
        ge=0.01,
        le=0.2,
        description="Maximum acceptable daily drawdown (1-20%)"
    )
    risk_free_rate: float = Field(
        default=0.02,
        ge=0,
        le=0.1,
        description="Annual risk-free rate for Sharpe ratio"
    )
    
    # Machine Learning
    model_update_frequency_hours: int = Field(
        default=24,
        ge=1,
        le=168,
        description="Frequency of model retraining in hours"
    )
    min_training_samples: int = Field(
        default=1000,
        ge=100,
        description="Minimum samples required for model training"
    )
    volatility_window_days: int = Field(
        default=30,
        ge=7,
        le=365,
        description="Window for volatility calculation in days"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    @validator('firebase_credentials_path')
    def validate_firebase_credentials(cls, v: str) -> str:
        """Validate Firebase credentials file exists"""
        if not os.path.exists(v):
            logging.warning(f"Firebase credentials file not found: {v}")
            # In production, this would trigger a Telegram alert
        return v
    
    class Config:
        env_prefix = "ARME_"
        case_sensitive = False
        extra = "ignore"

# Singleton configuration instance
_config_instance: Optional[ARMEConfig] = None

def get_config() -> ARMEConfig:
    """Get or create singleton configuration instance"""
    global _config_instance
    if _config_instance is None:
        try:
            _config_instance = ARMEConfig()
            logging.info(f"Configuration loaded from environment")
        except Exception as e:
            logging.error(f"Configuration error: {e}")
            raise
    return _config_instance

def update_config(updates: Dict[str, Any]) -> ARMEConfig:
    """Dynamically update configuration (for adaptive learning)"""
    global _config_instance
    config = get_config()
    
    # Create new config with updates
    updated_dict = config.dict()
    updated_dict.update(updates)
    _config_instance = ARMEConfig(**updated_dict)
    
    logging.info(f"Configuration updated with: {updates}")
    return _config_instance