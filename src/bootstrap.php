<?php
declare(strict_types=1);

// Khởi động chung cho mọi trang trong public/. Gọi: require __DIR__ . '/../src/bootstrap.php';

define('ROOT_PATH', dirname(__DIR__));

// Tự nạp class: TuVi\Foo\Bar -> src/Foo/Bar.php
spl_autoload_register(static function (string $class): void {
    $prefix = 'TuVi\\';
    if (strncmp($class, $prefix, strlen($prefix)) !== 0) {
        return;
    }
    $file = ROOT_PATH . '/src/' . str_replace('\\', '/', substr($class, strlen($prefix))) . '.php';
    if (is_file($file)) {
        require $file;
    }
});

require_once ROOT_PATH . '/src/helpers.php';

\TuVi\Env::load(ROOT_PATH . '/.env');

mb_internal_encoding('UTF-8');
date_default_timezone_set('Asia/Ho_Chi_Minh');

// Lỗi không bắt được: ghi log, chỉ hiện chi tiết khi APP_DEBUG=1 (tránh lộ thông tin).
set_exception_handler(static function (Throwable $e): void {
    error_log((string) $e);
    http_response_code(500);
    $debug = \TuVi\Env::get('APP_DEBUG', '0') === '1';
    view('error', [
        'title' => 'Có lỗi xảy ra',
        'message' => $debug ? $e->getMessage() : 'Đã có lỗi xảy ra. Vui lòng thử lại sau.',
    ]);
});

session_set_cookie_params([
    'lifetime' => 0,
    'path' => '/',
    'httponly' => true,
    'samesite' => 'Lax',
]);
session_start();
