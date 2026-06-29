export const KB_COLLECTION_NAME = "netflix-shows";

export const PROMPTS = {
  kbCountTypes: "How many rows are type TV Show vs Movie in the Netflix dataset?",
  liveCountryCapital: "What is the capital of Brazil?",
} as const;

export const TOOL_SERVER_URL = "http://host.docker.internal:5005";

export const KB_ANSWER_HINTS = [/TV Show/i, /Movie/i, /type/i];
export const TOOL_ANSWER_HINTS = [/Brasília/i, /Brasilia/i, /capital/i];
