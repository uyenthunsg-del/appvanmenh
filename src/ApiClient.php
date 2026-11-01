<?php
declare(strict_types=1);

namespace TuVi;

/** Gọi FastAPI engine bằng curl. Mọi phép tính nằm ở Python, PHP chỉ gửi đầu vào và nhận JSON. */
final class ApiClient
{
    public function __construct(private string $baseUrl, private int $timeout = 10)
    {
    }

    public static function fromEnv(): self
    {
        return new self(
            rtrim(Env::get('ENGINE_URL', 'http://127.0.0.1:8000'), '/'),
            (int) Env::get('ENGINE_TIMEOUT', '10')
        );
    }

    /** @return array<string, mixed> */
    public function health(): array
    {
        return $this->request('GET', '/health');
    }

    /** @return array<string, mixed> */
    public function numerology(string $fullName, string $birthDate, string $yMode = 'auto', ?int $year = null): array
    {
        $payload = [
            'full_name' => $fullName,
            'birth_date' => $birthDate,
            'y_mode' => $yMode,
        ];
        if ($year !== null) {
            $payload['year'] = $year; // năm xem cho chu kỳ năm cá nhân
        }
        return $this->request('POST', '/numerology', $payload);
    }

    /** @return array<string, mixed> */
    public function bazi(
        string $fullName,
        string $gender,
        string $birthDate,
        ?string $birthTime = null,
        string $birthPlace = '',
        string $ziMode = 'next_day',
        string $tuMode = 'fire'
    ): array {
        $payload = [
            'full_name' => $fullName,
            'gender' => $gender,
            'birth_date' => $birthDate,
            'birth_time' => ($birthTime !== null && $birthTime !== '') ? substr($birthTime, 0, 5) : null,
            'birth_place' => $birthPlace,
            'zi_mode' => $ziMode,
            'tu_mode' => $tuMode,
        ];
        return $this->request('POST', '/bazi', $payload);
    }

    /** @return array<string, mixed> */
    public function natal(
        string $fullName,
        string $gender,
        string $birthDate,
        ?string $birthTime = null,
        string $birthPlace = '',
        string $houseSystem = 'placidus'
    ): array {
        $payload = [
            'full_name' => $fullName,
            'gender' => $gender,
            'birth_date' => $birthDate,
            'birth_time' => ($birthTime !== null && $birthTime !== '') ? substr($birthTime, 0, 5) : null,
            'birth_place' => $birthPlace,
            'house_system' => $houseSystem,
        ];
        return $this->request('POST', '/natal', $payload);
    }

    /** @return array<string, mixed> */
    public function tuvi(
        string $fullName,
        string $gender,
        string $birthDate,
        ?string $birthTime = null,
        string $birthPlace = '',
        string $ziMode = 'next_day'
    ): array {
        $payload = [
            'full_name'   => $fullName,
            'gender'      => $gender,
            'birth_date'  => $birthDate,
            'birth_time'  => ($birthTime !== null && $birthTime !== '') ? substr($birthTime, 0, 5) : null,
            'birth_place' => $birthPlace,
            'zi_mode'     => $ziMode,
        ];
        return $this->request('POST', '/tuvi', $payload);
    }

    /** @return array<string, mixed> */
    private function request(string $method, string $path, ?array $payload = null): array
    {
        $ch = curl_init($this->baseUrl . $path);
        $options = [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_CONNECTTIMEOUT => 3,
            CURLOPT_TIMEOUT => $this->timeout,
            CURLOPT_HTTPHEADER => ['Accept: application/json', 'Content-Type: application/json'],
        ];
        if ($method === 'POST') {
            $options[CURLOPT_POST] = true;
            $options[CURLOPT_POSTFIELDS] = json_encode($payload ?? [], JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
        }
        curl_setopt_array($ch, $options);

        $body = curl_exec($ch);
        if ($body === false) {
            throw new EngineException('Không kết nối được engine tính toán: ' . curl_error($ch));
        }
        $status = (int) curl_getinfo($ch, CURLINFO_RESPONSE_CODE);

        $data = json_decode((string) $body, true);
        if (!is_array($data)) {
            throw new EngineException("Engine trả dữ liệu không phải JSON (HTTP $status).");
        }
        if ($status >= 400) {
            $detail = $data['detail'] ?? 'lỗi không rõ';
            throw new EngineException("Engine báo lỗi (HTTP $status): " . (is_string($detail) ? $detail : json_encode($detail, JSON_UNESCAPED_UNICODE)));
        }
        return $data;
    }
}
