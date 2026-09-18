import express from "express";
const app = express();
app.get("/", (_req, res) => res.send("B2 works"));
const port = Number(process.env.PORT || 4000);
app.listen(port, "127.0.0.1", () => console.log("listening on " + port));
