(function () {
  'use strict';

  // ---- 1. Bảng map ký tự -> {code, keyCode, shiftKey} theo layout US QWERTY ----
  const MAP = {};
  for (let i = 0; i < 26; i++) {
    const upper = String.fromCharCode(65 + i);
    const lower = String.fromCharCode(97 + i);
    const keyCode = 65 + i;
    const code = 'Key' + upper;
    MAP[lower] = { code, keyCode, shiftKey: false, key: lower };
    MAP[upper] = { code, keyCode, shiftKey: true, key: upper };
  }
  const DIGIT_ROW = [
    ['0', ')'], ['1', '!'], ['2', '@'], ['3', '#'], ['4', '$'],
    ['5', '%'], ['6', '^'], ['7', '&'], ['8', '*'], ['9', '('],
  ];
  DIGIT_ROW.forEach(([plain, shifted], i) => {
    const code = 'Digit' + plain;
    const keyCode = 48 + i;
    MAP[plain] = { code, keyCode, shiftKey: false, key: plain };
    MAP[shifted] = { code, keyCode, shiftKey: true, key: shifted };
  });
  const PUNCT = [
    ['-', '_', 'Minus', 189], ['=', '+', 'Equal', 187],
    ['[', '{', 'BracketLeft', 219], [']', '}', 'BracketRight', 221],
    ['\\', '|', 'Backslash', 220], [';', ':', 'Semicolon', 186],
    ["'", '"', 'Quote', 222], ['`', '~', 'Backquote', 192],
    [',', '<', 'Comma', 188], ['.', '>', 'Period', 190],
    ['/', '?', 'Slash', 191],
  ];
  PUNCT.forEach(([plain, shifted, code, keyCode]) => {
    MAP[plain] = { code, keyCode, shiftKey: false, key: plain };
    MAP[shifted] = { code, keyCode, shiftKey: true, key: shifted };
  });
  MAP[' '] = { code: 'Space', keyCode: 32, shiftKey: false, key: ' ' };

  // ---- 2. Tìm canvas mà noVNC đang render màn hình VM ----
  function findTarget() {
    const canvas = document.querySelector('canvas');
    return canvas || document.body;
  }

  // ---- 3. Bắn 1 sự kiện bàn phím tổng hợp ----
  function fireKey(target, type, info) {
    const ev = new KeyboardEvent(type, {
      key: info.key,
      code: info.code,
      keyCode: info.keyCode,
      which: info.keyCode,
      shiftKey: info.shiftKey,
      bubbles: true,
      cancelable: true,
      composed: true,
    });
    // Một số browser coi keyCode/which là getter tính sẵn -> ép lại cho chắc
    try {
      Object.defineProperty(ev, 'keyCode', { get: () => info.keyCode });
      Object.defineProperty(ev, 'which', { get: () => info.keyCode });
    } catch (e) { /* ignore nếu browser không cho override */ }
    target.dispatchEvent(ev);
  }

  function sendChar(target, ch) {
    if (ch === '\n' || ch === '\r') {
      const info = { code: 'Enter', keyCode: 13, shiftKey: false, key: 'Enter' };
      fireKey(target, 'keydown', info);
      fireKey(target, 'keyup', info);
      return;
    }
    const info = MAP[ch];
    if (!info) return; // ký tự không nằm trong bảng US QWERTY -> bỏ qua
    if (info.shiftKey) fireKey(target, 'keydown', { code: 'ShiftLeft', keyCode: 16, shiftKey: true, key: 'Shift' });
    fireKey(target, 'keydown', info);
    fireKey(target, 'keyup', info);
    if (info.shiftKey) fireKey(target, 'keyup', { code: 'ShiftLeft', keyCode: 16, shiftKey: false, key: 'Shift' });
  }

  async function sendText(text) {
    const target = findTarget();
    if (target.focus) target.focus();
    // click giả để noVNC nhận biết canvas đang được tương tác (một số bản cần focus thật)
    target.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
    target.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
    for (const ch of text) {
      sendChar(target, ch);
      await new Promise((r) => setTimeout(r, 8)); // giãn nhẹ giữa các phím tránh mất ký tự
    }
  }

  // ---- 4. UI: nút Paste + hộp thoại nhập text ----
  function buildDialog() {
    const overlay = document.createElement('div');
    overlay.id = 'custom-paste-overlay';
    Object.assign(overlay.style, {
      position: 'fixed', inset: '0', background: 'rgba(0,0,0,.5)',
      zIndex: 999999, display: 'none', alignItems: 'center', justifyContent: 'center',
    });
    const box = document.createElement('div');
    Object.assign(box.style, {
      background: '#fff', padding: '16px', borderRadius: '6px',
      width: '420px', maxWidth: '90vw', boxShadow: '0 4px 20px rgba(0,0,0,.3)',
      fontFamily: 'sans-serif',
    });
    box.innerHTML = `
      <div style="font-weight:600;margin-bottom:8px;">Gửi text tới VM (dạng gõ phím)</div>
      <textarea id="custom-paste-textarea" rows="6" style="width:100%;box-sizing:border-box;
        font-family:monospace;padding:6px;" placeholder="Dán nội dung vào đây..."></textarea>
      <div style="margin-top:10px;text-align:right;">
        <button id="custom-paste-cancel" style="margin-right:8px;">Hủy</button>
        <button id="custom-paste-send" style="background:#2b6cb0;color:#fff;border:0;
          padding:6px 14px;border-radius:4px;cursor:pointer;">Gửi</button>
      </div>
      <div style="font-size:11px;color:#888;margin-top:6px;">
        Lưu ý: chỉ hỗ trợ ký tự ASCII theo bàn phím US (chữ, số, dấu câu thông dụng).
      </div>`;
    overlay.appendChild(box);
    document.body.appendChild(overlay);

    overlay.querySelector('#custom-paste-cancel').onclick = () => {
      overlay.style.display = 'none';
    };
    overlay.querySelector('#custom-paste-send').onclick = async () => {
      const text = overlay.querySelector('#custom-paste-textarea').value;
      overlay.style.display = 'none';
      if (text) await sendText(text);
    };
    return overlay;
  }

  function addButton() {
    if (document.getElementById('custom-paste-btn')) return;
    const btn = document.createElement('button');
    btn.id = 'custom-paste-btn';
    btn.textContent = 'Paste';
    btn.title = 'Gửi text tới VM dưới dạng gõ phím';
    Object.assign(btn.style, {
      position: 'fixed', top: '8px', right: '90px', zIndex: 999998,
      padding: '4px 10px', fontSize: '13px', cursor: 'pointer',
      background: '#2b6cb0', color: '#fff', border: 0, borderRadius: '4px',
    });
    const overlay = buildDialog();
    btn.onclick = () => {
      overlay.style.display = 'flex';
      overlay.querySelector('#custom-paste-textarea').focus();
    };
    document.body.appendChild(btn);
  }

  function init() {
    addButton();
    let tries = 0;
    const t = setInterval(() => {
      addButton();
      if (++tries > 10) clearInterval(t);
    }, 1000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
