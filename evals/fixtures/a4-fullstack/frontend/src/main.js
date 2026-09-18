fetch("/api/hello").then(r => r.json()).then(d => { document.getElementById("app").textContent += " / " + d.msg; });
