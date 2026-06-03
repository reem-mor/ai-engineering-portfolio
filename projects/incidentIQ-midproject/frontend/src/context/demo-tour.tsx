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

export type DemoNodeId = "replay" | "ctrl" | "bus" | "feed" | "kpi" | "onc" | "drill";

export const DEMO_NODE_TO_BLOCK: Partial<Record<DemoNodeId, BlockKey>> = {
  replay: "documents",
  bus: "kb",
  feed: "flask",
  drill: "kb",
  kpi: "docker",
};

export const DEMO_TOUR_SEQUENCE: DemoNodeId[] = ["replay", "bus", "feed", "drill"];

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
  const [phase, setPhase] = useState<"demo" | "arch">("demo");
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const advance = useCallback(() => {
    if (phase === "demo") {
      const next = tourStep + 1;
      if (next >= DEMO_TOUR_SEQUENCE.length) {
        setPhase("arch");
        setTourStep(0);
        scrollToSection("architecture");
        const block = ARCHITECTURE_FLOW[0];
        setArchitectureBlock(block);
        const node = Object.entries(DEMO_NODE_TO_BLOCK).find(([, b]) => b === block)?.[0];
        if (node) setActiveDemoNode(node as DemoNodeId);
        return;
      }
      const node = DEMO_TOUR_SEQUENCE[next];
      setTourStep(next);
      setActiveDemoNode(node);
      const block = DEMO_NODE_TO_BLOCK[node];
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
    setPhase("demo");
    setTourRunning(true);
    setTourPaused(false);
    setActiveDemoNode(DEMO_TOUR_SEQUENCE[0]);
    const block = DEMO_NODE_TO_BLOCK[DEMO_TOUR_SEQUENCE[0]];
    if (block) setArchitectureBlock(block);
    scrollToSection("demo-dashboard");
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
