# 🧮 Aave V2 Wallet Credit Scoring System
This project is my attempt to assign DeFi credit scores (0–1000) to wallets interacting with the Aave V2 protocol based on their historical transaction behavior.
Higher scores indicate responsible, consistent usage, while lower scores highlight risky or exploitative behavior.

## ⚙️ Methodology
I used an unsupervised machine learning approach to analyze wallet activity and assign credit scores, without needing any labeled training data.

### Data Source
The input consists of raw transaction-level data from the Aave V2 protocol. Each record includes:
- userWallet, action, timestamp
- Action-specific metadata like amount, assetSymbol, and assetPriceUSD from actionData

## 🛠 Feature Engineering
Each wallet is summarized by the following engineered features:

|_Features_	             |   _Description_  
|------------------------|-------------------------|
total_txn, active_days	 | Overall activity  
*_count (per action)	   | Frequency of deposit, borrow, repay, etc. 
*_amount (USD value)	   | Total amount interacted (converted via asset price)
borrow_deposit_ratio	   | Risk indicator
repay_borrow_ratio	     | Responsibility indicator
liquidation_flag	       | Penalizes wallets that were liquidated
txn_span_days	           | Consistency over time

To compute monetary impact, I calculated:
~~~
amount_usd = amount_in_token * asset_price_usd
~~~

## 🧠 Scoring Model: IsolationForest
I used IsolationForest, an anomaly detection algorithm, to learn what typical wallet behavior looks like. Wallets that behaved unusually received lower raw anomaly scores. <br>

Then, I scaled the scores into a credit range of 0 to 1000 using Min-Max normalization:
- 1000 = very trustworthy and consistent
- 0 = highly anomalous or risky

## 🔄 Processing Flow
~~~
flowchart LR
    A[transactions.json] --> B[Flatten & Extract Features]
    B --> C[Aggregate by Wallet]
    C --> D[Compute Feature Ratios]
    D --> E[IsolationForest Scoring]
    E --> F[Normalize Scores (0–1000)]
    F --> G[wallet_credit_scores.csv]
~~~

This project serves as a transparent, extensible framework for behavioral risk scoring in DeFi.
