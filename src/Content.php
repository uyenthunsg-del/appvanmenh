<?php
declare(strict_types=1);

namespace TuVi;

/** Đọc nội dung tri thức ngắn trong data/*.json (ý nghĩa các con số, mô tả chỉ số). */
final class Content
{
    /** @return array<string, mixed> */
    public static function numerology(): array
    {
        $path = ROOT_PATH . '/data/numerology.json';
        $json = is_file($path) ? file_get_contents($path) : false;
        $data = $json === false ? null : json_decode($json, true);
        return is_array($data) ? $data : ['indices' => [], 'numbers' => [], 'disclaimer' => ''];
    }

    /** @return array<string, mixed> */
    public static function bazi(): array
    {
        $path = ROOT_PATH . '/data/bazi.json';
        $json = is_file($path) ? file_get_contents($path) : false;
        $data = $json === false ? null : json_decode($json, true);
        return is_array($data) ? $data : ['pillars' => [], 'ten_gods' => [], 'life_stages' => [], 'symbolic_stars' => []];
    }

    /** @return array<string, mixed> */
    public static function natal(): array
    {
        $path = ROOT_PATH . '/data/natal.json';
        $json = is_file($path) ? file_get_contents($path) : false;
        $data = $json === false ? null : json_decode($json, true);
        return is_array($data) ? $data : ['zodiac_signs' => [], 'planets' => [], 'houses' => [], 'aspects' => []];
    }

    /** @return array<string, mixed> */
    public static function tuvi(): array
    {
        $path = ROOT_PATH . '/data/tuvi.json';
        $json = is_file($path) ? file_get_contents($path) : false;
        $data = $json === false ? null : json_decode($json, true);
        return is_array($data) ? $data : ['brightness' => [], 'cuc' => [], 'palace_roles' => [], 'star_descriptions' => []];
    }
}
