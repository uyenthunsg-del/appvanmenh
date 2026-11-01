// Chế độ sáng/tối: nhớ lựa chọn trong localStorage, mặc định theo hệ điều hành.
// File này nạp ở <head> (không defer) để đặt theme trước khi vẽ trang, tránh nháy trắng.
(function () {
  var root = document.documentElement;
  function stored() { try { return localStorage.getItem('theme'); } catch (e) { return null; } }
  function save(v) { try { localStorage.setItem('theme', v); } catch (e) { /* bỏ qua nếu bị chặn */ } }
  var initial = stored() || (window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  root.setAttribute('data-bs-theme', initial === 'dark' ? 'dark' : 'light');

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('theme-toggle');
    if (!btn) return;
    function sync() {
      var dark = root.getAttribute('data-bs-theme') === 'dark';
      btn.setAttribute('aria-pressed', dark ? 'true' : 'false');
      btn.setAttribute('aria-label', dark ? 'Chuyển sang chế độ sáng' : 'Chuyển sang chế độ tối');
      btn.title = btn.getAttribute('aria-label');
    }
    btn.addEventListener('click', function () {
      var next = root.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-bs-theme', next);
      save(next);
      sync();
    });
    sync();
  });
})();
