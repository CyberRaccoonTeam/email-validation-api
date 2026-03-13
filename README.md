# Email Validation API

> Validate email addresses in real-time. Catch typos, disposable emails, and invalid domains.

![Status](https://img.shields.io/badge/Status-MVP-green)
![Stack](https://img.shields.io/badge/Stack-Python%2FFlask-blue)

---

## Features

- **Syntax Validation** - Check if email format is valid
- **Domain Validation** - Verify domain exists and has MX records
- **Disposable Email Detection** - Flag temporary/throwaway emails
- **SMTP Verification** - Check if mailbox exists (optional)
- **Bulk Validation** - Validate multiple emails at once
- **API Keys** - Secure access with rate limiting

---

## Quick Start

```bash
# Install dependencies
pip install flask flask-cors dnspython

# Run the server
python app.py

# Validate an email
curl -X POST http://localhost:5561/api/validate \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/validate` | POST | Validate single email |
| `/api/validate/bulk` | POST | Validate multiple emails |
| `/api/keys` | POST | Create API key |
| `/api/keys/:id` | GET | Get key usage stats |

---

## Response Format

```json
{
  "email": "test@example.com",
  "valid": false,
  "reason": "domain_has_no_mx_records",
  "checks": {
    "syntax": true,
    "domain_exists": true,
    "has_mx_records": false,
    "is_disposable": false,
    "smtp_check": null
  },
  "suggestion": null
}
```

---

## Revenue Model

- **Free Tier:** 100 validations/day
- **Pro ($9/mo):** 10,000 validations/day, bulk API
- **Business ($29/mo):** Unlimited, SMTP verification, webhook alerts

---

## Tech Stack

- **Backend:** Python 3.11, Flask
- **DNS:** dnspython for MX record lookups
- **Database:** SQLite for API keys and usage

---

## Roadmap

- [x] MVP - Syntax and MX validation
- [ ] SMTP verification
- [ ] Bulk validation endpoint
- [ ] Webhook notifications
- [ ] Disposable email database updates

---

## License

MIT

---

Built by [CyberRaccoonTeam](https://github.com/CyberRaccoonTeam)