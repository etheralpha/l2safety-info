---
---


populateLastUpdated({{site.data.l2safety.epoch}});
enableTooltips();
updateLinkTargets();


function populateLastUpdated(dataEpoch) {
  const currentEpoch = Math.round(Date.now()/10000)*10;
  const delta = currentEpoch - dataEpoch;
  const deltaHours = Math.round(delta/3600);
  let lastUpdated = ` — updated ${deltaHours}hrs ago`;
  if (deltaHours < 1) {
    const deltaMinutes = Math.round(delta/60);
    lastUpdated = ` — updated ${deltaMinutes}min ago`;
  }
  else if (deltaHours == 1) {
    lastUpdated = ` — updated ${deltaHours}hr ago`;
  }
  else if (deltaHours > 48) {
    const deltaDays = Math.round(deltaHours/24);
    lastUpdated = ` — updated ${deltaDays}d ago`;
  }
  // lastUpdated += " (updated daily)"
  document.getElementById("lastUpdated").innerText = lastUpdated;
}


function enableTooltips() {
  let tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  let tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
  })
}


// open external links and pdfs in new tab
function updateLinkTargets() {
  {%- assign site_url = site.url | split: "//" | last -%}
  document.querySelectorAll("a").forEach(link => {
    let href = link.href;
    // set all links to open in new tab
    if (/^(https?:)?\/\//.test(link.href)) {
      link.target = "_blank";
    }
    // if current domain, use same tab
    if (href != undefined && href.includes("{{site_url}}")) {
      link.target = "_self";
    }
    // if relative links, use new tab
    if (href != undefined && !href.includes("https")) {
      link.target = "_self";
    }
    // open all .pdf, .png, .jpg, .mp4 in new tab
    if (/(\.pdf$|\.png$|\.jpe*g$|\.mp4)/.test(href)) {
      link.target = "_blank";
    }
    // if new-tab class, use new tab
    if (link.classList.contains("new-tab")) {
      link.target = "_blank";
    }
  })
}
