<?php
declare(strict_types=1);

/** Escape dữ liệu trước khi in ra HTML (chống XSS). Luôn dùng hàm này cho dữ liệu động. */
function e(?string $value): string
{
    return htmlspecialchars((string) $value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/** Hiển thị một view trong src/views/ bên trong layout chung. */
function view(string $name, array $vars = []): void
{
    extract($vars, EXTR_SKIP);
    ob_start();
    require ROOT_PATH . '/src/views/' . $name . '.php';
    $pageContent = ob_get_clean();
    $pageTitle = $title ?? 'Tử vi';
    require ROOT_PATH . '/src/views/layout.php';
}

function redirect(string $path): never
{
    header('Location: ' . $path);
    exit;
}

/** Dữ liệu chỉ tồn tại tới lần đọc kế tiếp (thông báo lỗi, giá trị form cũ). */
function flash_set(string $key, mixed $value): void
{
    $_SESSION['_flash'][$key] = $value;
}

function flash_get(string $key, mixed $default = null): mixed
{
    $value = $_SESSION['_flash'][$key] ?? $default;
    unset($_SESSION['_flash'][$key]);
    return $value;
}
