// Phân loại rủi ro lệnh theo ĐỘNG TỪ CHÍNH, dùng khi lệnh không có trong data/command_risk.json.
// Chỉ trả 'ro' (chỉ đọc) hoặc 'chg' (thay đổi); 'dg' (nguy hiểm) luôn khai báo tay trong command_risk.json.
// Chữ nằm trong chuỗi '...' / "..." (mẫu grep, tham số) bị bỏ qua, nên grep 'error|set' vẫn là chỉ đọc.
const RISK_RO_VERBS = new Set(('dmesg grep egrep fgrep zgrep zcat cat less more head tail journalctl ls ll df du lsblk blkid findmnt ' +
  'free uptime uname hostname hostnamectl timedatectl date ps pgrep top htop iotop atop ss netstat ping arping traceroute tracepath mtr dig nslookup host ' +
  'wc sort uniq awk cut tr column jq xargs echo printf id whoami w who last lscpu lspci lsusb lsmod lshw dmidecode sensors stat file which type readlink realpath ' +
  'pvs vgs lvs pvdisplay vgdisplay lvdisplay multipath iostat vmstat mpstat pidstat sar nproc getent env printenv diff md5sum sha256sum ' +
  'pveversion pvereport arcstat ipmitool mtr showmount dpkg-query lsof lsattr getfacl arc_summary numactl nstat tcpdump watch test true ceph-conf corosync-quorumtool').split(/\s+/));
const RISK_RO_SUBS = new Set(('show status list ls dump get stat stats info detail df tree health query versions version pending showcmd log logs diff du top iostat perf ' +
  'nodes config available scan path fsid report services eval progress utilization metadata find ok-to-stop inventory show-label mon_status getmap getcrushmap ' +
  'autoscale-status get-quota dump_stuck ls-by-pool ls-by-osd ls-by-daemon listomapkeys listomapvals lspools features print-key listsnapshot ping network-get-interfaces ' +
  'localnet time-sync-status quorum_status dump_ops_in_flight dump_historic_ops get-health-metrics limit policy session tracking sources list-inconsistent-obj list-inconsistent-pg list_unfound').split(/\s+/));
const RISK_WRITE_SUBS = new Set(('set unset create rm remove delete del add purge destroy start stop restart reload reboot reset enable disable apply ' +
  'mv cp put import export flush replace modify update upgrade install move migrate resize rollback repair kill fail out in down up mark rename set-quota makestep').split(' '));

function autoRisk(cmd) {
  let s = String(cmd).split(/\s+#\s/)[0].trim();
  if (!s) return 'chg';
  // Che chuỗi trong nháy để chữ trong mẫu grep/tham số không bị tính là động từ.
  s = s.replace(/'[^']*'|"[^"]*"/g, ' Q ').replace(/<[^<>\s]*>/g, 'X');
  // Ghi file: chuyển hướng > (trừ về /dev/null hoặc 2>&1), tee, sed -i.
  const noNull = s.replace(/\d?>>?\s*\/dev\/null|\d?>&\d/g, ' ');
  if (/>/.test(noNull) || /(^|\|)\s*(sudo\s+)?tee\b/.test(s) || /\bsed\b[^|]*\s-i/.test(s)) return 'chg';
  const segs = s.split(/\|\||&&|[|;]/).map(x => x.trim()).filter(Boolean);
  return segs.length && segs.every(segRO) ? 'ro' : 'chg';
}

function segRO(seg) {
  let t = seg.split(/\s+/);
  while (t.length && (/^(sudo|time|nice|ionice)$/.test(t[0]) || /^[A-Z_]+=/.test(t[0]))) t.shift();
  if (t[0] === 'timeout') t = t.slice(2);
  if (t[0] === 'watch') { t.shift(); while (t[0] && t[0].startsWith('-')) { if (/^-[nd]$/.test(t[0])) t.shift(); t.shift(); } }
  const v = t[0], rest = t.slice(1), words = rest.filter(w => /^[a-z][a-z0-9_-]*$/.test(w));
  if (!v) return false;
  if (rest.some(w => /^--?(delete|exec|execdir|fix|force|yes|write)$/.test(w))) return false;
  switch (v) {
    case 'systemctl': return /^(status|is-active|is-enabled|is-failed|list-units|list-unit-files|list-timers|show|cat)$/.test(words[0] || '') || rest[0] === '--failed';
    case 'ip': return !words.some(w => /^(add|del|delete|set|flush|change|replace|append)$/.test(w));
    case 'smartctl': return !rest.some(w => /^(-t|--test|-s|--smart|-X|--abort)$/.test(w));
    case 'journalctl': return !rest.some(w => /^--(vacuum|rotate|flush|relinquish)/.test(w));
    case 'find': return true; // -delete/-exec đã loại ở trên
    case 'ethtool': return !rest.some(w => /^-[sKAGLCEW]$|^--(change|set|offload|pause)/.test(w));
    case 'zpool': case 'zfs': return /^(status|list|iostat|get|history|events|version)$/.test(words[0] || '');
    case 'nvme': return /^(list|smart-log|id-ctrl|id-ns|error-log|list-subsys)$/.test(words[0] || '');
    case 'pvecm': return /^(status|nodes)$/.test(words[0] || '');
    case 'corosync-cfgtool': return rest.length === 1 && /^-[sn]$/.test(rest[0]);
    case 'corosync-cmapctl': return !rest.some(w => /^-[sdDp]$/.test(w));
    case 'crushtool': return rest[0] === '-d' || rest.includes('--test');
    case 'ceph': if (/^-(s|w)$|^--status$/.test(rest[0] || '')) return true; break;
    case 'apt': return /^(policy|list|show|search)$/.test(words[0] || '');
    case 'dpkg': return /^-(l|L|s|S)$/.test(rest[0] || '');
    case 'nginx': return /^-(v|V|t|T)$/.test(rest[0] || '');
    case 'exportfs': return rest.length === 1 && rest[0] === '-v';
    case 'openssl': return rest.includes('-noout') && !rest.includes('-out');
    case 'iscsiadm': return /^session$/.test(rest[1] || '') && !rest.some(w => /^--(rescan|logout|login)/.test(w));
    case 'rados': if (words.includes('get')) return false; break; // rados get ghi object ra file
    case 'xargs': return segRO(rest.join(' '));
  }
  if (RISK_RO_VERBS.has(v)) return true;
  if (words.some(w => RISK_WRITE_SUBS.has(w))) return false;
  return words.some(w => RISK_RO_SUBS.has(w));
}

if (typeof module !== 'undefined') module.exports = { autoRisk };
