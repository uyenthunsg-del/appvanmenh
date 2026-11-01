<?php
declare(strict_types=1);

namespace TuVi;

/** Truy cập bảng profiles. */
final class ProfileRepository
{
    /** @param array<string, ?string> $data dữ liệu đã qua Validator */
    public function create(array $data): int
    {
        $pdo = Database::pdo();
        $stmt = $pdo->prepare(
            'INSERT INTO profiles (full_name, gender, birth_date, birth_time, birth_place)
             VALUES (:full_name, :gender, :birth_date, :birth_time, :birth_place)'
        );
        $stmt->execute([
            ':full_name' => $data['full_name'],
            ':gender' => $data['gender'],
            ':birth_date' => $data['birth_date'],
            ':birth_time' => $data['birth_time'],
            ':birth_place' => $data['birth_place'],
        ]);
        return (int) $pdo->lastInsertId();
    }

    /** @return array<string, mixed>|null */
    public function find(int $id): ?array
    {
        $stmt = Database::pdo()->prepare('SELECT * FROM profiles WHERE id = :id');
        $stmt->execute([':id' => $id]);
        $row = $stmt->fetch();
        return $row === false ? null : $row;
    }
}
