# Email Validation API

![RaccoonLabs](https://img.shields.io/badge/Built%20by-RaccoonLabs-blueviolet)

REST API for validating and verifying email addresses in real-time.

## What It Does
Part of the **RaccoonLabs API Suite**. Validate email syntax, check MX records, verify mailbox existence, and detect disposable/temporary emails. Bulk validation supported. Stripe-powered pricing with 3 tiers: **Starter $9/mo**, **Pro $29/mo**, **Enterprise $99/mo**.

## Tech Stack
- Python 3.10+, Flask
- DNS resolution, SMTP verification
- Stripe API

## Quick Start
```bash
git clone https://github.com/CyberRaccoonTeam/email-validation-api.git
cd email-validation-api
pip install -r requirements.txt
flask run
# POST /validate {"email": "test@example.com"}
```

## Pricing
| Tier | Price | Requests/mo |
|------|-------|-------------|
| Starter | $9 | 5,000 |
| Pro | $29 | 25,000 |
| Enterprise | $99 | Unlimited |

## License
MIT License

## Links
- **RaccoonLabs:** https://github.com/CyberRaccoonTeam
