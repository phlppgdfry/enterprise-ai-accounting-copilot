// Mirrors Invoice (models.py) and the flags in Store.submit (store.py). Amounts are parsed as strings into
// whole cents, like Python's Decimal: no binary floating point is involved.
const $ = id => document.getElementById(id);
const APPROVED = ['synthetic-office'];
function cents(s, name, { gt0 = false } = {}) {
  s = String(s).trim();
  if (!/^-?\d+(\.\d{1,2})?$/.test(s)) throw `${name}: use a number with at most two decimals`;
  const [i, f = ''] = s.replace('-', '').split('.');
  if ((i.replace(/^0+/, '') || '0').length + 2 > 12) throw `${name}: at most 12 digits`;
  const v = BigInt(i) * 100n + BigInt((f + '00').slice(0, 2));
  const signed = s.startsWith('-') ? -v : v;
  if (gt0 ? signed <= 0n : signed < 0n) throw `${name} must be ${gt0 ? 'greater than 0' : '0 or more'}`;
  return signed;
}
const eur = c => '€' + (Number(c) / 100).toLocaleString('en-BE', { minimumFractionDigits: 2 });
function check() {
  const out = [], today = new Date().toISOString().slice(0, 10);
  let net, vat, total, valid = true;
  try { net = cents($('ac-net').value, 'Net', { gt0: true }); out.push(['ok', 'Net is a valid amount', eur(net)]); } catch (e) { out.push(['bad', e]); valid = false; }
  try { vat = cents($('ac-vat').value, 'VAT'); out.push(['ok', 'VAT is a valid amount', eur(vat)]); } catch (e) { out.push(['bad', e]); valid = false; }
  try { total = cents($('ac-total').value, 'Total', { gt0: true }); out.push(['ok', 'Total is a valid amount', eur(total)]); } catch (e) { out.push(['bad', e]); valid = false; }
  if (valid) {
    if (net + vat !== total) { out.push(['bad', `net + vat must equal total exactly`, `${eur(net + vat)} ≠ ${eur(total)}`]); valid = false; }
    else out.push(['ok', 'net + vat = total, to the cent', (Number($('ac-net').value) + Number($('ac-vat').value) !== Number($('ac-total').value)) ? 'binary floats would wrongly say no' : '']);
    if (vat > net) { out.push(['bad', 'VAT exceeds net; investigate source document']); valid = false; }
  }
  if (!valid) return { status: ['bad', 'HTTP 422 · rejected', 'The API refuses this invoice; nothing is stored.'], out };
  const flags = [];
  if (!APPROVED.includes($('ac-sup').value)) flags.push(['supplier_not_approved', 'Supplier is not on the approved list']);
  if ($('ac-date').value > today) flags.push(['future_invoice_date', 'Invoice date lies in the future']);
  if (total > 1000000n) flags.push(['high_value', 'Total above €10,000']);
  flags.forEach(([k, t]) => out.push(['warn', t, k]));
  if (!flags.length) out.push(['ok', 'No review flags']);
  return { status: flags.length ? ['warn', 'blocked', 'Stored, but blocked: a reviewer must look at the flags and decide with a reason.'] : ['ok', 'pending_review', 'Stored and waiting for a reviewer other than the submitter. Only after approval does the outbox export it to the mock ERP.'], out };
}
function render() {
  const { status: [c, s, t], out } = check();
  $('ac-status').innerHTML = `<span class="pill ${c}">${s}</span><p>${t}</p>`;
  $('ac-checks').innerHTML = out.map(([c, t, d]) => `<li><span class="pill ${c}">${c === 'ok' ? '✓' : c === 'warn' ? 'flag' : '✗'}</span><span>${t}${d ? ` <span class="dim mono small">${d}</span>` : ''}</span></li>`).join('');
}
const PRESETS = {
  'Valid invoice': ['synthetic-office', '2026-01-10', '100.00', '21.00', '121.00'],
  'Off by one cent': ['synthetic-office', '2026-01-10', '100.00', '21.00', '121.01'],
  '0.20 + 0.10 = 0.30 (float trap)': ['synthetic-office', '2026-01-10', '0.20', '0.10', '0.30'],
  'Unknown supplier, €12,000': ['unknown-supplier', '2026-01-10', '9917.36', '2082.64', '12000.00'],
  'Three decimals': ['synthetic-office', '2026-01-10', '100.001', '21.00', '121.00'],
};
$('ac-presets').innerHTML = Object.keys(PRESETS).map(k => `<button type="button">${k}</button>`).join('');
$('ac-presets').addEventListener('click', e => { const v = PRESETS[e.target.textContent]; if (!v) return; ['ac-sup', 'ac-date', 'ac-net', 'ac-vat', 'ac-total'].forEach((id, i) => $(id).value = v[i]); render(); });
['ac-sup', 'ac-date', 'ac-net', 'ac-vat', 'ac-total'].forEach(id => $(id).addEventListener('input', render));
render();
