"""Event-level Isolation Forest sensitivity diagnostic (NOT SHAP/causal attribution).

Run from repository root:
    python src/explainability/explain_isolation_forest.py --event-id 3505

For each original field, replace its transformed feature block with a
representative NORMAL-TRAINING value, then recompute the frozen detector's
anomaly score. All other fields remain unchanged. The replacements can create
unrealistic combinations; deltas are diagnostic, not causal importance.
"""
import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--event-id', type=int, required=True)
    args = parser.parse_args()

    with (ROOT / 'config/project_config.json').open(encoding='utf-8') as f:
        cfg = json.load(f)
    feat_dir = ROOT / cfg['paths']['processed_data'] / 'features'
    model_dir = ROOT / cfg['paths']['models'] / 'isolation_forest'
    model = joblib.load(model_dir / 'isolation_forest.joblib')
    with (model_dir / 'feature_names.json').open(encoding='utf-8') as f:
        expected = json.load(f)
    train = pd.read_csv(feat_dir / 'train_normal_features.csv')
    test = pd.read_csv(feat_dir / 'test_features.csv')
    meta = pd.read_csv(feat_dir / 'test_metadata.csv')
    if train.columns.tolist() != expected or test.columns.tolist() != expected:
        raise ValueError('Feature schema differs from frozen model schema.')
    if len(test) != len(meta) or not meta.event_id.is_unique:
        raise ValueError('Test features and metadata are not aligned.')
    if not meta.is_attack.isin([0, 1]).all():
        raise ValueError('Invalid test labels.')
    if not np.isfinite(train.to_numpy(dtype=float)).all() or not np.isfinite(test.to_numpy(dtype=float)).all():
        raise ValueError('Invalid feature values.')
    selected = np.flatnonzero(meta.event_id.to_numpy() == args.event_id)
    if len(selected) != 1:
        raise ValueError('Event ID not found exactly once in held-out test partition.')
    pos = int(selected[0])
    original = test.iloc[[pos]].copy()
    baseline = float(-model.decision_function(original)[0])

    groups = {}
    for field in cfg['preprocessing']['categorical_features']:
        prefix = f'categorical__{field}_'
        indices = [c for c in expected if c.startswith(prefix)]
        if not indices:
            raise ValueError(f'No encoded columns for categorical field: {field}')
        groups[field] = ('categorical', indices)
    for field in cfg['preprocessing']['numerical_features']:
        col = f'numerical__{field}'
        if col not in expected:
            raise ValueError(f'Missing numeric field: {col}')
        groups[field] = ('numerical', [col])
    if set(c for _, cols in groups.values() for c in cols) != set(expected):
        raise ValueError('Some model features are not mapped to original fields.')

    rows = []
    for field, (kind, cols) in groups.items():
        altered = original.copy()
        if kind == 'numerical':
            altered.loc[:, cols[0]] = float(train[cols[0]].median())
            replacement = 'normal-training median (transformed scale)'
        else:
            # Use a real one-hot block from the most frequent normal-training
            # pattern; this avoids invalid one-hot combinations within a field.
            block = train[cols].value_counts(dropna=False).index[0]
            altered.loc[:, cols] = np.asarray(block, dtype=float)
            replacement = 'most frequent normal-training encoded category'
        replaced_score = float(-model.decision_function(altered)[0])
        rows.append({
            'field': field,
            'replacement': replacement,
            'original_anomaly_score': baseline,
            'replaced_anomaly_score': replaced_score,
            'score_drop_when_replaced': baseline - replaced_score,
        })

    rows.sort(key=lambda r: r['score_drop_when_replaced'], reverse=True)
    output = {
        'event_id': args.event_id,
        'actual_label': int(meta.iloc[pos].is_attack),
        'method': 'one-original-field-at-a-time normal-training reference replacement',
        'interpretation': 'Positive score drop: replacing the field reduced anomaly score; negative: replacement increased it. Diagnostic sensitivity, not causal feature attribution.',
        'baseline_anomaly_score': baseline,
        'feature_sensitivity': rows,
        'limitations': [
            'Reference replacements may create unrealistic feature combinations.',
            'Results depend on the chosen normal-training reference values.',
            'Correlated feature interactions and causal importance are not measured.',
            'Unknown categorical values are encoded as all zeros by the preprocessor.',
            'Do not use test labels or these diagnostics to retune the frozen models or thresholds.',
        ],
    }
    result_dir = ROOT / cfg['paths']['results'] / 'explainability'
    result_dir.mkdir(parents=True, exist_ok=True)
    destination = result_dir / f'isolation_forest_event_{args.event_id}.json'
    with destination.open('w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f'Event: {args.event_id} | Actual label: {output["actual_label"]}')
    print(f'Isolation Forest original anomaly score: {baseline:.6f}')
    print('One-field replacement sensitivity (positive drop = less anomalous):')
    for row in rows:
        print(f'  {row["field"]}: score drop {row["score_drop_when_replaced"]:+.6f} | replacement score {row["replaced_anomaly_score"]:.6f}')
    print(f'Saved: {destination}')
    print('NOTE: Reference-replacement sensitivity, NOT SHAP or causal attribution.')


if __name__ == '__main__':
    main()
