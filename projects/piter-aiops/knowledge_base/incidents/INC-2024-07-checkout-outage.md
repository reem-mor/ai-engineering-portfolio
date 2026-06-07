---
title: "Checkout outage postmortem reference"
doc_type: "incident"
services: ["checkout-api", "api-gateway"]
environments: ["NJ-DGE", "GIB-UKGC"]
severity_applicable: ["P1"]
tags: ["postmortem", "checkout", "5xx", "rollback"]
last_updated: "2026-06-06"
author: "Re'em Mor"
version: "1.0"
---

# Checkout Outage Postmortem Reference

## Summary

A checkout outage caused elevated 5xx responses after a deployment changed
request validation behavior. The incident is useful as historical context for
API Gateway 5xx spikes and rollback decisions.

## Root Cause Pattern

The failure mode was a bad rollout interacting with request validation and
upstream service assumptions. Similar future incidents should check recent
deployments before assuming infrastructure saturation.

## Resolution Pattern

Responders should correlate deploy timestamps, roll back the suspected release
when evidence is strong, then verify recovery through 5xx rate, latency, and
successful checkout attempts.

## Related

- `runbooks/RB-001-api-gateway-5xx-spike.md`
- `runbooks/RB-010-deployment-rollback.md`
