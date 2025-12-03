const API_BASE="http://localhost:5000";
let layout=null,simTime=null,playing=true,speed=1;
async function loadLayout(){layout=await (await fetch(API_BASE+"/api/layout")).json();drawLayout();}
function drawLayout(){const c=document.getElementById("mapContainer");c.innerHTML="";
layout.locations.forEach(l=>{const d=document.createElement("div");d.className="location "+(l.type==="lift"?"lift":"");
d.dataset.locId=l.id;d.style.left=l.x+"px";d.style.top=l.y+"px";d.textContent=l.id;c.appendChild(d);});}
function updateStatuses(eq){const map={};eq.forEach(e=>map[e.id]=e);
document.querySelectorAll(".location").forEach(div=>{const id=div.dataset.locId;div.classList.remove("ok","fault");
if(!map[id])div.classList.add("ok");else div.classList.add(map[id].status==="fault"?"fault":"ok");});}
function renderPallets(p){document.querySelectorAll(".pallet").forEach(p=>p.remove());
const c=document.getElementById("mapContainer");p.forEach(pl=>{const loc=document.querySelector(`.location[data-loc-id='${pl.currentLocation}']`);
if(!loc)return;const r=loc.getBoundingClientRect(),cr=c.getBoundingClientRect();
const d=document.createElement("div");d.className="pallet";d.textContent=pl.id.slice(-2);
d.style.left=(r.left-cr.left+5)+"px";d.style.top=(r.top-cr.top-18)+"px";c.appendChild(d);});}
function renderFaults(eq){const ul=document.getElementById("faultList");ul.innerHTML="";
eq.filter(e=>e.status==="fault").forEach(e=>{const li=document.createElement("li");
li.textContent=`${e.id} – ${Math.round(e.totalFaultSeconds)}s`;ul.appendChild(li);});}
async function fetchState(){if(!layout)return;const p=simTime?`?time=${simTime.toISOString()}`:"";
const d=await (await fetch(API_BASE+"/api/state"+p)).json();simTime=new Date(d.simTime);
document.getElementById("timeLabel").textContent="Time: "+d.simTime;
updateStatuses(d.equipment);renderPallets(d.pallets);renderFaults(d.equipment);}
function loop(){setInterval(()=>{if(!playing||!simTime)return;simTime=new Date(simTime.getTime()+speed*1000);fetchState();},1000);}
async function showHistory(){const id=document.getElementById("palletInput").value.trim();if(!id)return;
const d=await (await fetch(API_BASE+"/api/pallet/"+id+"/history")).json();
const ul=document.getElementById("palletHistoryList");ul.innerHTML="";
d.events.forEach(ev=>{const li=document.createElement("li");
li.textContent=`${ev.timestamp} – ${ev.messageType} ${ev.from||""}->${ev.to||""}`;ul.appendChild(li);});}
function controls(){document.getElementById("playPauseBtn").onclick=()=>{playing=!playing;
document.getElementById("playPauseBtn").textContent=playing?"Pause":"Play";};
document.getElementById("speedSelect").onchange=e=>speed=Number(e.target.value);
document.getElementById("palletHistoryBtn").onclick=showHistory;}
async function init(){controls();await loadLayout();await fetchState();loop();}init();
