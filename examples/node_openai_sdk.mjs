// Minimal Node example.
//
//   npm i openai
//   export ADZUKI_API_KEY="sk-..."
//   node examples/node_openai_sdk.mjs "Explain B-tree splits"

import OpenAI from "openai";

const client = new OpenAI({
  baseURL: process.env.ADZUKI_BASE_URL ?? "https://adzukiai.com/v1",
  apiKey: process.env.ADZUKI_API_KEY,
});

const prompt = process.argv.slice(2).join(" ") || "Explain B-tree splits in two sentences.";

const resp = await client.chat.completions.create({
  model: process.env.ADZUKI_MODEL ?? "deepseek-v4.1-flash",
  messages: [{ role: "user", content: prompt }],
});

console.log(resp.choices[0].message.content);
console.log();
console.log(
  `prompt ${resp.usage.prompt_tokens} tokens / output ${resp.usage.completion_tokens} tokens`,
);
