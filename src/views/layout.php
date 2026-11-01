<!doctype html>
<html lang="vi" data-bs-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title><?= e($pageTitle) ?> · Tử vi</title>
  <script src="assets/js/theme.js"></script>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="assets/css/app.css" rel="stylesheet">
  <script src="assets/js/app.js" defer></script>
</head>
<body>
  <nav class="navbar site-nav mb-4">
    <div class="container">
      <a class="navbar-brand" href="index.php">Tử vi · Bát tự · Bản đồ sao · Thần số học</a>
      <button id="theme-toggle" type="button" class="btn btn-sm btn-outline-secondary" aria-pressed="false">
        <svg class="icon-moon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
        <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
        <span class="d-none d-sm-inline">Sáng / Tối</span>
      </button>
    </div>
  </nav>
  <main class="container pb-5">
    <?= $pageContent ?>
  </main>
  <footer class="container text-center small pb-4 page-footer">
    Nội dung chỉ mang tính chất tham khảo, không thay thế tư vấn chuyên môn về sức khỏe, tài chính hay pháp lý.
  </footer>
</body>
</html>
