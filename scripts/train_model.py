import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

from src.config import MODEL_PATH, SAMPLE_DATA_PATH, ensure_project_dirs
from src.seed_data import generate_sample_dataset


def train() -> None:
    ensure_project_dirs()
    # Regenerate synthetic data so newly added obfuscation patterns are included.
    df = generate_sample_dataset(force=True)
    x_train, x_test, y_train, y_test = train_test_split(
        df["text_for_model"],
        df["label_multiclass"],
        test_size=0.25,
        random_state=42,
        stratify=df["label_multiclass"],
    )

    pipeline = Pipeline(
        steps=[
            (
                "features",
                FeatureUnion(
                    [
                        ("char_tfidf", TfidfVectorizer(analyzer="char", ngram_range=(3, 5), min_df=1)),
                        ("word_tfidf", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=1)),
                    ]
                ),
            ),
            ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)),
        ]
    )

    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)
    print(classification_report(y_test, predictions))
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
