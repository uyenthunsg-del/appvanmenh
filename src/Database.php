<?php
declare(strict_types=1);

namespace TuVi;

use PDO;

/** Kết nối PDO dùng chung tới MariaDB/MySQL. Mọi truy vấn dùng prepared statement. */
final class Database
{
    private static ?PDO $pdo = null;

    public static function pdo(): PDO
    {
        if (self::$pdo === null) {
            $dsn = sprintf(
                'mysql:host=%s;port=%s;dbname=%s;charset=utf8mb4',
                Env::get('DB_HOST', '127.0.0.1'),
                Env::get('DB_PORT', '3306'),
                Env::get('DB_NAME', 'tuvi')
            );
            self::$pdo = new PDO($dsn, Env::get('DB_USER', 'tuvi'), Env::get('DB_PASS', ''), [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false, // dùng prepared statement thật, chống SQL injection
            ]);
        }
        return self::$pdo;
    }
}
