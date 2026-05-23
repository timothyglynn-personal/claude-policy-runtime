# Approval Matrix

## Approval Authority

| Role | Max Single Trade | Max Daily Volume | Can Override Policy |
|------|-----------------|------------------|---------------------|
| AI Treasury Analyst | $5,000,000 | $15,000,000 | No |
| Treasury Manager | $25,000,000 | $75,000,000 | No |
| VP Treasury | $50,000,000 | $150,000,000 | Limited (with documentation) |
| CFO | Unlimited | Unlimited | Yes (with board notification) |

## Escalation Path

1. **Auto-Approved**: Trade < $5M, all policy checks pass, confidence > 85%
2. **Treasury Manager**: Trade $5M-$25M, or confidence 60-85%
3. **CFO**: Trade > $25M, or policy override requested
4. **Board**: Derivative authorization, policy exceptions

## Emergency Procedures

* In market stress events (VIX > 35), all trades > $10M require CFO approval
* Liquidity crisis: VP Treasury or higher can authorize temporary policy exceptions
* All emergency actions must be documented and reviewed within 24 hours

## Documentation Requirements

Every approved trade must include:
* Rationale and market analysis
* Expected impact on portfolio metrics
* Risk assessment
* Compliance verification timestamp
* Approver identity and timestamp
