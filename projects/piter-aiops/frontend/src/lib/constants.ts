import type { ComponentType } from "react";
import {
  Activity,
  Brain,
  Database,
  Gauge,
  Network,
  Search,
  ServerCog,
  ShieldCheck,
} from "lucide-react";

export type NavKey =
  | "dashboard"
  | "investigations"
  | "storm"
  | "memory"
  | "knowledge"
  | "tools"
  | "architecture"
  | "settings";

export type Investigation = {
  id: string;
  conclusion: "Critical" | "Malicious" | "Suspicious" | "Inconclusive" | "Benign" | "Noise";
  conclusionDetail: string;
  alertTime: string;
  alert: string;
  service: string;
  environment: string;
  entities: string;
  source: string;
  status: string;
  priority: "P1" | "P2" | "P3" | "P4";
  impact: string;
};

export type StormState = "idle" | "streaming" | "paused" | "critical" | "investigating" | "resolved";

export const NAV_ITEMS: {
  key: NavKey;
  label: string;
  icon: ComponentType<{ className?: string }>;
}[] = [
  { key: "dashboard", label: "Dashboard", icon: Gauge },
  { key: "investigations", label: "Investigations", icon: Search },
  { key: "storm", label: "Alert Storm Demo", icon: Activity },
  { key: "memory", label: "Context Memory", icon: Brain },
  { key: "knowledge", label: "Knowledge Base", icon: Database },
  { key: "tools", label: "Tools", icon: ServerCog },
  { key: "architecture", label: "Architecture", icon: Network },
  { key: "settings", label: "Settings", icon: ShieldCheck },
];

export const INVESTIGATIONS: Investigation[] = [
  {
    id: "INV-2026-0610-001",
    conclusion: "Critical",
    conclusionDetail: "Critical betting outage detected; escalation preview prepared.",
    alertTime: "10:02:55",
    alert: "P1 bet-service 100% error rate on GIB-UKGC",
    service: "bet-service",
    environment: "GIB-UKGC",
    entities: "bet-api, postgres, kafka-settlement",
    source: "Alert stream + Bedrock KB",
    status: "Escalated",
    priority: "P1",
    impact: "$520k/hr regulated market exposure",
  },
  {
    id: "INV-2026-0610-002",
    conclusion: "Noise",
    conclusionDetail: "Noise grouped: repeated memory warnings under threshold.",
    alertTime: "10:01:13",
    alert: "P4 wallet-service memory utilization 78%",
    service: "wallet-service",
    environment: "NJ-DGE",
    entities: "wallet-worker-3",
    source: "Noise suppression",
    status: "Noise Grouped",
    priority: "P4",
    impact: "No customer impact",
  },
  {
    id: "INV-2026-0610-003",
    conclusion: "Suspicious",
    conclusionDetail: "Known pattern: replication warning correlated with previous deploy.",
    alertTime: "09:58:42",
    alert: "P2 replication lag above 30s",
    service: "replication",
    environment: "GIB-UKGC",
    entities: "read-replica-2, wallet-service",
    source: "piter-recent-deployments",
    status: "Investigating",
    priority: "P2",
    impact: "Regulatory exposure",
  },
  {
    id: "INV-2026-0610-004",
    conclusion: "Benign",
    conclusionDetail: "False positive: synthetic canary recovered before threshold.",
    alertTime: "09:55:07",
    alert: "P3 auth-service canary 502 spike",
    service: "auth-service",
    environment: "MGM",
    entities: "auth-api, edge",
    source: "Synthetic monitor",
    status: "False Positive",
    priority: "P3",
    impact: "No sustained impact",
  },
  {
    id: "INV-2026-0610-005",
    conclusion: "Inconclusive",
    conclusionDetail: "Kafka consumer lag elevated; awaiting dependency correlation.",
    alertTime: "09:52:30",
    alert: "P3 Kafka consumer lag on settlement topic",
    service: "payments-service",
    environment: "NJ-DGE",
    entities: "kafka-settlement, payments-api",
    source: "Metrics pipeline",
    status: "In Review",
    priority: "P3",
    impact: "Settlement delay risk",
  },
];

export const PIPELINE = [
  { label: "Priority", body: "P1 classification from impact, severity, and regulated market." },
  {
    label: "Investigation",
    body: "Correlates warning shots, deploys, similar incidents, and KB evidence.",
  },
  { label: "Triage", body: "Turns evidence into concrete operator steps with citations." },
  { label: "Escalation", body: "Previews owner, policy, and masked notification recipients." },
  { label: "Resolution", body: "Produces validation steps and post-mortem draft." },
];

export const TOOLS = [
  {
    name: "piter-recent-deployments",
    purpose: "Recent deployments, correlation, rollback availability",
    input: "service, environment, alert_time, lookback_hours",
    output: "suspect_deployment, dependency_hop, rollback_available",
    status: "mock data / live-ready source",
    latency: "42 ms",
    used: true,
  },
  {
    name: "piter-service-context",
    purpose: "Ownership, on-call role, impact, priority, regulatory exposure",
    input: "service, environment, severity",
    output: "owner_team, escalation_path, business_impact",
    status: "mock data / live-ready source",
    latency: "31 ms",
    used: true,
  },
  {
    name: "piter-similar-incidents",
    purpose: "Historical incident matching, root cause, resolution, previous MTTR",
    input: "service, symptom, limit",
    output: "similar_incidents, root_cause, resolution, mttr_minutes",
    status: "mock data / live-ready source",
    latency: "58 ms",
    used: true,
  },
  {
    name: "piter-escalation",
    purpose: "Escalation policy preview and safe notification workflow",
    input: "operation, service, severity, incident_id, recipient, token",
    output: "policy, masked_recipient, blocked_reasons, idempotency_key",
    status: "mock by default / live-blocked",
    latency: "27 ms",
    used: true,
  },
];

export const WARNING_ALERTS = [
  "T+090s bet-service latency p95 increased to 2.4s",
  "T+125s connection pool exhausted briefly on bet-service",
  "T+155s bet-service 5xx rate above 2% (3.8%)",
  "T+170s bet-service circuit breaker tripped briefly",
  "T+175s P1: bet-service nodes unresponsive, 100% error rate",
];

export const AGENT_PROMPTS = [
  "What should I check first?",
  "Who should I escalate this to?",
  "What changed recently?",
  "Show similar past incidents",
  "What is the business impact?",
  "Create post-mortem summary",
];
