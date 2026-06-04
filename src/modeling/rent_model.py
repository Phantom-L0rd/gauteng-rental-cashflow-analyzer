import os
import json
import joblib
import logging
from datetime import datetime
import numpy as np

from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from src.utils.data_controller import load_parquet, save_config


class RentModel:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("RentModel")
        self.pipeline = None
        self.model_root = "models/rent_price"
        
        os.makedirs(self.model_root, exist_ok=True)

    def build_pipeline(self, is_prod=False):
        numerical = self.config["features"]["numerical"]
        categorical = self.config["features"]["categorical"]

        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
                ("num", "passthrough", numerical)
            ]
        )

        model_cfg = self.config["model"]

        if is_prod:
            params = self.config["model"]["prod_params"]
            regressor = RandomForestRegressor(
                **params, 
                random_state=model_cfg['random_state'], 
                n_jobs=-1)
        else:
            param_dist = self.config['param_dist']

            base_rf = RandomForestRegressor(random_state=model_cfg['random_state'], n_jobs=-1)

            regressor = RandomizedSearchCV(
                estimator=base_rf,
                param_distributions=param_dist,
                n_iter=20,
                cv=5,
                scoring='neg_mean_squared_error',
                verbose=2,
                random_state=model_cfg['random_state'],
                n_jobs=-1
            )
            

        self.pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", regressor)
        ])

    def train(self, df):
        target_col = self.config["target"]

        X = df.drop(columns=[target_col])
        y = df[target_col]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.config["model"]["test_size"],
            random_state=self.config["model"]['random_state']
        )

        self.build_pipeline()

        self.logger.info("Training model...")
        self.pipeline.fit(X_train, y_train)

        self.logger.info("Training complete!")

        rf_search = self.pipeline.named_steps['regressor']
        best_params = rf_search.best_params_
        metrics = self.evaluate(X_test, y_test, best_params)

        return metrics, best_params

    def evaluate(self, X_test, y_test, best_params):
        preds = self.pipeline.predict(X_test)

        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        mae = float(mean_absolute_error(y_test, preds))
        r2 = float(r2_score(y_test, preds))

        self.logger.info(f"RMSE: {rmse}")
        self.logger.info(f"MAE: {mae}")
        self.logger.info(f"R2: {r2}")
        self.logger.info(f"Best Parameters: {best_params}")

        return {"rmse": rmse, "mae": mae, "r2": r2}

    def update_registry(self, metrics, best_params):
        registry_path = os.path.join(self.model_root, "registry.json")
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M")

        if not os.path.exists(registry_path):
            registry = {
                "models": []
            }
        else:
            with open(registry_path, "r") as f:
                registry = json.load(f)
        
        registry["models"].append({
            "training_date" : timestamp,
            "metrics": metrics,
            "best_params": best_params
        })

        # Save registry
        with open(registry_path, "w") as f:
            json.dump(registry, f, indent=4)
    
    def should_promote(self, new_metrics, old_metrics, threshold=0.02):
        """
        Promote only if RMSE improvement is > 2% 
        and R2 hasn't dropped.
        """
        rmse_improvement = (old_metrics['rmse'] - new_metrics['rmse']) / old_metrics['rmse']
        
        if rmse_improvement > threshold and new_metrics['r2'] >= old_metrics['r2']:
            return True
        return False
    
    def save_prod_params(self, best_params, metrics):
        self.config['model']['version'] += 1 
        self.config['model']['prod_params'] = best_params
        self.config['model']['production_metrics'] = {
            'rmse': float(metrics['rmse']),
            'r2': float(metrics['r2']),
            'mae': float(metrics['mae'])
        }

        save_config("configs/model_config.yaml", self.config)
        self.logger.info("Successfully saved best params to config")

    def train_production(self, df):
        """Trains on the entire dataset with no split for maximum accuracy"""
        target_col = self.config["target"]
        X = df.drop(columns=[target_col])
        y = df[target_col]

        self.build_pipeline(is_prod=True)
        self.logger.info("🚀 Training Production Model on 100% of data...")
        self.pipeline.fit(X, y)
        
        # Save with a special 'prod' tag
        version = self.config['model']['version']
        save_dir = os.path.join(self.model_root, "production")
        os.makedirs(save_dir, exist_ok=True)
        joblib.dump(self.pipeline, os.path.join(save_dir, f"prod_model_v{version}.joblib"))
        self.logger.info(f"Production Model Version {version} complete and saved!")
    
    def run(self, force_feature_rebuild=False):
        """
        Executes the full training workflow.
        Set force_feature_rebuild=True if you want to refresh features 
        even if the file exists.
        """
        self.logger.info("🚀 Initializing model training process...")

        # 1. Load rental data
        df = load_parquet("data/2_silver_cleaned/type=rent/listings.parquet")

        numerical = self.config["features"]["numerical"]
        categorical = self.config["features"]["categorical"]
        target_col = self.config['target']
        df_processed = df[numerical+categorical+[target_col]]
        df_processed = df_processed.drop_duplicates()

        self.logger.info(f"Loaded {len(df_processed)} samples for training.")

        # 2. Train Model
        metrics, best_params = self.train(df_processed)

        # 3. Update Registry
        self.update_registry(metrics, best_params)

        # 4. Check if best model
        # if self.should_promote(metrics, self.config['model']['production_metrics']):
        #     self.logger.info("New best model found...")
        #     self.save_prod_params(best_params, metrics)
        #     self.train_production(df_processed)

        self.logger.info(f"🏁 Training complete!")

