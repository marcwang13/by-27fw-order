/**
 * BLACK YAK 27FW 線上訂貨：收單程式（Google Apps Script，綁在 Google 試算表上）
 *
 * 安裝：
 * 1. 新增一個 Google 試算表 → 選單「擴充功能」→「Apps Script」
 * 2. 把這個檔案的內容整份貼上取代原本的程式碼，儲存
 * 3. 右上「部署」→「新增部署作業」→ 類型選「網頁應用程式」
 *    執行身分：我；誰可以存取：所有人 → 部署 → 依畫面授權
 * 4. 複製「網頁應用程式網址」，貼到網站的 config.js 的 SUBMIT_URL
 *
 * 每張訂單會寫入兩個分頁：
 * - 訂單：一張單一列（同一個訂單編號再次送出會覆蓋舊資料）
 * - 明細：每個款色尺寸一列（連鎖分店會分店分開列）
 * - 另外每張訂單自動開一個分頁，分頁名＝經銷商／店名，款色一列、尺寸橫排
 *   （舊訂單要補分頁：編輯器選 rebuildOrderTabs 執行一次）
 *
 * 刪除／作廢訂單：
 * - 直接刪掉「訂單」分頁裡那一列（明細可一起刪），或把「狀態」改成「作廢」
 * - 之後客人就算從「我的訂單」修改再送出，也不會再寫進來，網頁會請客人重新下新單
 * - 隱藏分頁「_紀錄」記錄收過的訂單編號，請不要刪除
 *
 * 管理者檢視：網站網址加 ?admin=金鑰 就會出現「訂單彙整」（金鑰在 專案設定 → 指令碼屬性 ADMIN_KEY）
 * 管理者編輯：訂單彙整按「編輯訂單」→ 改數量／分店／經銷商資料 → 送出。保留原下單帳號與狀態，
 *   「最後修改」欄記錄「業務 時間」；可選擇是否寄「訂單已由業務調整」信給客人
 * 客人刪除：「我的訂單」按刪除 → 從 訂單／明細 移除、刪掉該訂單分頁、寄「訂單取消」信
 *
 * 登入：客人用 Email 收驗證碼登入後才能送單；每張單記錄「帳號 Email」，只有同一個帳號能修改／刪除
 * 客人通知：送出／修改會寄確認信＋Excel 訂單本到客人的帳號 Email；刪除會寄取消通知
 *
 * Email 通知：每張新訂單／修改都會寄信到 NOTIFY_TO（多個收件人用逗號分隔，留空就不寄）
 */

const NOTIFY_TO = 'marc_wang@emers.com,zero_wang@emers.com,zoe_chang@emers.com,vince_tian@emers.com,david_wu@emers.com,benson_wang@emers.com,max_lee@emers.com,kai_weng@emers.com';

const ORDER_HEAD = ['送出時間', '訂單編號', '經銷商／店名', '聯絡人', '電話', 'Email', '訂單備註', '款色數', '件數', '零售金額', '分店數', '分店', '狀態', '帳號 Email', '最後修改'];
const LINE_HEAD = ['送出時間', '訂單編號', '經銷商／店名', '分店', '分頁', '月份', '款號', '色碼 SKU', '英文品名', '中文品名', '顏色', '尺寸', '數量', '台灣建議售價', '零售金額'];

// 管理者金鑰存在「專案設定 → 指令碼屬性」的 ADMIN_KEY（不寫在程式裡）
function adminOk_(key) {
  const k = PropertiesService.getScriptProperties().getProperty('ADMIN_KEY');
  return !!k && String(key || '') === k;
}

function doGet(e) {
  const p = (e && e.parameter) || {};
  if (p.action === 'list') {
    if (!adminOk_(p.key)) return json_({ error: 'forbidden' });
    return json_({ orders: listOrders_(SpreadsheetApp.getActiveSpreadsheet()) });
  }
  return ContentService.createTextOutput('BLACK YAK 27FW 收單程式運作中');
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

// 給網站「訂單彙整」用：訂單＋明細
function listOrders_(ss) {
  const os = sheet_(ss, '訂單', ORDER_HEAD), ls = sheet_(ss, '明細', LINE_HEAD);
  const on = os.getLastRow(), ln = ls.getLastRow();
  if (on < 2) return [];
  const H = h => ORDER_HEAD.indexOf(h);
  const iso = v => v instanceof Date ? v.toISOString() : String(v || '');
  const byOid = {};
  (ln < 2 ? [] : ls.getRange(2, 1, ln - 1, LINE_HEAD.length).getValues()).forEach(r => {
    (byOid[String(r[1])] = byOid[String(r[1])] || []).push({ branch: String(r[3] || ''), sheet: r[4], mon: r[5], style: r[6], sku: r[7], en: r[8], zh: r[9],
      color: r[10], size: String(r[11]), qty: Number(r[12] || 0), price: Number(r[13] || 0) });
  });
  return os.getRange(2, 1, on - 1, ORDER_HEAD.length).getValues().filter(o => o[1]).map(o => ({
    oid: String(o[1]), submittedAt: iso(o[0]), store: String(o[2] || ''), contact: String(o[3] || ''), phone: String(o[4] || ''),
    email: String(o[5] || ''), note: String(o[6] || ''), styles: Number(o[H('款色數')] || 0), qty: Number(o[H('件數')] || 0),
    amount: Number(o[H('零售金額')] || 0), status: String(o[H('狀態')] || '已送出'), account: String(o[H('帳號 Email')] || '').toLowerCase(),
    edited: String(o[H('最後修改')] || ''), lines: byOid[String(o[1])] || []
  }));
}

// 管理者在網站改狀態（例如「已確認」）
function setStatus_(ss, oid, status) {
  const os = sheet_(ss, '訂單', ORDER_HEAD);
  const row = findOid_(os, oid);
  if (!row) return 'deleted';
  os.getRange(row, ORDER_HEAD.indexOf('狀態') + 1).setValue(status);
  const log = logSheet_(ss), n = log.getLastRow();
  if (n) log.getRange(1, 1, n, 3).getValues().forEach(v => {
    if (String(v[0]) === oid && v[2] && ss.getSheetByName(String(v[2]))) ss.getSheetByName(String(v[2])).getRange(9, 2).setValue(status);
  });
  return 'ok';
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const d = JSON.parse(e.postData.contents);
    if (d && d.action === 'otp_send') return out_(otpSend_(d.email));
    if (d && d.action === 'otp_verify') return out_(JSON.stringify(otpVerify_(d.email, d.code)));
    const acct = authEmail_(d && d.auth);
    if (d && d.action === 'mine') {
      if (!acct) return out_(JSON.stringify({ error: 'login_required' }));
      return out_(JSON.stringify({ orders: listOrders_(SpreadsheetApp.getActiveSpreadsheet()).filter(o => o.account === acct) }));
    }
    if (d && d.action === 'cancel' && d.oid) {
      if (!acct) return out_('login_required');
      return out_(cancel_(SpreadsheetApp.getActiveSpreadsheet(), String(d.oid), acct));
    }
    if (d && d.action === 'admin_delete' && d.oid) return out_(adminOk_(d.key) ? cancel_(SpreadsheetApp.getActiveSpreadsheet(), String(d.oid), '', true) : 'forbidden');
    if (d && d.action === 'status' && d.oid) return out_(adminOk_(d.key) ? setStatus_(SpreadsheetApp.getActiveSpreadsheet(), String(d.oid), String(d.status || '已確認')) : 'forbidden');
    if (d && d.action === 'admin_save') {
      if (!adminOk_(d.key)) return out_('forbidden');
      if (!d.oid || !Array.isArray(d.lines)) return out_('invalid');
      return out_(saveOrder_(SpreadsheetApp.getActiveSpreadsheet(), d, '', true));
    }
    if (!d || !d.oid || !Array.isArray(d.lines)) return out_('invalid');
    if (!acct) return out_('login_required');
    return out_(saveOrder_(SpreadsheetApp.getActiveSpreadsheet(), d, acct, false));
  } catch (err) {
    return out_('error: ' + err);
  } finally {
    lock.releaseLock();
  }
}

// 寫入一張訂單（客人送出／修改，或管理者編輯）
// 管理者編輯：不看登入帳號，保留原本的「帳號 Email」「送出時間」「狀態」，最後修改記「業務」
function saveOrder_(ss, d, acct, byAdmin) {
  const os = sheet_(ss, '訂單', ORDER_HEAD);
  const ls = sheet_(ss, '明細', LINE_HEAD);
  const log = logSheet_(ss);
  const H = h => ORDER_HEAD.indexOf(h);
  const seen = log.getLastRow() > 0 && log.getRange(1, 1, log.getLastRow(), 1).getValues().some(r => String(r[0]) === String(d.oid));
  const row = findOid_(os, d.oid);
  const prev = row ? os.getRange(row, 1, 1, ORDER_HEAD.length).getValues()[0] : null;
  if (prev && String(prev[H('狀態')]).trim() === '作廢') return 'void';
  if (byAdmin) {
    if (!prev) return 'deleted';
    acct = String(prev[H('帳號 Email')] || '').toLowerCase();
  } else if (prev) {
    const owner = String(prev[H('帳號 Email')] || '').toLowerCase();
    if (owner && owner !== acct) return 'forbidden';
  }
  if (seen && !row) return 'deleted';
  if (!seen) log.appendRow([d.oid, new Date()]);
  removeOid_(os, d.oid);
  removeOid_(ls, d.oid);

  const now = new Date();
  const t = byAdmin ? (prev[0] instanceof Date ? prev[0] : new Date(prev[0] || now)) : (d.submittedAt ? new Date(d.submittedAt) : now);
  const status = byAdmin ? (String(prev[H('狀態')] || '').trim() || '已送出') : (d.status || '已送出');
  const edited = byAdmin ? '業務 ' + Utilities.formatDate(now, 'Asia/Taipei', 'yyyy/MM/dd HH:mm') : (seen ? '客人 ' + Utilities.formatDate(now, 'Asia/Taipei', 'yyyy/MM/dd HH:mm') : '');
  const branches = Array.isArray(d.branches) ? d.branches : [];
  os.appendRow([t, d.oid, d.store || '', d.contact || '', d.phone || '', d.email || '', d.note || '',
    d.styles || 0, d.qty || 0, d.amount || 0, branches.length || '', branches.map(b => b.name).join('、'), status, acct, edited]);

  const info = {};
  d.lines.forEach(l => { info[l.k] = l; });
  const rows = [];
  const push = (branch, l, qty) => {
    const x = info[l.k] || l;
    rows.push([t, d.oid, d.store || '', branch, x.sheet || '', x.mon || '', x.style || '', x.sku || '', x.en || '', x.zh || '', x.color || '',
      l.size, qty, x.price || 0, qty * (x.price || 0)]);
  };
  if (branches.length) {
    branches.forEach(b => (b.lines || []).forEach(l => push(b.name, l, l.qty)));
  } else {
    d.lines.forEach(l => push('', l, l.qty));
  }
  if (rows.length) ls.getRange(ls.getLastRow() + 1, 1, rows.length, LINE_HEAD.length).setValues(rows);
  try {
    writeOrderTab_(ss, log, d.oid, { t: t, store: d.store, contact: d.contact, phone: d.phone, email: d.email, note: d.note,
      branches: branches.map(b => b.name).join('、'), styles: d.styles, qty: d.qty, amount: d.amount, status: status }, rows);
  } catch (err) { console.error('order tab failed: ' + err); }
  d.account = acct;
  let att = null;
  try { if (d._xlsx) att = Utilities.newBlob(Utilities.base64Decode(d._xlsx), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', String(d._xlsxName || ('BLACKYAK_27FW_訂單本_' + d.oid + '.xlsx'))); } catch (err) { console.error('xlsx decode failed: ' + err); }
  if (byAdmin) {
    try { notify_(ss, d, rows, true, '訂單修改（業務）', att); } catch (err) { console.error('notify failed: ' + err); }
    if (d.notifyCustomer !== false) { try { customerMail_(d, rows, '訂單已由業務調整', acct, att); } catch (err) { console.error('customer mail failed: ' + err); } }
  } else {
    try { notify_(ss, d, rows, seen, null, att); } catch (err) { console.error('notify failed: ' + err); }
    try { customerMail_(d, rows, seen ? '訂單已更新' : '訂單確認', acct, att); } catch (err) { console.error('customer mail failed: ' + err); }
  }
  return 'ok';
}

function sheet_(ss, name, head) {
  let sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.getRange(1, 1, 1, head.length).setValues([head]).setFontWeight('bold').setBackground('#141414').setFontColor('#ffffff');
    sh.setFrozenRows(1);
  } else if (sh.getLastColumn() < head.length) {
    const from = sh.getLastColumn() + 1;
    sh.getRange(1, from, 1, head.length - from + 1).setValues([head.slice(from - 1)]).setFontWeight('bold').setBackground('#141414').setFontColor('#ffffff');
  }
  return sh;
}

function logSheet_(ss) {
  let sh = ss.getSheetByName('_紀錄');
  if (!sh) { sh = ss.insertSheet('_紀錄'); sh.hideSheet(); }
  return sh;
}

function findOid_(sh, oid) {
  const n = sh.getLastRow();
  if (n < 2) return 0;
  const ids = sh.getRange(2, 2, n - 1, 1).getValues();
  for (let i = 0; i < ids.length; i++) if (String(ids[i][0]) === String(oid)) return i + 2;
  return 0;
}

function removeOid_(sh, oid) {
  const n = sh.getLastRow();
  if (n < 2) return;
  const ids = sh.getRange(2, 2, n - 1, 1).getValues();
  for (let i = ids.length - 1; i >= 0; i--) {
    if (String(ids[i][0]) === String(oid)) sh.deleteRow(i + 2);
  }
}

// ── 每張訂單一個分頁（分頁名＝經銷商／店名）──────────────────────────
const SIZE_ORDER = ['XXS', 'XS', 'S', 'M', 'L', 'XL', '2XL', 'XXL', '3XL', '4XL', 'FREE', 'FREE SIZE', 'F'];
const RESERVED_TABS = ['訂單', '明細', '_紀錄'];

function sizeCmp_(a, b) {
  const k = s => {
    s = String(s).toUpperCase().trim();
    const i = SIZE_ORDER.indexOf(s);
    if (i >= 0) return [0, i, ''];
    const n = parseFloat(s);
    if (!isNaN(n)) return [1, n, s];
    return [2, 0, s];
  };
  const x = k(a), y = k(b);
  for (let i = 0; i < 3; i++) { if (x[i] < y[i]) return -1; if (x[i] > y[i]) return 1; }
  return 0;
}

// 找這張訂單已經用的分頁名；沒有就用店名開一個（同名就加 (2)、(3)）
function tabName_(ss, log, oid, store) {
  const n = log.getLastRow();
  const vals = n ? log.getRange(1, 1, n, 3).getValues() : [];
  let at = -1;
  for (let i = 0; i < vals.length; i++) if (String(vals[i][0]) === String(oid)) { at = i; break; }
  if (at >= 0 && vals[at][2] && ss.getSheetByName(vals[at][2])) return String(vals[at][2]);
  const used = vals.filter((v, i) => i !== at && v[2]).map(v => String(v[2]));
  const base = (String(store || '').replace(/[\[\]\*\?:\\\/]/g, '-').trim() || String(oid)).slice(0, 90);
  let name = base, k = 2;
  while (RESERVED_TABS.indexOf(name) >= 0 || used.indexOf(name) >= 0 || ss.getSheetByName(name)) name = `${base} (${k++})`;
  if (at >= 0) log.getRange(at + 1, 3).setValue(name);
  else log.appendRow([oid, new Date(), name]);
  return name;
}

// rows 欄位同 LINE_HEAD：0時間 1編號 2店名 3分店 4分頁 5月份 6款號 7SKU 8英文 9中文 10顏色 11尺寸 12數量 13售價 14金額
function writeOrderTab_(ss, log, oid, m, rows) {
  const name = tabName_(ss, log, oid, m.store);
  const sh = ss.getSheetByName(name) || ss.insertSheet(name, ss.getNumSheets());
  sh.clear();
  sh.setFrozenRows(0);

  const groups = {}, order = [], sizes = [];
  rows.forEach(r => {
    const key = [r[3], r[7], r[6], r[10]].join('|');
    if (!groups[key]) { groups[key] = { r: r, q: {}, qty: 0, amt: 0 }; order.push(key); }
    const g = groups[key], sz = String(r[11]);
    g.q[sz] = (g.q[sz] || 0) + Number(r[12] || 0);
    g.qty += Number(r[12] || 0); g.amt += Number(r[14] || 0);
    if (sizes.indexOf(sz) < 0) sizes.push(sz);
  });
  sizes.sort(sizeCmp_);
  const hasBranch = rows.some(r => r[3]);

  const info = [
    ['BLACK YAK 27FW 訂單', ''],
    ['訂單編號', oid],
    ['送出時間', m.t || ''],
    ['經銷商／店名', m.store || ''],
    ['聯絡人', [m.contact, m.phone, m.email].filter(Boolean).join('  ')],
    ['分店', m.branches || ''],
    ['備註', m.note || ''],
    ['合計', `${m.styles || order.length} 款色、${m.qty || 0} 件、零售金額 NT$${Number(m.amount || 0).toLocaleString('en-US')}`],
    ['狀態', m.status || ''],
  ];
  sh.getRange(1, 1, info.length, 2).setValues(info);
  sh.getRange(1, 1).setFontSize(14).setFontWeight('bold').setFontColor('#141414');
  sh.getRange(2, 1, info.length - 1, 1).setFontColor('#666666');
  sh.getRange(8, 2).setFontWeight('bold');

  const top = info.length + 2;
  const head = (hasBranch ? ['分店'] : []).concat(['分頁', '月份', '款號', '色碼 SKU', '中文品名', '英文品名', '顏色'], sizes, ['件數', '台灣建議售價', '零售金額']);
  const body = order.map(k => {
    const g = groups[k], r = g.r;
    return (hasBranch ? [r[3]] : []).concat([r[4], r[5], r[6], r[7], r[9], r[8], r[10]], sizes.map(s => g.q[s] || ''), [g.qty, r[13], g.amt]);
  });
  const tq = order.reduce((s, k) => s + groups[k].qty, 0), ta = order.reduce((s, k) => s + groups[k].amt, 0);
  const foot = head.map((_, i) => '');
  foot[0] = '合計';
  sizes.forEach((s, i) => { foot[head.length - 3 - sizes.length + i] = order.reduce((t, k) => t + (groups[k].q[s] || 0), 0); });
  foot[head.length - 3] = tq; foot[head.length - 1] = ta;

  const all = [head].concat(body, [foot]);
  sh.getRange(top, 1, all.length, head.length).setValues(all);
  sh.getRange(top, 1, 1, head.length).setFontWeight('bold').setBackground('#141414').setFontColor('#ffffff');
  sh.getRange(top + all.length - 1, 1, 1, head.length).setFontWeight('bold').setBackground('#f3e6e6');
  sh.getRange(top, 1, all.length, head.length).setBorder(true, true, true, true, true, true, '#dddddd', SpreadsheetApp.BorderStyle.SOLID);
  const firstSize = head.length - 3 - sizes.length + 1;
  sh.getRange(top, firstSize, all.length, sizes.length + 1).setHorizontalAlignment('center');
  sh.getRange(top + 1, head.length - 1, all.length - 1, 2).setNumberFormat('#,##0');
  sh.setFrozenRows(top);
  sh.autoResizeColumns(1, head.length);
}

// 用「訂單」＋「明細」把每張訂單的分頁重建一次（第一次安裝或手動整理時在編輯器執行）
function rebuildOrderTabs() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const os = sheet_(ss, '訂單', ORDER_HEAD), ls = sheet_(ss, '明細', LINE_HEAD), log = logSheet_(ss);
  const on = os.getLastRow(), ln = ls.getLastRow();
  if (on < 2) return;
  const lines = ln < 2 ? [] : ls.getRange(2, 1, ln - 1, LINE_HEAD.length).getValues();
  const H = h => ORDER_HEAD.indexOf(h);
  os.getRange(2, 1, on - 1, ORDER_HEAD.length).getValues().forEach(o => {
    const oid = String(o[1]);
    if (!oid) return;
    const rows = lines.filter(l => String(l[1]) === oid);
    writeOrderTab_(ss, log, oid, { t: o[0], store: o[2], contact: o[3], phone: o[4], email: o[5], note: o[6],
      branches: o[H('分店')], styles: o[H('款色數')], qty: o[H('件數')], amount: o[H('零售金額')], status: o[H('狀態')] }, rows);
  });
}

// 客人在「我的訂單」按刪除：從 訂單／明細 移除、刪掉該訂單分頁、寄取消通知（信裡保留原本明細）
function cancel_(ss, oid, acct, byAdmin) {
  const os = sheet_(ss, '訂單', ORDER_HEAD), ls = sheet_(ss, '明細', LINE_HEAD), log = logSheet_(ss);
  const row = findOid_(os, oid);
  if (!row) return 'deleted';
  const o = os.getRange(row, 1, 1, ORDER_HEAD.length).getValues()[0];
  const H = h => ORDER_HEAD.indexOf(h);
  if (String(o[H('狀態')]).trim() === '作廢') return 'void';
  const owner = String(o[H('帳號 Email')] || '').toLowerCase();
  if (!byAdmin && owner && owner !== acct) return 'forbidden';
  const ln = ls.getLastRow();
  const rows = ln < 2 ? [] : ls.getRange(2, 1, ln - 1, LINE_HEAD.length).getValues().filter(r => String(r[1]) === oid);
  removeOid_(os, oid);
  removeOid_(ls, oid);
  const n = log.getLastRow();
  if (n) {
    const vals = log.getRange(1, 1, n, 3).getValues();
    for (let i = 0; i < vals.length; i++) if (String(vals[i][0]) === oid) {
      const tab = vals[i][2] && ss.getSheetByName(String(vals[i][2]));
      if (tab) ss.deleteSheet(tab);
      log.getRange(i + 1, 3).setValue('');
      break;
    }
  }
  try {
    notify_(ss, { oid: oid, store: o[2], contact: o[3], phone: o[4], email: o[5], note: o[6],
      branches: String(o[H('分店')] || '').split('、').filter(Boolean).map(x => ({ name: x })),
      styles: o[H('款色數')], qty: o[H('件數')], amount: o[H('零售金額')] }, rows, false, byAdmin ? '訂單取消（業務刪除）' : '訂單取消');
  } catch (err) { console.error('notify failed: ' + err); }
  try {
    customerMail_({ oid: oid, store: o[2], contact: o[3], phone: o[4], email: o[5], note: o[6],
      branches: String(o[H('分店')] || '').split('、').filter(Boolean).map(x => ({ name: x })),
      styles: o[H('款色數')], qty: o[H('件數')], amount: o[H('零售金額')] }, rows, byAdmin ? '訂單已由業務取消' : '訂單已取消', owner || acct, null);
  } catch (err) { console.error('customer mail failed: ' + err); }
  return 'ok';
}

function orderHtml_(d, rows, title, intro, footer) {
  const esc = v => String(v == null ? '' : v).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const fmt = n => Number(n || 0).toLocaleString('en-US');
  // 依分店、款色彙整成一行一款：M×4 L×2
  const groups = {};
  rows.forEach(r => { const key = [r[3], r[6], r[7], r[9], r[10]].join('|'); (groups[key] = groups[key] || { branch: r[3], style: r[6], sku: r[7], zh: r[9], color: r[10], sizes: [], qty: 0, amt: 0 });
    groups[key].sizes.push(`${r[11]}×${r[12]}`); groups[key].qty += Number(r[12]); groups[key].amt += Number(r[14]); });
  const list = Object.values(groups);
  const hasBranch = list.some(g => g.branch);
  const tr = list.map(g => `<tr>${hasBranch ? `<td>${esc(g.branch)}</td>` : ''}<td>${esc(g.style)}<br><span style="color:#888">${esc(g.sku)}</span></td><td>${esc(g.zh)}</td><td>${esc(g.color)}</td><td>${esc(g.sizes.join('  '))}</td><td style="text-align:right">${g.qty}</td><td style="text-align:right">${fmt(g.amt)}</td></tr>`).join('');
  const th = s => `<th style="background:#141414;color:#fff;padding:6px 8px;text-align:left;font-weight:600">${s}</th>`;
  return `<div style="font-family:Arial,'Microsoft JhengHei',sans-serif;font-size:14px;color:#222">
  <h2 style="color:#141414;margin:0 0 8px">BLACK YAK 27FW ${esc(title)}</h2>
  ${intro ? `<p style="margin:0 0 12px">${intro}</p>` : ''}
  <table style="border-collapse:collapse;margin-bottom:12px">
  <tr><td style="color:#666;padding:2px 12px 2px 0">訂單編號</td><td><b>${esc(d.oid)}</b></td></tr>
  <tr><td style="color:#666;padding:2px 12px 2px 0">經銷商／店名</td><td>${esc(d.store)}</td></tr>
  <tr><td style="color:#666;padding:2px 12px 2px 0">聯絡人</td><td>${esc(d.contact)} ${esc(d.phone)} ${esc(d.email)}</td></tr>
  ${d.account ? `<tr><td style="color:#666;padding:2px 12px 2px 0">下單帳號</td><td>${esc(d.account)}</td></tr>` : ''}
  ${d.note ? `<tr><td style="color:#666;padding:2px 12px 2px 0">備註</td><td>${esc(d.note)}</td></tr>` : ''}
  ${(d.branches || []).length ? `<tr><td style="color:#666;padding:2px 12px 2px 0">分店</td><td>${esc(d.branches.map(b => b.name).join('、'))}</td></tr>` : ''}
  <tr><td style="color:#666;padding:2px 12px 2px 0">合計</td><td><b>${fmt(d.styles)} 款色、${fmt(d.qty)} 件、零售金額 NT$${fmt(d.amount)}</b></td></tr>
  </table>
  ${list.length ? `<table style="border-collapse:collapse;font-size:13px" border="1" bordercolor="#ddd" cellpadding="6">
  <tr>${hasBranch ? th('分店') : ''}${th('款號')}${th('品名')}${th('顏色')}${th('尺寸×數量')}${th('件數')}${th('零售金額')}</tr>${tr}</table>` : ''}
  ${footer || ''}</div>`;
}

function notify_(ss, d, rows, isEdit, kindOverride, att) {
  if (!NOTIFY_TO) return;
  const fmt = n => Number(n || 0).toLocaleString('en-US');
  const kind = kindOverride || (isEdit ? '訂單修改' : '新訂單');
  const subject = `【BLACK YAK 27FW ${kind}】${d.store || '（未填店名）'}｜${fmt(d.qty)} 件｜NT$${fmt(d.amount)}`;
  const html = orderHtml_(d, rows, kind, '', `<p><a href="${ss.getUrl()}" style="color:#141414">開啟 Google 試算表看完整訂單</a></p>`);
  const msg = { to: NOTIFY_TO, subject: subject, htmlBody: html, name: 'BLACK YAK 27FW 線上訂貨' };
  if (att) msg.attachments = [att];
  MailApp.sendEmail(msg);
}

// 寄給客人（帳號 Email）：訂單確認／已更新附 Excel 訂單本；取消只寄通知
function customerMail_(d, rows, kind, to, att) {
  if (!to) return;
  const intro = kind === '訂單已由業務取消'
    ? 'BLACK YAK 業務已取消這張訂單，以下是原本的內容供您留存。如有疑問請直接回覆此信。'
    : kind === '訂單已取消'
    ? '您的這張訂單已經取消，以下是原本的內容供您留存。如非本人操作，請盡快聯絡 BLACK YAK 業務。'
    : kind === '訂單已由業務調整'
    ? `BLACK YAK 業務已依雙方討論調整這張訂單，以下是調整後的內容。${att ? '最新的 Excel 訂單本在附件。' : ''}如有疑問請直接回覆此信。`
    : `感謝您的訂購，${kind === '訂單已更新' ? '訂單已更新為以下內容' : '我們已收到您的訂單'}。${att ? '完整的 Excel 訂單本在附件。' : ''}如需修改或刪除，請到下單網站的「我的訂單」操作。`;
  const html = orderHtml_(d, rows, kind, intro, '<p style="color:#888;font-size:12px">此信由系統自動寄出，有任何問題請直接回覆此信或聯絡 BLACK YAK 業務。</p>');
  const msg = { to: to, subject: `【BLACK YAK 27FW】${kind}｜${d.oid}`, htmlBody: html, name: 'BLACK YAK 台灣', replyTo: NOTIFY_TO.split(',')[0].trim() };
  if (att) msg.attachments = [att];
  MailApp.sendEmail(msg);
}

// ── Email 驗證碼登入 ─────────────────────────────────────────
function authSecret_() {
  const pr = PropertiesService.getScriptProperties();
  let k = pr.getProperty('AUTH_SECRET');
  if (!k) { k = Utilities.getUuid() + Utilities.getUuid(); pr.setProperty('AUTH_SECRET', k); }
  return k;
}
function normEmail_(e) {
  const s = String(e || '').trim().toLowerCase();
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s) ? s : '';
}
function tokenFor_(email) {
  return Utilities.base64EncodeWebSafe(Utilities.computeHmacSha256Signature(email, authSecret_()));
}
function authEmail_(a) {
  if (!a) return '';
  const em = normEmail_(a.email);
  return em && a.token && String(a.token) === tokenFor_(em) ? em : '';
}
function otpSend_(email) {
  const em = normEmail_(email);
  if (!em) return 'invalid_email';
  const c = CacheService.getScriptCache();
  if (c.get('otpwait:' + em)) return 'wait';
  const code = String(Math.floor(100000 + Math.random() * 900000));
  c.put('otp:' + em, code, 600);
  c.put('otptry:' + em, '0', 600);
  c.put('otpwait:' + em, '1', 60);
  MailApp.sendEmail({ to: em, subject: `BLACK YAK 27FW 線上訂貨 登入驗證碼：${code}`, name: 'BLACK YAK 台灣',
    htmlBody: `<div style="font-family:Arial,'Microsoft JhengHei',sans-serif;font-size:14px;color:#222"><h2 style="color:#141414;margin:0 0 8px">BLACK YAK 27FW 線上訂貨</h2><p>您的登入驗證碼是：</p><p style="font-size:28px;font-weight:bold;letter-spacing:6px;margin:8px 0">${code}</p><p style="color:#666">10 分鐘內有效。如果不是您本人要登入，請忽略這封信。</p></div>` });
  return 'ok';
}
function otpVerify_(email, code) {
  const em = normEmail_(email);
  if (!em) return { error: 'invalid_email' };
  const c = CacheService.getScriptCache();
  const want = c.get('otp:' + em);
  if (!want) return { error: 'expired' };
  const tries = Number(c.get('otptry:' + em) || 0) + 1;
  c.put('otptry:' + em, String(tries), 600);
  if (tries > 5) { c.remove('otp:' + em); return { error: 'too_many' }; }
  if (String(code || '').trim() !== want) return { error: 'bad_code' };
  c.remove('otp:' + em);
  return { email: em, token: tokenFor_(em) };
}

function out_(s) {
  return ContentService.createTextOutput(s);
}
