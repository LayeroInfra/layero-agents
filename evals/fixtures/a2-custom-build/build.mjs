import { mkdirSync, writeFileSync, readFileSync } from "node:fs";
mkdirSync("public_out", { recursive: true });
writeFileSync("public_out/index.html", readFileSync("page.tpl", "utf8").replace("{{TEXT}}", "A2 works"));
