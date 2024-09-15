---
---


populateLastUpdated({{site.data.l2safety.epoch}});
updateLinkTargets();
enableTooltips();


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


// options: "descending", "ascending", "initial"
let sortOrder = {
  "l2": "descending",
  "score": "descending",
  "tvl": "descending",
  "type": "descending",
  "stateValidation": "descending",
  "dataAvailability": "descending",
  "exitWindow": "descending",
  "proposerFailure": "descending",
  "sequencerFailure": "descending",
  "status": "descending"
}
// used to save original format to revert to initial order
let originalRows;

function compareValues(a, b) {
  // pad numbers with 0 placeholders so it sorts properly
  const ne = str => str.replace(/\d+/g, n => n.padStart(8, "0"));
  // compare values
  // return a.localeCompare(b);
  return ne(a).localeCompare(ne(b));
}

function cloneRecursively(originalItem) {
  let clonedItem = [...originalItem];
  clonedItem.children = (clonedItem.children || []).map(cloneRecursively);
  return clonedItem;
}

function sortTable(sortEl, sortType, colNum) {
  let table = document.querySelector("tbody");
  // get all the rows in this table:
  let rows = Array.from(table.querySelectorAll(`tr`));
  // save original format to revert to initial order
  if (originalRows === undefined) {
    // needs a deep clone
    originalRows = cloneRecursively(rows);
  }

  // sort the rows
  if (sortOrder[sortType] == "initial") {
    // set sort icon style
    document.querySelectorAll(".sort svg").forEach(item => {
      item.setAttribute("style", "transform: rotate(0deg); fill: currentColor");
    });
    // set next sort method
    sortOrder[sortType] = "descending";
    // update table with sorted rows
    table.replaceChildren(...originalRows);
  } else {
    // hack for TVL since won't sort properly but it's already sorted so just need to reverse if ascending
    if (colNum == 2) {
      if (sortOrder[sortType] == "ascending") {
        rows.reverse();
      } else if (sortOrder[sortType] == "descending") {
        table.replaceChildren(...originalRows);
      }
    } else {
      rows.sort( (r1,r2) => {
        // get each row's column and sorting content
        let t1 = r1.querySelector(`td:nth-child(${colNum})`).getAttribute('data-sort');
        let t2 = r2.querySelector(`td:nth-child(${colNum})`).getAttribute('data-sort');
        // return t1 - t2;
        // return t1 >= t2 ? -1 : 1;
        // compare content
        if (sortOrder[sortType] == "ascending") {
          return compareValues(t1,t2);
        } else if (sortOrder[sortType] == "descending") {
          return compareValues(t2,t1);
        }
      });
    }
    // a.sort(function(a,b){return a - b})
    if (sortOrder[sortType] == "ascending") {
      // reset all sort icon styles
      document.querySelectorAll(".sort svg").forEach(item => {
        item.setAttribute("style", "transform: rotate(0deg); fill: currentColor");
      });
      // set current sort icon style
      sortEl.querySelector("svg").setAttribute("style", "transform: rotate(180deg); fill: var(--l2s-accent)");
      // set next sort method
      sortOrder[sortType] = "initial";
    } else if (sortOrder[sortType] == "descending") {
      // reset all sort icon styles
      document.querySelectorAll(".sort svg").forEach(item => {
        item.setAttribute("style", "transform: rotate(0deg); fill: currentColor");
      });
      // set current sort icon style
      sortEl.querySelector("svg").setAttribute("style", "transform: rotate(0deg); fill: var(--l2s-accent)");
      // set next sort method
      sortOrder[sortType] = "ascending";
    }
    // update table with sorted rows
    table.replaceChildren(...rows);
  }
}
