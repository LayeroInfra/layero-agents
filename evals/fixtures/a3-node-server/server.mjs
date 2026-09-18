import { createServer } from "node:http";
createServer((_q, r) => { r.writeHead(200, {"content-type":"text/plain"}); r.end("A3 works"); })
  .listen(Number(process.env.PORT || 3000), "0.0.0.0");
