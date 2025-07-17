import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import IsolationForest

def generate_credit_scores(json_path):
    with open(json_path, 'r') as f:
        raw = json.load(f)

    records = []
    for tx in raw:
        try:
            records.append({
                'wallet': tx.get('userWallet', ''),
                'action': tx.get('action', '').lower(),
                'timestamp': pd.to_datetime(tx.get('timestamp', 0), unit='s'),
                'amount': float(tx.get('actionData', {}).get('amount', 0)),
                'asset': tx.get('actionData', {}).get('assetSymbol', ''),
                'price_usd': float(tx.get('actionData', {}).get('assetPriceUSD', 0))
            })
        except Exception as e:
            print(f"Skipping record due to error: {e}")

    df = pd.DataFrame(records)

    if df.empty:
        raise ValueError("No valid transactions found.")

    df['amount_usd'] = df['amount'] * df['price_usd']
    actions = ['deposit', 'borrow', 'repay', 'redeemunderlying', 'liquidationcall']

    features = df.groupby('wallet').agg(
        total_txn=('action', 'count'),
        active_days=('timestamp', lambda x: x.dt.date.nunique()),
        first_txn=('timestamp', 'min'),
        last_txn=('timestamp', 'max'),
    )

    for action in actions:
        action_df = df[df['action'] == action]
        grouped = action_df.groupby('wallet')
        features[f'{action}_count'] = grouped.size()
        features[f'{action}_amount'] = grouped['amount_usd'].sum()

    features = features.fillna(0)
    features['borrow_deposit_ratio'] = features['borrow_amount'] / (features['deposit_amount'] + 1e-6)
    features['repay_borrow_ratio'] = features['repay_amount'] / (features['borrow_amount'] + 1e-6)
    features['liquidation_flag'] = (features['liquidationcall_count'] > 0).astype(int)
    features['txn_span_days'] = (features['last_txn'] - features['first_txn']).dt.days + 1

    features = features.drop(columns=['first_txn', 'last_txn'])
    features = features.fillna(0)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(features)

    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(scaled)
    raw_scores = model.decision_function(scaled)

    final_scores = MinMaxScaler((0, 1000)).fit_transform(raw_scores.reshape(-1, 1)).flatten()
    features['credit_score'] = final_scores.astype(int)

    result = features[['credit_score']].reset_index()
    result.to_csv("wallet_credit_scores.csv", index=False)
    print(result.head())
    return result

if __name__ == "__main__":
    generate_credit_scores("user-wallet-transactions.json")