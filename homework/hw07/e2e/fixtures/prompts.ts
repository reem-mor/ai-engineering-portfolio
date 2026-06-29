export const KB_COLLECTION_NAME = "netflix-shows";

export const PROMPTS = {
  kbCountTypes: "How many rows are type TV Show vs Movie in the Netflix dataset?",
  liveCountryCapital: "What is the capital of Brazil?",
} as const;

export const TOOL_SERVER_URL = "http://host.docker.internal:5005";

/** Dataset-grounded hints — TV Show=2676, Movie=6131 (8807 rows total). */
export const KB_ANSWER_HINTS = [
  /2,?676/,
  /6,?131/,
  /2676[\s\S]{0,80}6131|6131[\s\S]{0,80}2676/i,
];

/** Tool response must include capital or population from country_info fixture/live API. */
export const TOOL_ANSWER_HINTS = [/Brasília/i, /Brasilia/i, /212,?559,?417/];

export const TOOL_OPERATION_HINTS = [/country_info/i, /country info/i, /HW07 Netflix Tools/i];
