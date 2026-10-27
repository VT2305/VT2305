const form = document.querySelector('#search-form');
const button = document.querySelector('#search-button');
const query = document.querySelector('#query');
const cards = document.querySelector('#cards');
const errorBox = document.querySelector('#error');
const intentPanel = document.querySelector('#intent-panel');
const intentTags = document.querySelector('#intent-tags');
const countMessage = document.querySelector('#count-message');
const modeUsed = document.querySelector('#mode-used');
const resultCount = document.querySelector('#result-count');

function node(tag, css, value) {
  const el = document.createElement(tag);
  if (css) el.className = css;
  if (value !== undefined) el.textContent = String(value);
  return el;
}
function chip(text, type='') { return node('span', `tag ${type}`, text); }
function metric(name, value) {
  const outer = node('div', '');
  outer.append(node('span', '', name), node('b', '', value));
  return outer;
}
function renderProduct(result, index) {
  const { product, score_breakdown: s, score } = result;
  const card = node('article', 'card');
  const head = node('div', 'card-head');
  const itemTop = node('div', 'item-top');
  itemTop.append(node('span','category',`${String(index + 1).padStart(2,'0')} / ${product.category}`), node('span','score',`${Math.round(score)} / 100`));
  head.append(itemTop, node('h3','',product.name),node('p','item-desc',product.description));
  const body = node('div','card-body');
  const prices = node('div','price-row');
  prices.append(node('span','price',`$${product.price_usd.toFixed(0)}`),node('span','demo','USD / FICTIONAL'));
  const features = node('div','features');
  for (const feature of product.features.slice(0,6)) features.append(node('span','feature',feature));
  const why = node('div','why');
  why.append(node('div','why-title','WHY THIS MATCHES'),node('p','',result.explanation));
  const metrics = node('div','metric');
  metrics.append(metric('Preferences',`${Math.round(s.preference_match*100)}%`),metric('Price value',`${Math.round(s.price_value*100)}%`),metric('Demo rating',`${product.rating.toFixed(1)}/5`));
  body.append(prices,features,why,metrics);
  card.append(head,body); return card;
}
function render(data) {
  cards.replaceChildren(); intentTags.replaceChildren();
  intentPanel.hidden = false;
  modeUsed.textContent = `${data.parser_used.toUpperCase()} PARSER`;
  const i=data.intent;
  if (i.category) intentTags.append(chip(`CATEGORY · ${i.category}`,'hard'));
  if (i.max_price_usd !== null) intentTags.append(chip(`MAX · $${i.max_price_usd}`,'hard'));
  if (i.min_battery_hours !== null) intentTags.append(chip(`BATTERY · ≥${i.min_battery_hours}h`,'hard'));
  for (const f of i.required_features) intentTags.append(chip(`MUST · ${f}`,'hard'));
  for (const f of i.excluded_features) intentTags.append(chip(`EXCLUDE · ${f}`,'hard'));
  for (const f of i.preferences) intentTags.append(chip(`PREFER · ${f}`,'soft'));
  if (!intentTags.children.length) intentTags.append(chip('NO STRUCTURED CONSTRAINTS DETECTED'));
  countMessage.textContent = data.message;
  resultCount.textContent = `${data.eligible_count} qualifying · ${data.results.length} shown`;
  if (!data.results.length) {
    const empty = node('div','initial-state');
    empty.append(node('div','initial-orbit','∅'),node('p','','No eligible products'),node('span','',data.suggestions.join(' ')));
    cards.append(empty); return;
  }
  for (const [index,result] of data.results.entries()) cards.append(renderProduct(result,index));
}
async function performSearch(event) {
  event?.preventDefault();
  errorBox.hidden = true;
  button.disabled = true;
  button.textContent='Finding matches…';
  try {
    const res = await fetch('/api/search', {
      method: 'POST', headers: {'content-type':'application/json'},
      body: JSON.stringify({ query: query.value, parser: document.querySelector('#parser').value, top_k: 6 })
    });
    const data=await res.json();
    if (!res.ok) throw new Error(typeof data.detail==='string' ? data.detail : 'Could not complete search. Please check your input.');
    render(data);
    document.querySelector('#results-section').scrollIntoView({behavior:'smooth',block:'start'});
  } catch (err) {
    errorBox.textContent=err instanceof Error ? err.message : 'Search failed.';
    errorBox.hidden=false;
  } finally {
    button.disabled=false;
    button.replaceChildren(document.createTextNode('Explore matches '),node('span','','↗'));
  }
}
form.addEventListener('submit',performSearch);
for (const example of document.querySelectorAll('[data-query]')) {
  example.addEventListener('click',()=>{query.value=example.dataset.query;performSearch();});
}
fetch('/api/catalogue').then(r=>r.json()).then(d=>{
  document.querySelector('#catalogue-count').textContent=`${d.count} fictional demo products`;
}).catch(()=>{});
