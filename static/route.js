// route.js - autosave editor logic
(function(){
  const routeId = location.pathname.split("/").pop();
  const endpoint = `/api/route/${routeId}`;

  // debounce helper
  function debounce(fn, wait){
    let t;
    return function(...args){
      clearTimeout(t);
      t = setTimeout(()=>fn.apply(this,args), wait);
    };
  }

  // gather whole route from DOM
  function collectRoute(){
    const title = document.querySelector("h1").innerText.trim();
    const stops = [];
    document.querySelectorAll(".stop-row").forEach(row=>{
      const idx = row.dataset.index;
      const name = row.querySelector('[data-field="name"]') ? row.querySelector('[data-field="name"]').value : row.querySelector('input[type="text"]').value;
      const timeEl = row.querySelector('[data-field="time"]') || row.querySelector('input[type="time"]');
      const delayEl = row.querySelector('[data-field="delay"]') || row.querySelector('input[type="number"]');
      const time = timeEl ? timeEl.value : row.querySelector('.time-left').innerText.trim();
      const delay = delayEl ? parseInt(delayEl.value || 0) : 0;
      stops.push({name: name, time: time, delay: Number(isNaN(delay) ? 0 : delay)});
    });
    return {title, stops};
  }

  // save route to API
  async function saveRoute(){
    const payload = collectRoute();
    try{
      await fetch(endpoint, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify(payload)
      });
      // optionally show a tiny saved indicator (omitted for brevity)
    }catch(e){
      console.error("save failed", e);
    }
  }

  const debouncedSave = debounce(saveRoute, 650);

  // attach input listeners
  document.addEventListener("input", function(e){
    const el = e.target;
    if (el.matches('input[type="time"], input[type="number"], input[type="text"]')) {
      debouncedSave();
    }
  });

  // plus / minus / delete buttons
  document.querySelectorAll('.stop-row').forEach(row=>{
    row.addEventListener('click', async function(e){
      const target = e.target;
      const idx = parseInt(row.dataset.index);
      if (target.matches('button[data-action="add"], button[data-action="sub"], button[data-action="delete"], button[data-action]')) {
        const action = target.getAttribute('data-action') || target.name;
        if (action === 'add') {
          // increment delay input
          const delayEl = row.querySelector('input[data-field="delay"], input[type="number"]');
          delayEl.value = (parseInt(delayEl.value || 0) + 1);
          debouncedSave();
        } else if (action === 'sub') {
          const delayEl = row.querySelector('input[data-field="delay"], input[type="number"]');
          delayEl.value = (parseInt(delayEl.value || 0) - 1);
          debouncedSave();
        } else if (action === 'delete') {
          // delete via API then remove DOM and resave
          if (!confirm("Delete this stop?")) return;
          try{
            await fetch(`/api/route/${routeId}/delete_stop`, {
              method: "POST",
              headers: {"Content-Type":"application/json"},
              body: JSON.stringify({index: idx})
            });
            row.remove();
            // reindex remaining rows' data-index
            document.querySelectorAll('.stop-row').forEach((r,i)=> r.dataset.index = i);
            debouncedSave();
          }catch(e){ console.error(e); }
        }
      }
    });
  });

  // Add Stop button
  const addBtn = document.getElementById('add-stop');
  if (addBtn){
    addBtn.addEventListener('click', async function(){
      const name = prompt("Stop name:", "New stop");
      if (name === null) return;
      const time = prompt("Time (HH:MM):", "00:00") || "00:00";
      // create and append via API
      await fetch(`/api/route/${routeId}/add_stop`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({name: name, time: time, delay: 0})
      });
      // reload page to show new stop (simpler)
      location.reload();
    });
  }

  // Reset route
  const resetBtn = document.getElementById('reset-route');
  if (resetBtn){
    resetBtn.addEventListener('click', async ()=>{
      if (!confirm("Reset times & delays to defaults?")) return;
      // reload route from server by replacing with current server state:
      // We call GET then POST the saved original
      const r = await fetch(endpoint);
      const route = await r.json();
      // write route to API (it will replace)
      await fetch(endpoint, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({title: route.title, stops: route.stops})
      });
      location.reload();
    });
  }

})();
