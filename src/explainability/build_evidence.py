"""Build an auditable, structured SOC evidence record from existing frozen results.

Run from repository root:
    python src/explainability/build_evidence.py --event-id 3505

This step does not retrain, rescore, or infer an attack technique. Ground-truth
labels are deliberately excluded from the operational evidence object.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def load_json(path):
    with path.open(encoding='utf-8') as handle:
        return json.load(handle)


def require_close(a, b, name):
    if not np.isclose(float(a), float(b), rtol=1e-8, atol=1e-7):
        raise ValueError(f'{name} does not match frozen predictions: {a} vs {b}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--event-id', type=int, required=True)
    args = parser.parse_args()
    cfg = load_json(ROOT / 'config/project_config.json')
    test_path = ROOT / cfg['paths']['processed_data'] / 'splits/test.csv'
    prediction_path = ROOT / cfg['paths']['results'] / 'detection_comparison/test_predictions.csv'
    explanation_dir = ROOT / cfg['paths']['results'] / 'explainability'

    test = pd.read_csv(test_path)
    predictions = pd.read_csv(prediction_path)
    for name, frame in [('test', test), ('predictions', predictions)]:
        if 'event_id' not in frame or not frame.event_id.is_unique:
            raise ValueError(f'{name} event IDs missing or duplicated')
    event = test.loc[test.event_id.eq(args.event_id)]
    pred = predictions.loc[predictions.event_id.eq(args.event_id)]
    if len(event) != 1 or len(pred) != 1:
        raise ValueError('Event must appear exactly once in both held-out test and predictions.')
    raw = event.iloc[0]
    p = pred.iloc[0]
    if int(raw.is_attack) != int(p.is_attack):
        raise ValueError('Event label mismatch between raw test and predictions.')

    ae = load_json(explanation_dir / f'autoencoder_event_{args.event_id}.json')
    iso = load_json(explanation_dir / f'isolation_forest_event_{args.event_id}.json')
    if int(ae['event_id']) != args.event_id or int(iso['event_id']) != args.event_id:
        raise ValueError('Explanation event ID mismatch.')
    if int(ae['is_attack']) != int(raw.is_attack) or int(iso['actual_label']) != int(raw.is_attack):
        raise ValueError('Explanation label mismatch.')
    require_close(ae['reconstruction_mse'], p.autoencoder_reconstruction_mse, 'Autoencoder score')
    require_close(iso['baseline_anomaly_score'], p.isolation_forest_score, 'Isolation Forest score')

    if_threshold = float(load_json(ROOT / cfg['paths']['results'] / 'isolation_forest/threshold_selection.json')['threshold'])
    ae_threshold = float(load_json(ROOT / cfg['paths']['results'] / 'autoencoder/threshold_selection.json')['selected_threshold'])
    if_pred = int(float(p.isolation_forest_score) >= if_threshold)
    ae_pred = int(float(p.autoencoder_reconstruction_mse) >= ae_threshold)
    if if_pred != int(p.isolation_forest_pred) or ae_pred != int(p.autoencoder_pred):
        raise ValueError('Frozen prediction differs from score/threshold rule.')
    agree = bool(if_pred == ae_pred)
    if agree != bool(p.models_agree):
        raise ValueError('Model agreement flag mismatch.')

    original_fields = cfg['preprocessing']['categorical_features'] + cfg['preprocessing']['numerical_features']
    if any(field not in event.columns for field in original_fields):
        raise ValueError('Raw event missing a configured telemetry field.')
    raw_evidence = {field: raw[field].item() if hasattr(raw[field], 'item') else raw[field]
                    for field in original_fields}
    grouped_errors = ae['grouped_squared_error']
    sensitivities = iso['feature_sensitivity']
    if set(grouped_errors) != set(original_fields) or {item['field'] for item in sensitivities} != set(original_fields):
        raise ValueError('Explanation field groups do not match raw telemetry schema.')

    record = {
        'schema_version': '1.0',
        'event_id': args.event_id,
        'raw_evidence': raw_evidence,
        'detection': {
            'isolation_forest': {'anomaly_score': float(p.isolation_forest_score),
                                 'validation_selected_threshold': if_threshold,
                                 'prediction': 'anomaly' if if_pred else 'normal'},
            'autoencoder': {'reconstruction_mse': float(p.autoencoder_reconstruction_mse),
                            'validation_selected_threshold': ae_threshold,
                            'prediction': 'anomaly' if ae_pred else 'normal'},
            'models_agree': agree,
        },
        'explanations': {
            'autoencoder': {
                'method': ae['explanation_type'],
                'grouped_squared_reconstruction_error': grouped_errors,
                'interpretation': ae['limitations'],
            },
            'isolation_forest': {
                'method': iso['method'],
                'feature_sensitivity': sensitivities,
                'interpretation': iso['interpretation'],
                'limitations': iso['limitations'],
            },
        },
        'provenance': {
            'raw_event': 'data/processed/splits/test.csv',
            'frozen_predictions': 'results/detection_comparison/test_predictions.csv',
            'autoencoder_explanation': f'results/explainability/autoencoder_event_{args.event_id}.json',
            'isolation_forest_explanation': f'results/explainability/isolation_forest_event_{args.event_id}.json',
            'thresholds': 'validation-selected, unchanged after held-out test evaluation',
        },
        'analyst_notice': 'Scores and explanation diagnostics are not proof of an attack. Review original evidence independently.',
        'mitre_mapping': None,
        'llm_recommendation': None,
        'human_decision': None,
    }
    output_dir = explanation_dir / 'evidence'
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f'event_{args.event_id}_evidence.json'
    with output.open('w', encoding='utf-8') as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False, allow_nan=False)
    print(f'Event: {args.event_id}')
    print(f'Isolation Forest: {record["detection"]["isolation_forest"]["prediction"]} | score {float(p.isolation_forest_score):.6f}')
    print(f'Autoencoder: {record["detection"]["autoencoder"]["prediction"]} | MSE {float(p.autoencoder_reconstruction_mse):.6f}')
    print(f'Models agree: {agree}')
    print(f'Raw fields preserved: {len(raw_evidence)}')
    print(f'Saved: {output}')
    print('Ground truth intentionally excluded from operational evidence.')


if __name__ == '__main__':
    main()
