(function(){
  function sendToolInvoke(toolName, args) {
    // The Apps SDK listens for a postMessage protocol in the iframe;
    // The examples repo demonstrates sending a structured action so
    // ChatGPT can call the MCP tool with given args.
    window.parent?.postMessage({
      type: "OPENAI_WIDGET_ACTION",
      action: { tool: toolName, args: args }
    }, "*");
  }

  function cardEl(card) {
    const root = document.createElement("div");
    root.className = "sw-card";

    const img = document.createElement("img");
    img.src = card.image || "https://placehold.co/600x340";
    root.appendChild(img);

    const body = document.createElement("div");
    body.className = "sw-body";
    const t = document.createElement("div");
    t.className = "sw-title";
    t.textContent = card.title || "";
    const s = document.createElement("div");
    s.className = "sw-subtitle";
    s.textContent = card.subtitle || "";
    body.appendChild(t); body.appendChild(s);
    root.appendChild(body);

    const actions = document.createElement("div");
    actions.className = "sw-actions";
    (card.actions || []).forEach(a => {
      const btn = document.createElement("button");
      btn.className = "sw-btn";
      btn.textContent = a.label;
      btn.onclick = () => sendToolInvoke(a.tool, a.args || {});
      actions.appendChild(btn);
    });
    root.appendChild(actions);

    return root;
  }

  function backEl(back) {
    if (!back) return document.createElement("div");
    const wrap = document.createElement("div");
    wrap.className = "sw-back";
    const btn = document.createElement("button");
    btn.className = "sw-btn";
    btn.textContent = back.label || "Back";
    btn.onclick = () => sendToolInvoke(back.tool, back.args || {});
    wrap.appendChild(btn);
    return wrap;
  }

  function mountCommon(root, data) {
    root.innerHTML = "";
    const wrap = document.createElement("div");
    wrap.className = "sw-wrap";

    const heading = document.createElement("div");
    heading.className = "sw-heading";
    heading.textContent = data.heading || "Stocks";
    wrap.appendChild(heading);

    const row = document.createElement("div");
    row.className = "sw-row";
    (data.cards || []).forEach(c => row.appendChild(cardEl(c)));
    wrap.appendChild(row);

    wrap.appendChild(backEl(data.back));
    root.appendChild(wrap);
  }

  window.StockWidgets = {
    mountNewsCarousel: (root, data) => mountCommon(root, data),
    mountAnalysisCarousel: (root, data) => mountCommon(root, data),
  };
})();
