<?php
declare(strict_types=1);

/**
 * Trang kiểm tra môi trường: mở http://tuvi.test/check.php để biết PHP, .env, database,
 * engine Python và file giao diện đã ổn chưa. Chỉ chạy khi truy cập từ chính máy này.
 * Không in mật khẩu. XÓA file này trước khi đưa website lên mạng (Giai đoạn 6).
 */
$remote = $_SERVER['REMOTE_ADDR'] ?? '';
if (!in_array($remote, ['127.0.0.1', '::1'], true)) {
    http_response_code(404);
    exit('Not found');
}

error_reporting(E_ALL);
ini_set('display_errors', '0');

$root = dirname(__DIR__);
$rows = [];
/** Ghi một dòng kết quả: [tên kiểm tra, trạng thái ok|warn|fail, chi tiết/gợi ý]. */
$add = static function (string $name, string $status, string $detail) use (&$rows): void {
    $rows[] = [$name, $status, $detail];
};

// 1. PHP và extension
$add('Phiên bản PHP', version_compare(PHP_VERSION, '8.2.0', '>=') ? 'ok' : 'fail',
    PHP_VERSION . (version_compare(PHP_VERSION, '8.2.0', '>=') ? '' : ' (cần 8.2 trở lên: đổi PHP của site tuvi.test trong FlyEnv)'));
foreach (['curl', 'mbstring', 'pdo_mysql'] as $ext) {
    $add("Extension $ext", extension_loaded($ext) ? 'ok' : 'fail',
        extension_loaded($ext) ? 'đã bật' : 'chưa bật: vào FlyEnv, mục PHP, bật extension này rồi khởi động lại PHP');
}

// 2. Nạp mã nguồn và .env
$loaded = false;
try {
    require_once $root . '/src/bootstrap.php';
    $loaded = true;
} catch (Throwable $e) {
    $add('Nạp mã nguồn (src/bootstrap.php)', 'fail', get_class($e) . ': ' . $e->getMessage());
}

if ($loaded) {
    $envFile = $root . '/.env';
    if (!is_file($envFile)) {
        $add('File .env', 'fail', 'không thấy ' . $envFile . '. Sao chép .env.example thành .env rồi điền DB_PASS');
    } else {
        $add('File .env', 'ok', 'đã có');
        foreach (['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'ENGINE_URL'] as $k) {
            $v = \TuVi\Env::get($k);
            $add("  $k", $v ? 'ok' : 'warn', $v ?: 'trống, sẽ dùng giá trị mặc định');
        }
        $pass = \TuVi\Env::get('DB_PASS', '');
        $add('  DB_PASS', $pass !== '' ? 'ok' : 'warn',
            $pass !== '' ? 'đã điền (' . strlen($pass) . ' ký tự, không hiển thị)' : 'đang trống: điền mật khẩu user tuvi của MariaDB');
        $add('  APP_DEBUG', 'ok', \TuVi\Env::get('APP_DEBUG', '0') === '1'
            ? '1: trang lỗi sẽ hiện chi tiết nguyên nhân'
            : '0: trang lỗi chỉ hiện thông báo chung. Đổi thành 1 trong .env để thấy nguyên nhân khi đang chạy thử');
    }

    // 3. Database
    try {
        $pdo = \TuVi\Database::pdo();
        $ver = (string) $pdo->query('SELECT VERSION()')->fetchColumn();
        $add('Kết nối database', 'ok', 'thành công, phiên bản ' . $ver);
        $have = $pdo->query('SHOW TABLES')->fetchAll(PDO::FETCH_COLUMN);
        foreach (['users', 'profiles', 'readings'] as $t) {
            $add("  Bảng $t", in_array($t, $have, true) ? 'ok' : 'fail',
                in_array($t, $have, true) ? 'có' : 'chưa có: nhập database/schema.sql bằng phpMyAdmin');
        }
        if (in_array('profiles', $have, true)) {
            $cnt = (int) $pdo->query('SELECT COUNT(*) FROM profiles')->fetchColumn();
            $add('  Số hồ sơ đã lưu', 'ok', (string) $cnt);
        }
    } catch (Throwable $e) {
        $msg = $e->getMessage();
        $hint = match (true) {
            str_contains($msg, '2002'), str_contains($msg, 'refused') =>
                ' → MariaDB chưa chạy hoặc sai DB_HOST/DB_PORT. Bật MariaDB trong FlyEnv (nút play phải xanh) và xem lại cổng.',
            str_contains($msg, '1045') =>
                ' → sai user hoặc mật khẩu. Kiểm tra DB_USER và DB_PASS trong .env.',
            str_contains($msg, '1049') =>
                ' → database chưa tồn tại. Tạo database tên đúng như DB_NAME trong mục MariaDB của FlyEnv.',
            default => '',
        };
        $add('Kết nối database', 'fail', $msg . $hint);
    }

    // 4. Engine Python
    try {
        $api = \TuVi\ApiClient::fromEnv();
        $h = $api->health();
        $add('Engine Python (/health)', 'ok', 'trả lời: ' . json_encode($h, JSON_UNESCAPED_UNICODE));
        $r = $api->numerology('Nguyễn Văn A', '1990-01-01', 'auto', 2026);
        $missing = array_diff(['attitude', 'maturity', 'personal_year'], array_keys($r));
        $add('Engine đúng phiên bản mới', $missing === [] ? 'ok' : 'fail',
            $missing === [] ? 'có đủ các chỉ số mới' : 'thiếu ' . implode(', ', $missing) . ': tắt cửa sổ engine cũ rồi chạy lại uvicorn');
    } catch (Throwable $e) {
        $add('Engine Python', 'fail', $e->getMessage() . ' → chạy engine: vào E:\\tuvi\\engine, chạy uvicorn main:app --host 127.0.0.1 --port 8000');
    }

    // 5. Dữ liệu nội dung
    $c = \TuVi\Content::numerology();
    $add('data/numerology.json', count($c['indices'] ?? []) === 7 ? 'ok' : 'fail',
        count($c['indices'] ?? []) . ' chỉ số (cần 7)' . (count($c['indices'] ?? []) === 7 ? '' : ': file cũ hoặc hỏng, giải nén lại bản mới nhất'));
}

// 6. File giao diện
foreach ([
    'assets/css/app.css' => '--sky-base',
    'assets/js/theme.js' => 'data-bs-theme',
    'assets/js/app.js' => 'chart-scroll',
    'assets/img/stars.svg' => '<circle',
] as $rel => $needle) {
    $file = __DIR__ . '/' . $rel;
    if (!is_file($file)) {
        $add("Giao diện: $rel", 'fail', 'không thấy file. Giải nén lại bản mới nhất vào E:\\tuvi');
        continue;
    }
    $ok = str_contains((string) file_get_contents($file), $needle);
    $add("Giao diện: $rel", $ok ? 'ok' : 'fail',
        number_format((int) filesize($file)) . ' byte' . ($ok ? '' : ' nhưng là bản CŨ: giải nén đè lại bản mới nhất rồi bấm Ctrl+F5 trên trình duyệt'));
}

$fails = count(array_filter($rows, static fn ($r) => $r[1] === 'fail'));
$label = ['ok' => 'OK', 'warn' => 'Lưu ý', 'fail' => 'LỖI'];
$color = ['ok' => '#15803d', 'warn' => '#b45309', 'fail' => '#b91c1c'];
?>
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex">
  <title>Kiểm tra môi trường · Tử vi</title>
  <style>
    body { font: 15px/1.5 system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; color: #111; background: #fff; }
    table { border-collapse: collapse; width: 100%; }
    td { border-bottom: 1px solid #ddd; padding: .4rem .5rem; vertical-align: top; }
    td:nth-child(2) { white-space: nowrap; font-weight: 700; }
    .sum { padding: .8rem 1rem; border-radius: 6px; margin: 1rem 0; font-weight: 600; }
  </style>
</head>
<body>
  <h1>Kiểm tra môi trường</h1>
  <div class="sum" style="background:<?= $fails ? '#fee2e2' : '#dcfce7' ?>">
    <?= $fails ? "Có $fails mục LỖI, xem các dòng đỏ bên dưới." : 'Mọi thứ đều ổn.' ?>
  </div>
  <table>
    <?php foreach ($rows as [$name, $status, $detail]): ?>
      <tr>
        <td><?= htmlspecialchars($name, ENT_QUOTES, 'UTF-8') ?></td>
        <td style="color:<?= $color[$status] ?>"><?= $label[$status] ?></td>
        <td><?= htmlspecialchars($detail, ENT_QUOTES, 'UTF-8') ?></td>
      </tr>
    <?php endforeach; ?>
  </table>
  <p style="color:#555;margin-top:1.5rem">Trang này chỉ mở được từ chính máy bạn. Xóa file <code>public/check.php</code> trước khi đưa website lên mạng.</p>
</body>
</html>
