# Notifications

Escalation notifications default to **mock** mode. No SNS or SES messages are sent unless all safety gates pass.

## Environment variables

```env
PITER_NOTIFICATION_MODE=mock          # mock | preview | live
PITER_NOTIFICATION_REQUIRE_CONFIRMATION=true
PITER_DEMO_SMS_RECIPIENT=
PITER_DEMO_EMAIL_RECIPIENT=
PITER_SNS_TOPIC_ARN=
PITER_SES_SENDER_EMAIL=
PITER_NOTIFICATION_MAX_SENDS_PER_INCIDENT=1
```

## Modes

| Mode | Behavior |
|---|---|
| `mock` | Preview only; `sent: false`; masked recipients in UI |
| `preview` | Policy and recipient mask; no external dispatch |
| `live` | Blocked locally unless confirmation token, allowlist, and severity gates pass |

## UI display

Settings and the agent panel read `notification.mode` from `/api/bootstrap`.
Recipients are masked (`ro***ll`, `a***@example.com`).

## Safety

- Do not commit real phone numbers or personal emails.
- `piter-escalation` Lambda source does not call boto3 SNS/SES in the course repo.
- Tests assert live dispatch remains blocked in local source.

See [`action_groups/piter-escalation/lambda_function.py`](../action_groups/piter-escalation/lambda_function.py).
