<?php
declare(strict_types=1);

namespace TuVi;

/** Kiểm tra và làm sạch dữ liệu form hồ sơ. Trả về [lỗi theo trường, dữ liệu sạch]. */
final class Validator
{
    /**
     * @param array<string, mixed> $in
     * @return array{0: array<string, string>, 1: array<string, ?string>}
     */
    public static function profile(array $in): array
    {
        $errors = [];

        // Họ tên: chỉ chữ cái (kể cả có dấu), dấu cách, dấu chấm, nháy đơn, gạch nối.
        $name = preg_replace('/\s+/u', ' ', trim(self::str($in, 'full_name'))) ?? '';
        $len = mb_strlen($name);
        if ($len < 2 || $len > 150) {
            $errors['full_name'] = 'Họ tên phải dài từ 2 đến 150 ký tự.';
        } elseif (!preg_match('/^[\p{L}\p{M}\s.\'\-]+$/u', $name) || !preg_match('/\p{L}/u', $name)) {
            $errors['full_name'] = 'Họ tên chỉ gồm chữ cái, dấu cách, dấu chấm, dấu nháy và gạch nối.';
        }

        $gender = self::str($in, 'gender');
        if (!in_array($gender, ['male', 'female'], true)) {
            $errors['gender'] = 'Vui lòng chọn giới tính.';
        }

        // Ngày sinh dương lịch: đúng định dạng, ngày có thật, từ năm 1900, không ở tương lai.
        $date = self::str($in, 'birth_date');
        $dt = \DateTimeImmutable::createFromFormat('!Y-m-d', $date);
        $parseErrors = \DateTimeImmutable::getLastErrors();
        $bad = $dt === false
            || ($parseErrors !== false && ($parseErrors['warning_count'] > 0 || $parseErrors['error_count'] > 0))
            || $dt->format('Y-m-d') !== $date;
        if ($bad) {
            $errors['birth_date'] = 'Ngày sinh không hợp lệ.';
        } elseif ((int) $dt->format('Y') < 1900 || $dt > new \DateTimeImmutable('today')) {
            $errors['birth_date'] = 'Ngày sinh phải từ năm 1900 và không ở tương lai.';
        }

        // Giờ sinh: không bắt buộc (để trống nếu không biết), định dạng HH:MM 24 giờ.
        $time = self::str($in, 'birth_time');
        if ($time !== '' && !preg_match('/^([01]\d|2[0-3]):[0-5]\d$/', $time)) {
            $errors['birth_time'] = 'Giờ sinh không hợp lệ (định dạng HH:MM).';
        }

        $place = preg_replace('/\s+/u', ' ', trim(self::str($in, 'birth_place'))) ?? '';
        $placeLen = mb_strlen($place);
        if ($placeLen < 2 || $placeLen > 150 || preg_match('/[\p{Cc}<>]/u', $place)) {
            $errors['birth_place'] = 'Nơi sinh phải dài từ 2 đến 150 ký tự và không chứa ký tự đặc biệt < >.';
        }

        return [$errors, [
            'full_name' => $name,
            'gender' => $gender,
            'birth_date' => $date,
            'birth_time' => $time === '' ? null : $time,
            'birth_place' => $place,
        ]];
    }

    /** @param array<string, mixed> $in */
    private static function str(array $in, string $key): string
    {
        $v = $in[$key] ?? '';
        return is_string($v) ? $v : ''; // bỏ qua mảng gửi lên dưới dạng field[]=...
    }
}
