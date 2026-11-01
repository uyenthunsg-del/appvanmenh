<?php
declare(strict_types=1);

namespace TuVi\Controllers;

use TuVi\ApiClient;
use TuVi\Content;
use TuVi\Csrf;
use TuVi\Env;
use TuVi\EngineException;
use TuVi\ProfileRepository;
use TuVi\Validator;

/** Form nhập hồ sơ, lưu database và trang kết quả Thần số học. */
final class ProfileController
{
    private const Y_MODES = ['auto', 'vowel', 'consonant'];

    public function form(): void
    {
        view('form', [
            'title' => 'Xem lá số',
            'errors' => flash_get('errors', []),
            'old' => flash_get('old', []),
            'csrf' => Csrf::token(),
            'today' => date('Y-m-d'),
        ]);
    }

    public function store(): void
    {
        if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
            http_response_code(405);
            header('Allow: POST');
            view('error', ['title' => 'Không hợp lệ', 'message' => 'Trang này chỉ nhận dữ liệu gửi từ form.']);
            return;
        }
        if (!Csrf::verify($_POST['csrf'] ?? null)) {
            http_response_code(419);
            view('error', ['title' => 'Phiên hết hạn', 'message' => 'Phiên làm việc đã hết hạn. Vui lòng quay lại và gửi lại form.']);
            return;
        }

        [$errors, $clean] = Validator::profile($_POST);
        if ($errors !== []) {
            flash_set('errors', $errors);
            flash_set('old', array_map(static fn ($v) => (string) $v, $clean));
            redirect('index.php');
        }

        $id = (new ProfileRepository())->create($clean);
        redirect('result.php?id=' . $id); // chuyển hướng sau POST để F5 không gửi lại form
    }

    public function show(): void
    {
        $id = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT, ['options' => ['min_range' => 1]]);
        $profile = $id ? (new ProfileRepository())->find($id) : null;
        if ($profile === null) {
            http_response_code(404);
            view('error', ['title' => 'Không tìm thấy', 'message' => 'Không tìm thấy hồ sơ này.']);
            return;
        }

        $yMode = $_GET['y'] ?? 'auto';
        if (!is_string($yMode) || !in_array($yMode, self::Y_MODES, true)) {
            $yMode = 'auto';
        }

        $ziMode = $_GET['zi'] ?? 'next_day';
        if (!is_string($ziMode) || !in_array($ziMode, ['next_day', 'early_late'], true)) {
            $ziMode = 'next_day';
        }

        $tuMode = $_GET['tu'] ?? 'fire';
        if (!is_string($tuMode) || !in_array($tuMode, ['fire', 'water'], true)) {
            $tuMode = 'fire';
        }

        $houseSystem = $_GET['house'] ?? 'placidus';
        if (!is_string($houseSystem) || !in_array($houseSystem, ['placidus', 'whole_sign', 'equal'], true)) {
            $houseSystem = 'placidus';
        }

        $activeTab = $_GET['tab'] ?? 'natal';
        if (!is_string($activeTab) || !in_array($activeTab, ['natal', 'bazi', 'numerology', 'tuvi'], true)) {
            $activeTab = 'natal';
        }

        $client = ApiClient::fromEnv();

        $result = null;
        $apiError = null;
        try {
            $result = $client->numerology($profile['full_name'], $profile['birth_date'], $yMode, (int) date('Y'));
        } catch (EngineException $ex) {
            error_log('Numerology error: ' . $ex->getMessage());
            $apiError = Env::get('APP_DEBUG', '0') === '1'
                ? $ex->getMessage()
                : 'Không lấy được kết quả Thần số học từ engine tính toán. Hãy kiểm tra engine đã chạy chưa.';
        }

        $baziResult = null;
        $baziError = null;
        try {
            $baziResult = $client->bazi(
                $profile['full_name'],
                $profile['gender'],
                $profile['birth_date'],
                $profile['birth_time'],
                $profile['birth_place'],
                $ziMode,
                $tuMode
            );
        } catch (EngineException $ex) {
            error_log('Bazi error: ' . $ex->getMessage());
            $baziError = Env::get('APP_DEBUG', '0') === '1'
                ? $ex->getMessage()
                : 'Không lấy được kết quả Bát Tự từ engine tính toán. Hãy kiểm tra engine đã chạy chưa.';
        }

        $natalResult = null;
        $natalError = null;
        try {
            $natalResult = $client->natal(
                $profile['full_name'],
                $profile['gender'],
                $profile['birth_date'],
                $profile['birth_time'],
                $profile['birth_place'],
                $houseSystem
            );
        } catch (EngineException $ex) {
            error_log('Natal error: ' . $ex->getMessage());
            $natalError = Env::get('APP_DEBUG', '0') === '1'
                ? $ex->getMessage()
                : 'Không lấy được kết quả Bản Đồ Sao từ engine tính toán. Hãy kiểm tra engine đã chạy chưa.';
        }

        $tuviResult = null;
        $tuviError  = null;
        try {
            $tuviResult = $client->tuvi(
                $profile['full_name'],
                $profile['gender'],
                $profile['birth_date'],
                $profile['birth_time'],
                $profile['birth_place'],
                $ziMode
            );
        } catch (EngineException $ex) {
            error_log('Tuvi error: ' . $ex->getMessage());
            $tuviError = Env::get('APP_DEBUG', '0') === '1'
                ? $ex->getMessage()
                : 'Không lấy được kết quả Tử Vi từ engine tính toán. Hãy kiểm tra engine đã chạy chưa.';
        }

        view('result', [
            'title'       => 'Lá số: ' . $profile['full_name'],
            'profile'     => $profile,
            'result'      => $result,
            'apiError'    => $apiError,
            'texts'       => Content::numerology(),
            'yMode'       => $yMode,
            'baziResult'  => $baziResult,
            'baziError'   => $baziError,
            'baziTexts'   => Content::bazi(),
            'ziMode'      => $ziMode,
            'tuMode'      => $tuMode,
            'natalResult' => $natalResult,
            'natalError'  => $natalError,
            'natalTexts'  => Content::natal(),
            'houseSystem' => $houseSystem,
            'tuviResult'  => $tuviResult,
            'tuviError'   => $tuviError,
            'tuviTexts'   => Content::tuvi(),
            'activeTab'   => $activeTab,
        ]);
    }
}
