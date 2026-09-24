"""Select an Autoencoder anomaly threshold using validation data ONLY.

Run from the repository root:
    python src/detection/select_autoencoder_threshold.py

Prediction rule: reconstruction_mse >= selected_threshold -> attack.
Selection: maximum validation F1, highest threshold in case of ties.
The held-out test set is never accessed by this script.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

ROOT = Path(__file__).resolve().parents[2]
with (ROOT / 'config' / 'project_config.json').open(encoding='utf-8') as f:
    config = json.load(f)
results_dir = ROOT / config['paths']['results'] / 'autoencoder'
scores_file = results_dir / 'validation_scores.csv'
df = pd.read_csv(scores_file)
required = {'event_id', 'is_attack', 'reconstruction_mse'}
if not required.issubset(df.columns):
    raise ValueError(f'Missing columns: {sorted(required - set(df.columns))}')
if df.empty or df[list(required)].isna().any().any():
    raise ValueError('Validation scores are empty or contain missing values.')
if not df.event_id.is_unique:
    raise ValueError('Duplicate validation event IDs.')
if not df.is_attack.isin([0, 1]).all():
    raise ValueError('Labels must be binary.')
scores = df.reconstruction_mse.to_numpy(dtype=np.float64)
y_true = df.is_attack.to_numpy(dtype=int)
if not np.isfinite(scores).all() or (scores < 0).any():
    raise ValueError('Reconstruction MSE must be finite and nonnegative.')
if len(np.unique(y_true)) < 2:
    raise ValueError('Threshold selection requires both normal and attack events.')

# Include all distinct observed scores and a candidate that predicts all normal.
# Evaluate in ascending order, updating on equal F1 to prefer higher thresholds.
thresholds = np.append(np.unique(scores), np.nextafter(scores.max(), np.inf))
best = None
for threshold in thresholds:
    y_pred = (scores >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average='binary', zero_division=0
    )
    if best is None or f1 >= best['f1']:
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        best = {
            'threshold': float(threshold),
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1),
            'confusion_matrix': {
                'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp)
            },
        }

output = {
    'model': 'autoencoder',
    'dataset': 'validation',
    'score_column': 'reconstruction_mse',
    'prediction_rule': 'reconstruction_mse >= threshold',
    'selection_method': 'maximize validation F1 over unique scores and all-normal candidate',
    'tie_break': 'highest threshold',
    'validation_events': int(len(df)),
    'normal_events': int((y_true == 0).sum()),
    'attack_events': int((y_true == 1).sum()),
    'selected_threshold': best['threshold'],
    'precision': best['precision'],
    'recall': best['recall'],
    'f1': best['f1'],
    'confusion_matrix': best['confusion_matrix'],
    'test_set_used': False,
}
results_dir.mkdir(parents=True, exist_ok=True)
output_file = results_dir / 'threshold_selection.json'
with output_file.open('w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('Autoencoder - Threshold Selection')
print('---------------------------------')
print(f"Validation events: {output['validation_events']}")
print(f"Selected threshold: {best['threshold']:.6f}")
print('Validation metrics:')
print(f"Precision: {best['precision']:.4f}")
print(f"Recall:    {best['recall']:.4f}")
print(f"F1-score:  {best['f1']:.4f}")
print('Confusion matrix:')
for name, count in best['confusion_matrix'].items():
    print(f'{name.upper()}: {count}')
print(f'Results saved to: {output_file}')
print('Held-out test set remains untouched.')
