#!/usr/bin/env node
// Kiểm thử tìm kiếm với dữ liệu thật, dùng đúng scripts/search.js mà web nhúng vào.
//   node scripts/check_search.js              chạy data/search_tests.json, exit 1 nếu có câu không đạt
//   node scripts/check_search.js "vm treo" ... in kết quả hàng đầu của từng câu tìm
const fs = require('fs');
const path = require('path');
const {createSearch, createIndex} = require('./search.js');

const ROOT = path.resolve(__dirname, '..');
const load = f => JSON.parse(fs.readFileSync(path.join(ROOT, 'data', f), 'utf8'));
const DATA = load('commands.json'), vi = load('vi.json');
Object.values(DATA).forEach(bs => bs.forEach(b => b.subs.forEach(s => s.items.forEach(it => {
  if (vi[it.c]) [it.v, it.k] = vi[it.c];
}))));
const GUIDES = load('guides.json').map(g => ({...g, md: fs.readFileSync(path.join(ROOT, g.file), 'utf8')}));
const engine = createSearch(load('synonyms.json'));
const index = createIndex(engine, {DATA, CASES: load('cases.json'), SCRIPTS: load('scripts.json'), TRIAGE: load('triage.json'), GUIDES,
  TOPICS: load('topics.json'), LABELS: load('labels_vi.json')});

const queries = process.argv.slice(2);
if (queries.length) {
  for (const q of queries) {
    const r = index.query(q);
    console.log(`\n"${q}" → ${r.commands.length} lệnh, ${r.cases.length} case/runbook, ${r.scripts.length} script, ${r.guides.length} bài viết, ${r.triage.length} triage`);
    console.log('  ý tìm:', r.terms.map(t => t.alts.length > 1 ? `${t.raw}(+${t.alts.length - 1})` : t.raw).join(' · '));
    r.guides.slice(0, 3).forEach(x => console.log(`  bài   ${x.score.toFixed(1).padStart(5)}  ${x.g.id}`));
    r.cases.slice(0, 5).forEach(x => console.log(`  case  ${x.score.toFixed(1).padStart(5)}  ${x.c.id}`));
    r.commands.slice(0, 5).forEach(x => console.log(`  lệnh  ${x.score.toFixed(1).padStart(5)}  ${x.b.id}  ${x.it.c}`));
  }
  process.exit(0);
}

// Mỗi test: q, tùy chọn min (tổng kết quả tối thiểu, mặc định 1), top_case (id phải nằm trong 3 case đầu),
// top_command (lệnh phải nằm trong 5 lệnh đầu), top_guide (bài viết đứng đầu), max_commands (chặn kết quả rác).
const tests = load('search_tests.json');
let fail = 0;
for (const t of tests) {
  const r = index.query(t.q), errs = [];
  const total = r.commands.length + r.cases.length + r.scripts.length + r.guides.length + r.triage.length;
  if (total < (t.min ?? 1)) errs.push(`chỉ có ${total} kết quả`);
  if (t.top_case && !r.cases.slice(0, 3).some(x => x.c.id === t.top_case))
    errs.push(`case ${t.top_case} không nằm trong top 3 (đang là: ${r.cases.slice(0, 3).map(x => x.c.id).join(', ') || 'không có'})`);
  if (t.top_command && !r.commands.slice(0, 5).some(x => x.it.c === t.top_command))
    errs.push(`lệnh "${t.top_command}" không nằm trong top 5`);
  if (t.top_guide && r.guides[0]?.g.id !== t.top_guide)
    errs.push(`bài viết ${t.top_guide} không đứng đầu (đang là: ${r.guides[0]?.g.id || 'không có'})`);
  if (t.max_commands != null && r.commands.length > t.max_commands)
    errs.push(`${r.commands.length} lệnh, vượt giới hạn ${t.max_commands}`);
  if (errs.length) { fail++; console.log(`KHÔNG ĐẠT "${t.q}": ${errs.join('; ')}`); }
}
console.log(`search: ${tests.length - fail}/${tests.length} câu tìm mẫu đạt`);
process.exit(fail ? 1 : 0);
