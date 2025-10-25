import pandas as pd
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
import joblib # For saving the model
import numpy as np

# 1. Load and prepare data
data = pd.read_csv("training_data.csv")

# Define your feature columns
feature_cols = [
    "karma_ratio", #returns float of the ratio of post karma to comment karma
    "active_karma_rate", #returns float of the avg karma per day in the last 30 days or less of activity
    "age_days", #returns int of the age of the account in days
    "biggest_timestamp", #returns float the largest time between activity in Unix
    "burst_activity_ratio", #returns float of the ratio of activity that takes place within 65 seconds
    "first_activity_delay", #returns int of the days of how long it took from account creation to first activity
    "short_comment_ratio", #returns float of the ratio of comments under 20 characters
    "avg_comment_similarity", #returns float in the pairwise similarity score of the last 10 comments
    "verified_email", #returns a boolean of if the account has a verified email
    "trophy_count", #returns int of how many trophies an account has
    "name_pattern", #returns boolean if an account has a Word-Word-Num regex name pattern
    "icon_default", #returns boolean of if the account has the default icon
    "popular_subreddits_ratio", #returns the ratio of activity of common karma farming subreddits given a list of subs
    "scammy_subreddits_ratio" #returns the ratio of activity of scam/spam/selling subs given a list of keywords
]

X = data[feature_cols].values
y = data["is_bot"].values

# 2. Define Model and Hyperparameter Grid
# We're using RandomForest, which doesn't require feature scaling.
model = RandomForestClassifier(random_state=42)

# Define a "grid" of parameters to test.
# We'll test different numbers of trees and tree depths.
param_grid = {
    'n_estimators': [50, 100, 150, 200],
    'max_depth': [None, 5, 10, 15],
    'min_samples_leaf': [1, 2, 4]
}

# 3. Set up Cross-Validation and Grid Search
# Use K-Fold CV. With n_splits=10, we use 90 users for training
# and 10 for testing, repeated 10 times.
cv_strategy = KFold(n_splits=10, shuffle=True, random_state=42)

# GridSearchCV will automatically test all parameter combinations
# using our 10-fold cross-validation strategy.
grid_search = GridSearchCV(
    estimator=model,
    param_grid=param_grid,
    cv=cv_strategy,
    scoring='accuracy',
    n_jobs=-1 # Use all available CPU cores
)

# 4. Run the search
# This fits the model, tunes parameters, and finds the best
# cross-validated score all in one step.
grid_search.fit(X, y)

# 5. Check accuracy
# This is now the *average* accuracy across all 10 folds,
# which is much more reliable than your single-split score.
print(f"Best Cross-Validated Accuracy: {grid_search.best_score_ * 100:.2f}%")
print(f"Best Parameters Found: {grid_search.best_params_}")

# 6. Save your best trained model
# GridSearchCV automatically retrains the best model on ALL data.
final_model = grid_search.best_estimator_
joblib.dump(final_model, "bot_detector_model.pkl")
# We no longer need to save the scaler.pkl

# 7. Inspect feature importances
# This replaces the "weights" from Logistic Regression.
# It shows which features the model found most predictive.
print("\nLearned Feature Importances:")
importances = final_model.feature_importances_
sorted_indices = np.argsort(importances)[::-1]

for i in sorted_indices:
    print(f"  {feature_cols[i]}: {importances[i]:.4f}")