"""Explain Autoencoder reconstruction error for one held-out event.

Run from repository root:
    python src/explainability/explain_autoencoder.py --event-id 3505

Per-feature squared errors are reconstruction diagnostics, not causal
attributions. One-hot feature errors are grouped by original field.
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
    parser.add_argument('--event-id', type=int, default=3505)
    args = parser.parse_args()

    with (ROOT / 'config/project_config.json').open(encoding='utf-8') as f:
        config = json.load(f)
    features_dir = ROOT / config['paths']['processed_data'] / 'features'
    model_dir = ROOT / config['paths']['models'] / 'autoencoder'
    with (model_dir / 'feature_names.json').open(encoding='utf-8') as f:
        expected = json.load(f)
    features = pd.read_csv(features_dir / 'test_features.csv')
    metadata = pd.read_csv(features_dir / 'test_metadata.csv')
    if features.columns.tolist() != expected or len(features) != len(metadata):
        raise ValueError('Test feature schema or row alignment mismatch.')
    if not metadata.event_id.is_unique:
        raise ValueError('Duplicate event IDs.')
    matched = np.flatnonzero(metadata.event_id.to_numpy() == args.event_id)
    if len(matched) != 1:
        raise ValueError(f'Expected exactly one event {args.event_id}, found {len(matched)}.')
    i = int(matched[0])
    model = joblib.load(model_dir / 'autoencoder.joblib')
    x = features.iloc[[i]].to_numpy(dtype=float)
    if not np.isfinite(x).all() or x.shape[1] != model.n_features_in_:
        raise ValueError('Invalid model input.')
    reconstructed = model.predict(x)
    sq_errors = (x[0] - reconstructed[0]) ** 2
    mse = float(sq_errors.mean())
    if not np.isfinite(sq_errors).all():
        raise ValueError('Invalid reconstruction output.')

    # Prefer fitted ColumnTransformer metadata over parsing feature names.
    preprocessor = joblib.load(ROOT / config['paths']['models'] / 'preprocessing/preprocessor.joblib')
    names = list(preprocessor.get_feature_names_out())
    if names != expected:
        raise ValueError('Saved model features do not match the fitted preprocessor.')
    grouped = {}
    # The preprocessing config specifies the original columns and their order.
    categorical = config['preprocessing']['categorical_features']
    numerical = config['preprocessing']['numerical_features']
    for name, error in zip(names, sq_errors):
        # sklearn ColumnTransformer feature names: <transformer>__<feature>_<category>
        # Match original field names longest-first to handle underscores.
        suffix = name.split('__', 1)[-1]
        field = next((c for c in sorted(categorical, key=len, reverse=True)
                      if suffix.startswith(c + '_')), None)
        if field is None:
            field = next((n for n in numerical if suffix == n), None)
        if field is None:
            raise ValueError(f'Cannot map transformed feature {name!r} to an original field.')
        grouped[field] = grouped.get(field, 0.0) + float(error)

    out = ROOT / config['paths']['results'] / 'explainability'
    out.mkdir(parents=True, exist_ok=True)
    result = {
        'event_id': args.event_id,
        'is_attack': int(metadata.iloc[i].is_attack),
        'model': 'autoencoder',
        'explanation_type': 'per-feature squared reconstruction error grouped by original field',
        'limitations': 'Describes reconstruction mismatch in transformed feature space; not causal importance or security proof.',
        'reconstruction_mse': mse,
        'transformed_feature_count': len(names),
        'grouped_squared_error': dict(sorted(grouped.items(), key=lambda p: p[1], reverse=True)),
        'per_transformed_feature': dict(zip(names, map(float, sq_errors))),
    }
    path = out / f'autoencoder_event_{args.event_id}.json'
    with path.open('w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(f'Event: {args.event_id} | Actual label: {result["is_attack"]}')
    print(f'Autoencoder reconstruction MSE: {mse:.6f}')
    print('Squared reconstruction error grouped by original field:')
    for field, value in result['grouped_squared_error'].items():
        print(f'  {field}: {value:.6f}')
    print(f'Saved: {path}')
    print('NOTE: These are reconstruction diagnostics, not causal feature attributions.')


if __name__ == '__main__':
    main()
