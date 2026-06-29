export const KB_COLLECTION_NAME = "netflix-shows";

export const PROMPTS = {
  kbCountTypes:
    "Using the #netflix-shows knowledge base only: how many rows are type TV Show vs Movie? Show exact counts.",
  liveCountryCapital:
    "Use the country_info tool: what is the capital of Brazil and its population?",
  combinedDemo:
    "Using #netflix-shows and country_info: how many Movie titles are in the dataset, and what is Japan's capital?",
} as const;

export const TOOL_SERVER_URL =
  process.env.TOOL_SERVER_URL ??
  (process.env.OPEN_WEBUI_HOST_INSTALL === "1"
    ? "http://localhost:5005"
    : "http://host.docker.internal:5005");

/** Dataset-grounded hints — TV Show=2676, Movie=6131 (8807 rows total). */
export const KB_ANSWER_HINTS = [
  /2[,.\s]?676/,
  /6[,.\s]?131/,
  /2676[\s\S]{0,120}6131|6131[\s\S]{0,120}2676/i,
];

/** Tool response must include capital or population from country_info fixture/live API. */
export const TOOL_ANSWER_HINTS = [/Brasília/i, /Brasilia/i, /212,?559,?417/];

export const TOOL_OPERATION_HINTS = [/country_info/i, /country info/i, /HW07 Netflix Tools/i];
