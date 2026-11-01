<?php
declare(strict_types=1);

namespace TuVi;

/** Token chống CSRF: một token ngẫu nhiên cho mỗi phiên, kiểm tra bằng hash_equals. */
final class Csrf
{
    public static function token(): string
    {
        if (empty($_SESSION['csrf'])) {
            $_SESSION['csrf'] = bin2hex(random_bytes(32));
        }
        return $_SESSION['csrf'];
    }

    public static function verify(mixed $token): bool
    {
        return is_string($token)
            && isset($_SESSION['csrf'])
            && hash_equals($_SESSION['csrf'], $token);
    }
}
