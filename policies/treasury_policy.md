# Treasury Investment Policy

## Liquidity Requirements

* **Minimum overnight liquidity**: $50,000,000
  * Overnight deposits + money market funds must exceed next-day obligations by at least $50M
  * Calculation: total_liquid_assets - next_day_obligations >= $50M

## Portfolio Duration Limits

* **Maximum portfolio duration**: 2.5 years
  * Weighted average duration across all holdings must not exceed 2.5 years
  * Individual instruments may have longer durations if the portfolio average remains compliant

## Concentration Limits

* **Single issuer maximum**: 15% of total portfolio value
  * No single non-government issuer may represent more than 15% of total portfolio
  * US Government securities are exempt from issuer concentration limits

* **Instrument type maximum**: 40% of total portfolio value
  * No single instrument type (corporate, municipal, etc.) may exceed 40%
  * Government securities are exempt from type concentration limits

## Government Securities Minimum

* **Government securities floor**: 30% of total portfolio value
  * US Treasuries + agency securities must represent at least 30% of portfolio at all times
  * This ensures baseline liquidity and credit quality

## Approval Tiers

| Trade Size | Approval Required |
|-----------|-------------------|
| < $5,000,000 | Auto-approved (policy checks still apply) |
| $5,000,000 - $25,000,000 | Treasury Manager approval |
| > $25,000,000 | CFO approval |

## Confidence Thresholds

| Confidence Level | Action |
|-----------------|--------|
| > 85% | Auto-execute (if all other checks pass) |
| 60% - 85% | Escalate for human review |
| < 60% | Block - insufficient confidence |

## Prohibited Instruments

* Derivatives (without explicit board approval)
* Cryptocurrency or digital assets
* Equities or equity-linked instruments
* Instruments rated below B-
* Instruments with maturity > 10 years
