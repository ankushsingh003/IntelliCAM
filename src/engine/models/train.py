"""
src/engine/models/train.py

Training script to generate the synthetic XGBoost model.
Uses scikit-learn to generate a dummy dataset of Five C vectors 
and trains a real XGBoost booster, saving it to disk.
"""
import logging
import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from configs.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_dummy_model():
    """Trains and saves a mock XGBoost model using synthetic data."""
    logger.info("Generating synthetic training data...")
    
    np.random.seed(42)
    n_samples = 5000
    
    # Generate 5Cs scores (0-100)
    character = np.random.normal(60, 20, n_samples).clip(0, 100)
    capacity = np.random.normal(60, 20, n_samples).clip(0, 100)
    capital = np.random.normal(55, 25, n_samples).clip(0, 100)
    collateral = np.random.normal(70, 15, n_samples).clip(0, 100)
    conditions = np.random.normal(50, 20, n_samples).clip(0, 100)
    
    # Generate specific flags
    bounce_count = np.random.poisson(1, n_samples)
    shell_flag = np.random.binomial(1, 0.05, n_samples)
    auto_reject = np.random.binomial(1, 0.02, n_samples)
    
    df = pd.DataFrame({
        "character_score": character,
        "capacity_score": capacity,
        "capital_score": capital,
        "collateral_score": collateral,
        "conditions_score": conditions,
        "bounce_count": bounce_count,
        "shell_risk_flag": shell_flag,
        "is_auto_reject": auto_reject
    })
    
    # Generate Target: Probability of Default (PD)
    # Higher scores = Lower PD
    base_pd = 1.0 - ((character + capacity + capital + collateral + conditions) / 500.0)
    base_pd += (bounce_count * 0.05)
    base_pd += (shell_flag * 0.3)
    base_pd = np.where(auto_reject == 1, 0.99, base_pd)
    base_pd = base_pd.clip(0.01, 0.99)
    
    # Convert PD to a binary default outcome for standard binary logistic regression
    y = np.random.binomial(1, base_pd)
    
    X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.2, random_state=42)
    
    logger.info("Training XGBoost...")
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)
    
    params = {
        'objective': 'binary:logistic',
        'eval_metric': 'auc',
        'max_depth': 4,
        'eta': 0.1,
        'random_state': 42
    }
    
    evals = [(dtrain, 'train'), (dtest, 'eval')]
    
    model = xgb.train(params, dtrain, num_boost_round=100, evals=evals, early_stopping_rounds=10, verbose_eval=False)
    
    out_path = settings.models_dir / "xgb_credit_model.json"
    settings.models_dir.mkdir(parents=True, exist_ok=True)
    model.save_model(str(out_path))
    
    logger.info(f"Model successfully saved to {out_path}")

if __name__ == "__main__":
    train_dummy_model()
