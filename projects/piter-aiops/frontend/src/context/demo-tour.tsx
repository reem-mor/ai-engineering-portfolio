import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { scrollToSection } from "@/lib/workflow-utils";

export type BlockKey = "documents" | "kb" | "flask" | "docker" | "ec2" | "public";

export type DemoNodeId =
  | "priority"
  | "investigation"
  | "triage"
  | "escalation"
  | "resolution"
  | "analytics"
  | "kb"
  | "history";

/** PITER live-demo story: scroll sections in order. */
export const PITER_TOUR_SECTIONS: { id: string; node: DemoNodeId; label: string }[] = [
  { id: "priority-center", node: "priority", label: "Priority Center" },
  { id: "investigation", node: "investigation", label: "Investigation Workspace" },
  { id: "triage-plan", node: "triage", label: "Triage Plan" },
  { id: "escalation", node: "escalation", label: "Escalation Hub" },
  { id: "resolution", node: "resolution", label: "Resolution Tracker" },
  { id: "incident-history", node: "history", label: "Incident History" },
  { id: "agent-analytics", node: "analytics", label: "Agent Analytics" },
  { id: "live-kb", node: "kb", label: "Knowledge Base" },
];

export const DEMO_NODE_TO_BLOCK: Partial<Record<DemoNodeId, BlockKey>> = {
  priority: "documents",
  investigation: "kb",
  triage: "flask",
  escalation: "docker",
  resolution: "ec2",
  analytics: "docker",
  kb: "kb",
  history: "flask",
};

export const ARCHITECTURE_FLOW: BlockKey[] = [
  "documents",
  "kb",
  "flask",
  "docker",
  "ec2",
  "public",
];

type DemoTourState = {
  activeDemoNode: DemoNodeId | null;
  setActiveDemoNode: (id: DemoNodeId | null) => void;
  architectureBlock: BlockKey;
  setArchitectureBlock: (key: BlockKey) => void;
  tourRunning: boolean;
  tourPaused: boolean;
  startDemoTour: () => void;
  pauseDemoTour: () => void;
  stepDemoTour: () => void;
};

const DemoTourContext = createContext<DemoTourState | null>(null);

export function DemoTourProvider({ children }: { children: ReactNode }) {
  const [activeDemoNode, setActiveDemoNode] = useState<DemoNodeId | null>(null);
  const [architectureBlock, setArchitectureBlock] = useState<BlockKey>("kb");
  const [tourRunning, setTourRunning] = useState(false);
  const [tourPaused, setTourPaused] = useState(false);
  const [tourStep, setTourStep] = useState(0);
  const [phase, setPhase] = useState<"piter" | "arch">("piter");
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const advance = useCallback(() => {
    if (phase === "piter") {
      const next = tourStep + 1;
      if (next >= PITER_TOUR_SECTIONS.length) {
        setPhase("arch");
        setTourStep(0);
        scrollToSection("architecture");
        const block = ARCHITECTURE_FLOW[0];
        setArchitectureBlock(block);
        setActiveDemoNode("priority");
        return;
      }
      const step = PITER_TOUR_SECTIONS[next];
      setTourStep(next);
      setActiveDemoNode(step.node);
      scrollToSection(step.id);
      const block = DEMO_NODE_TO_BLOCK[step.node];
      if (block) setArchitectureBlock(block);
      return;
    }

    const next = tourStep + 1;
    if (next >= ARCHITECTURE_FLOW.length) {
      setTourRunning(false);
      setTourPaused(false);
      clearTimer();
      return;
    }
    setTourStep(next);
    setArchitectureBlock(ARCHITECTURE_FLOW[next]);
  }, [phase, tourStep, clearTimer]);

  const startDemoTour = useCallback(() => {
    clearTimer();
    setTourStep(0);
    setPhase("piter");
    setTourRunning(true);
    setTourPaused(false);
    const first = PITER_TOUR_SECTIONS[0];
    setActiveDemoNode(first.node);
    const block = DEMO_NODE_TO_BLOCK[first.node];
    if (block) setArchitectureBlock(block);
    scrollToSection(first.id);
  }, [clearTimer]);

  const pauseDemoTour = useCallback(() => {
    setTourPaused((p) => {
      const next = !p;
      if (next) clearTimer();
      else if (tourRunning) {
        intervalRef.current = setInterval(advance, 2500);
      }
      return next;
    });
  }, [advance, clearTimer, tourRunning]);

  const stepDemoTour = useCallback(() => {
    advance();
  }, [advance]);

  useEffect(() => {
    if (!tourRunning || tourPaused) {
      clearTimer();
      return;
    }
    intervalRef.current = setInterval(advance, 2500);
    return clearTimer;
  }, [tourRunning, tourPaused, advance, clearTimer]);

  const value = useMemo(
    () => ({
      activeDemoNode,
      setActiveDemoNode,
      architectureBlock,
      setArchitectureBlock,
      tourRunning,
      tourPaused,
      startDemoTour,
      pauseDemoTour,
      stepDemoTour,
    }),
    [
      activeDemoNode,
      architectureBlock,
      tourRunning,
      tourPaused,
      startDemoTour,
      pauseDemoTour,
      stepDemoTour,
    ],
  );

  return (
    <DemoTourContext.Provider value={value}>{children}</DemoTourContext.Provider>
  );
}

export function useDemoTour() {
  const ctx = useContext(DemoTourContext);
  if (!ctx) throw new Error("useDemoTour must be used within DemoTourProvider");
  return ctx;
}
