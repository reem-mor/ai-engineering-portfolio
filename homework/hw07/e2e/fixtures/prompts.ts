export const KB_COLLECTION_NAME = "netflix-shows";

export const PROMPTS = {
  kbCountTypes: "How many rows are type TV Show vs Movie in the Netflix dataset?",
  liveCountryCapital: "What is the capital of Brazil?",
} as const;

export const TOOL_SERVER_URL = "http://host.docker.internal:5005";

/** Match assistant output only — must not appear in the user prompt text. */
export const KB_ANSWER_HINTS = [
  /\b6,?789\b/,
  /6[\s,]*789/,
  /TV Show.*Movie|Movie.*TV Show/i,
];

export const TOOL_ANSWER_HINTS = [/Brasília/i, /Brasilia/i, /212,?559,?417/];
