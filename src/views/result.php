<?php
/** @var array<string,mixed> $profile */
/** @var array<string,mixed>|null $result */
/** @var string|null $apiError */
/** @var array<string,mixed> $texts */
/** @var string $yMode */
/** @var array<string,mixed>|null $baziResult */
/** @var string|null $baziError */
/** @var array<string,mixed> $baziTexts */
/** @var string $ziMode */
/** @var string $tuMode */
/** @var array<string,mixed>|null $natalResult */
/** @var string|null $natalError */
/** @var array<string,mixed> $natalTexts */
/** @var string $houseSystem */
/** @var array<string,mixed>|null $tuviResult */
/** @var string|null $tuviError */
/** @var array<string,mixed> $tuviTexts */
/** @var string $activeTab */
use TuVi\Chart;

$yLabels = ['auto' => 'Tự động', 'vowel' => 'Luôn nguyên âm', 'consonant' => 'Luôn phụ âm'];
$tiles = [
    'soul_urge'   => 'Linh hồn',
    'expression'  => 'Sứ mệnh',
    'attitude'    => 'Thái độ',
    'personality' => 'Nhân cách',
    'maturity'    => 'Trưởng thành',
    'birth_day'   => 'Ngày sinh',
];
$time = $profile['birth_time'] ? substr((string) $profile['birth_time'], 0, 5) : 'chưa nhập';
$gender = $profile['gender'] === 'male' ? 'Nam' : 'Nữ';
$d = date_create((string) $profile['birth_date']);
$birthText = $d ? $d->format('d/m/Y') : (string) $profile['birth_date'];

/** Helper lấy class CSS ngũ hành không dấu */
$elemClass = static function (string $elem): string {
    return match ($elem) {
        'Kim' => 'elem-Kim',
        'Mộc' => 'elem-Moc',
        'Thủy' => 'elem-Thuy',
        'Hỏa' => 'elem-Hoa',
        'Thổ' => 'elem-Tho',
        default => '',
    };
};

/** Helper lấy class CSS nguyên tố phương Tây */
$zodiacElemClass = static function (string $elem): string {
    return match ($elem) {
        'Fire', 'Lửa' => 'zodiac-Fire',
        'Earth', 'Đất' => 'zodiac-Earth',
        'Air', 'Khí' => 'zodiac-Air',
        'Water', 'Nước' => 'zodiac-Water',
        default => '',
    };
};

/** Dòng giải thích cách tính Thần số học */
$howto = static function (string $key, array $item): string {
    return match ($key) {
        'life_path'   => 'ngày ' . (int) $item['parts']['day'] . ' + tháng ' . (int) $item['parts']['month']
                         . ' + năm ' . (int) $item['parts']['year'] . ' = ' . (int) $item['total'],
        'attitude'    => 'ngày ' . (int) $item['parts']['day'] . ' + tháng ' . (int) $item['parts']['month']
                         . ' = ' . (int) $item['total'],
        'maturity'    => 'số chủ đạo ' . (int) $item['parts']['life_path'] . ' + số sứ mệnh ' . (int) $item['parts']['expression']
                         . ' = ' . (int) $item['total'],
        'birth_day'   => 'ngày sinh ' . (int) $item['day'] . ' (số gốc) → ' . (int) $item['value'] . ' (rút gọn)',
        default       => 'tổng chữ cái = ' . (int) $item['total'],
    };
};

// URL query base để giữ các tùy chọn khi chuyển tab hoặc đổi trường phái
$baseQuery = 'result.php?id=' . (int) $profile['id'];
$queryPreset = '&amp;zi=' . e($ziMode) . '&amp;tu=' . e($tuMode) . '&amp;house=' . e($houseSystem) . '&amp;y=' . e($yMode);
?>

<!-- Thông tin hồ sơ -->
<div class="card shadow-sm mb-4">
  <div class="card-body">
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2">
      <div>
        <h1 class="h4 mb-1"><?= e($profile['full_name']) ?></h1>
        <p class="text-secondary mb-0">
          <?= e($gender) ?> · sinh <?= e($birthText) ?> · giờ sinh: <?= e($time) ?> · nơi sinh: <?= e($profile['birth_place']) ?>
        </p>
      </div>
      <div>
        <a class="btn btn-sm btn-outline-primary" href="index.php">
          <i class="bi bi-person-plus"></i> Xem hồ sơ khác
        </a>
      </div>
    </div>
  </div>
</div>

<!-- Tabs chọn 4 Môn Huyền Học -->
<ul class="nav nav-pills module-tabs mb-4 justify-content-center justify-content-md-start" id="moduleTabs">
  <li class="nav-item">
    <a class="nav-link <?= $activeTab === 'natal' ? 'active' : '' ?>"
       href="<?= $baseQuery ?>&amp;tab=natal<?= $queryPreset ?>">
      Bản Đồ Sao (Natal Chart)
    </a>
  </li>
  <li class="nav-item">
    <a class="nav-link <?= $activeTab === 'bazi' ? 'active' : '' ?>"
       href="<?= $baseQuery ?>&amp;tab=bazi<?= $queryPreset ?>">
      Bát Tự (Tứ Trụ)
    </a>
  </li>
  <li class="nav-item">
    <a class="nav-link <?= $activeTab === 'numerology' ? 'active' : '' ?>"
       href="<?= $baseQuery ?>&amp;tab=numerology<?= $queryPreset ?>">
      Thần Số Học
    </a>
  </li>
  <li class="nav-item">
    <span class="nav-link disabled text-muted" title="Sẽ hoàn thiện ở Giai đoạn 4">
      Tử Vi Đẩu Số <small class="badge bg-secondary-subtle text-secondary ms-1">GĐ 4</small>
    </span>
  </li>
</ul>

<?php if ($activeTab === 'natal'): ?>
  <!-- ================= BẢN ĐỒ SAO (NATAL CHART) ================= -->
  <?php if ($natalError !== null): ?>
    <div class="alert alert-warning" role="alert">
      <strong>Chưa lấy được dữ liệu Bản Đồ Sao.</strong> <?= e($natalError) ?>
    </div>
  <?php elseif ($natalResult !== null):
      $loc = $natalResult['resolved_location'];
      $planets = $natalResult['planets'];
      $angles = $natalResult['angles'];
      $houses = $natalResult['houses'];
      $aspects = $natalResult['aspects'];
      $balance = $natalResult['balance'];
      $sun = $planets['SUN']['zodiac'];
      $moon = $planets['MOON']['zodiac'];
      $asc = $angles['ASC']['zodiac'];
  ?>
    <!-- Cảnh báo múi giờ lịch sử nếu có -->
    <?php if (!empty($natalResult['timezone_note'])): ?>
      <div class="alert alert-info d-flex align-items-center gap-2 mb-4" role="alert">
        <span class="fs-5">ℹ️</span>
        <div>
          <strong>Hiệu chỉnh múi giờ lịch sử:</strong> <?= e($natalResult['timezone_note']) ?>
        </div>
      </div>
    <?php endif; ?>

    <!-- Bộ Ba Cốt Lõi: The Big 3 (Mặt Trời, Mặt Trăng, Cung Mọc) -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <div class="d-flex flex-wrap justify-content-between align-items-center mb-3">
          <h2 class="h5 mb-0">Bộ Ba Năng Lượng Cốt Lõi (The Big 3)</h2>
          <span class="small text-secondary">
            Tọa độ địa lý: <strong><?= e($loc['name']) ?></strong> (<?= $loc['latitude'] ?>°B, <?= $loc['longitude'] ?>°Đ)
          </span>
        </div>
        <div class="row row-cols-1 row-cols-md-3 g-3">
          <!-- Sun -->
          <div class="col">
            <div class="p-3 rounded-3 h-100" style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25);">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="text-secondary small fw-bold text-uppercase">Mặt Trời (Bản ngã)</span>
                <span class="fs-4">☉</span>
              </div>
              <div class="fs-4 fw-bold mb-1 text-danger">
                <?= e($sun['sign_name']) ?> <span class="fs-6 fw-normal text-secondary">(<?= $sun['degrees'] ?>°<?= sprintf('%02d', $sun['minutes']) ?>')</span>
              </div>
              <p class="small text-secondary mb-0">Nhà <?= $planets['SUN']['house'] ?> · Cung <?= e($sun['sign_element_vn']) ?> (<?= e($sun['sign_modality_vn']) ?>)</p>
            </div>
          </div>
          <!-- Moon -->
          <div class="col">
            <div class="p-3 rounded-3 h-100" style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.25);">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="text-secondary small fw-bold text-uppercase">Mặt Trăng (Nội tâm)</span>
                <span class="fs-4">☽</span>
              </div>
              <div class="fs-4 fw-bold mb-1 text-primary">
                <?= e($moon['sign_name']) ?> <span class="fs-6 fw-normal text-secondary">(<?= $moon['degrees'] ?>°<?= sprintf('%02d', $moon['minutes']) ?>')</span>
              </div>
              <p class="small text-secondary mb-0">Nhà <?= $planets['MOON']['house'] ?> · Cung <?= e($moon['sign_element_vn']) ?> (<?= e($moon['sign_modality_vn']) ?>)</p>
            </div>
          </div>
          <!-- Ascendant -->
          <div class="col">
            <div class="p-3 rounded-3 h-100" style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.25);">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="text-secondary small fw-bold text-uppercase">Cung Mọc (Diện mạo)</span>
                <span class="fs-5 fw-bold text-purple">AC</span>
              </div>
              <div class="fs-4 fw-bold mb-1 text-purple" style="color: #8b5cf6;">
                <?= e($asc['sign_name']) ?> <span class="fs-6 fw-normal text-secondary">(<?= $asc['degrees'] ?>°<?= sprintf('%02d', $asc['minutes']) ?>')</span>
              </div>
              <p class="small text-secondary mb-0">Đỉnh Nhà 1 · Cung <?= e($asc['sign_element_vn']) ?> (<?= e($asc['sign_modality_vn']) ?>)</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bánh Xe Bản Đồ Sao & Bảng Hành Tinh (Layout 2 cột) -->
    <div class="row g-4 mb-4">
      <!-- Cột trái: Bánh xe SVG -->
      <div class="col-lg-6">
        <div class="card shadow-sm h-100">
          <div class="card-body d-flex flex-column align-items-center justify-content-center p-2 p-md-3">
            <h2 class="h5 mb-2 align-self-start">Bánh Xe Bản Đồ Sao (Natal Wheel)</h2>
            <div class="natal-svg-container w-100">
              <?= $natalResult['svg'] ?>
            </div>
            <p class="small text-secondary text-center mt-2 mb-0">
              Cung Mọc (AC) cố định tại góc 9 giờ bên trái. Các đường nối tâm thể hiện góc chiếu:
              <span class="text-primary fw-bold">Xanh</span> (Tam hợp, Lục hợp),
              <span class="text-danger fw-bold">Đỏ</span> (Vuông góc, Đối đỉnh).
            </p>
          </div>
        </div>
      </div>

      <!-- Cột phải: Bảng Tọa Độ Hành Tinh & Cân Bằng Nguyên Tố -->
      <div class="col-lg-6">
        <!-- Bảng Hành Tinh -->
        <div class="card shadow-sm mb-4">
          <div class="card-body p-0">
            <div class="p-3 border-bottom">
              <h2 class="h5 mb-0">Vị Trí Các Hành Tinh &amp; Thiên Thể</h2>
            </div>
            <div class="table-responsive">
              <table class="table table-hover planet-table mb-0">
                <thead>
                  <tr class="small text-secondary border-bottom">
                    <th>Hành tinh</th>
                    <th>Cung Hoàng Đạo</th>
                    <th class="text-center">Độ số</th>
                    <th class="text-center">Nhà</th>
                    <th class="text-center">Trạng thái</th>
                  </tr>
                </thead>
                <tbody>
                  <?php foreach ($planets as $p):
                      $z = $p['zodiac'];
                  ?>
                    <tr>
                      <td>
                        <span class="fs-5 me-1"><?= e($p['symbol']) ?></span>
                        <strong><?= e($p['name']) ?></strong>
                      </td>
                      <td>
                        <span class="badge <?= $zodiacElemClass($z['sign_element']) ?>">
                          <?= e($z['sign_symbol']) ?> <?= e($z['sign_name']) ?>
                        </span>
                      </td>
                      <td class="text-center small font-monospace">
                        <?= $z['degrees'] ?>°<?= sprintf('%02d', $z['minutes']) ?>'
                      </td>
                      <td class="text-center fw-bold">
                        Nhà <?= (int) $p['house'] ?>
                      </td>
                      <td class="text-center">
                        <?php if ($p['is_retrograde']): ?>
                          <span class="badge text-bg-danger" title="Nghịch hành (Retrograde)">Rx</span>
                        <?php else: ?>
                          <span class="text-secondary small">Thuận</span>
                        <?php endif; ?>
                      </td>
                    </tr>
                  <?php endforeach; ?>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Cân Bằng Nguyên Tố & Tính Chất -->
        <div class="card shadow-sm">
          <div class="card-body">
            <h3 class="h6 fw-bold mb-3">Phân Bổ 4 Nguyên Tố</h3>
            <div class="five-elem-bars mb-4">
              <?php foreach ($balance['elements'] as $eKey => $eVal): ?>
                <div class="elem-bar-row">
                  <div class="elem-bar-label <?= $zodiacElemClass($eKey) ?> px-2 py-1 rounded small">
                    <?= e($eVal['name']) ?>
                  </div>
                  <div class="elem-bar-track">
                    <div class="elem-bar-fill <?= $eKey === 'Earth' ? 'Moc' : ($eKey === 'Fire' ? 'Hoa' : ($eKey === 'Water' ? 'Thuy' : 'Kim')) ?>"
                         style="width: <?= min(100, max(5, $eVal['percentage'])) ?>%;"></div>
                  </div>
                  <div class="elem-bar-val">
                    <strong><?= $eVal['count'] ?></strong> hành tinh (<?= $eVal['percentage'] ?>%)
                  </div>
                </div>
              <?php endforeach; ?>
            </div>

            <h3 class="h6 fw-bold mb-3">Phân Bổ 3 Tính Chất</h3>
            <div class="row g-2 text-center small">
              <?php foreach ($balance['modalities'] as $mKey => $mVal): ?>
                <div class="col-4">
                  <div class="p-2 rounded bg-body-tertiary border">
                    <div class="fw-bold"><?= e($mVal['name']) ?></div>
                    <div class="fs-5 fw-bold text-primary"><?= $mVal['count'] ?></div>
                    <div class="text-secondary small"><?= $mVal['percentage'] ?>%</div>
                  </div>
                </div>
              <?php endforeach; ?>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bảng 12 Nhà Hoàng Đạo (House Cusps) -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <div class="d-flex flex-wrap justify-content-between align-items-center mb-3">
          <h2 class="h5 mb-0">12 Nhà Hoàng Đạo (Houses)</h2>
          <span class="badge bg-secondary-subtle text-secondary border">
            <?= e($natalResult['house_system_name']) ?>
          </span>
        </div>
        <div class="row row-cols-2 row-cols-md-3 row-cols-xl-6 g-2">
          <?php foreach ($houses as $h):
              $z = $h['zodiac'];
              $isAngleHouse = in_array($h['house'], [1, 4, 7, 10], true);
              $angleLabel = match ($h['house']) {
                  1 => ' (AC)',
                  4 => ' (IC)',
                  7 => ' (DC)',
                  10 => ' (MC)',
                  default => '',
              };
          ?>
            <div class="col">
              <div class="p-2 rounded border <?= $isAngleHouse ? 'border-primary' : '' ?>" style="background: var(--glass-bg);">
                <div class="d-flex justify-content-between align-items-center">
                  <span class="fw-bold small <?= $isAngleHouse ? 'text-primary' : '' ?>">
                    Nhà <?= $h['house'] ?><?= $angleLabel ?>
                  </span>
                  <span class="badge <?= $zodiacElemClass($z['sign_element']) ?>" style="font-size: .65rem;">
                    <?= e($z['sign_symbol']) ?>
                  </span>
                </div>
                <div class="small fw-bold mt-1"><?= e($z['sign_name']) ?></div>
                <div class="text-secondary small font-monospace"><?= $z['degrees'] ?>°<?= sprintf('%02d', $z['minutes']) ?>'</div>
              </div>
            </div>
          <?php endforeach; ?>
        </div>
      </div>
    </div>

    <!-- Bảng Danh Sách Góc Chiếu (Aspects) -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <h2 class="h5 mb-3">Danh Sách Góc Chiếu Giữa Các Hành Tinh</h2>
        <?php if (!empty($aspects)): ?>
          <div class="table-responsive" style="max-height: 380px; overflow-y: auto;">
            <table class="table table-sm table-hover mb-0">
              <thead class="sticky-top bg-body">
                <tr class="small text-secondary border-bottom">
                  <th>Cặp Hành Tinh</th>
                  <th>Góc Chiếu</th>
                  <th class="text-center">Góc thực tế</th>
                  <th class="text-center">Dung sai (Orb)</th>
                  <th class="text-center">Tính chất</th>
                </tr>
              </thead>
              <tbody>
                <?php foreach ($aspects as $asp):
                    $badgeClass = match ($asp['nature']) {
                        'harmonious' => 'aspect-badge-harmonious',
                        'challenging' => 'aspect-badge-challenging',
                        default => 'aspect-badge-neutral',
                    };
                    $natureLabel = match ($asp['nature']) {
                        'harmonious' => 'Thuận lợi',
                        'challenging' => 'Thử thách',
                        default => 'Trung hòa',
                    };
                ?>
                  <tr>
                    <td>
                      <span class="fw-bold me-1"><?= e($asp['point1_symbol']) ?> <?= e($asp['point1_name']) ?></span>
                      <span class="text-secondary">kết hợp</span>
                      <span class="fw-bold ms-1"><?= e($asp['point2_symbol']) ?> <?= e($asp['point2_name']) ?></span>
                    </td>
                    <td>
                      <span class="fw-bold" style="color: <?= e($asp['color']) ?>;">
                        <?= e($asp['aspect_symbol']) ?> <?= e($asp['aspect_name']) ?>
                      </span>
                      <span class="small text-secondary">(<?= (int) $asp['target_angle'] ?>°)</span>
                    </td>
                    <td class="text-center small font-monospace"><?= $asp['actual_angle'] ?>°</td>
                    <td class="text-center small font-monospace"><?= $asp['orb'] ?>°</td>
                    <td class="text-center">
                      <span class="<?= $badgeClass ?>"><?= $natureLabel ?></span>
                    </td>
                  </tr>
                <?php endforeach; ?>
              </tbody>
            </table>
          </div>
        <?php else: ?>
          <p class="small text-secondary mb-0">Không có góc chiếu lớn nào trong phạm vi dung sai cho phép.</p>
        <?php endif; ?>
      </div>
    </div>

    <!-- Tri Thức & Giải Nghĩa Chiêm Tinh -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <h2 class="h5 mb-3">Giải Nghĩa Năng Lượng Hành Tinh Trong Lá Số</h2>
        <?php foreach ($planets as $code => $p):
            $pInfo = $natalTexts['planets'][$code] ?? null;
            if (!$pInfo) continue;
            $z = $p['zodiac'];
        ?>
          <details class="meaning">
            <summary>
              <span class="fs-6 fw-bold me-2"><?= e($p['symbol']) ?> <?= e($p['name']) ?></span>
              <span class="badge <?= $zodiacElemClass($z['sign_element']) ?> me-2"><?= e($z['sign_name']) ?></span>
              <span class="small text-secondary">ở Nhà <?= (int) $p['house'] ?></span>
            </summary>
            <p class="small mt-2 mb-0"><?= e($pInfo['meaning']) ?></p>
          </details>
        <?php endforeach; ?>
      </div>
    </div>

    <!-- Nút Luận Giải AI (Giai đoạn 5) -->
    <div class="mb-4">
      <button type="button" class="btn btn-ai btn-lg w-100" disabled aria-describedby="ai-note-natal">
        Xem luận giải chi tiết Bản Đồ Sao bằng AI
      </button>
      <p id="ai-note-natal" class="small text-secondary text-center mt-2 mb-0">
        Tính năng luận giải Bản Đồ Sao bằng AI sẽ được mở ở Giai đoạn 5. AI sẽ phân tích dựa trên toàn bộ vị trí hành tinh, các góc chiếu và 12 nhà đã tính toán ở trên.
      </p>
    </div>

    <!-- Tùy Chọn Trường Phái Hệ Thống Nhà -->
    <div class="card shadow-sm mb-4">
      <div class="card-body small">
        <h3 class="h6 fw-bold mb-2">Lựa chọn hệ thống phân chia 12 Nhà (House System)</h3>
        <p class="text-secondary mb-3">
          Chiêm tinh học phương Tây có nhiều cách chia đỉnh nhà khác nhau. Bạn có thể chọn hệ thống phù hợp dưới đây để cập nhật lại bánh xe và đỉnh nhà:
        </p>
        <div class="d-flex flex-wrap gap-2">
          <a class="btn btn-sm <?= $houseSystem === 'placidus' ? 'btn-primary' : 'btn-outline-secondary' ?>"
             href="<?= $baseQuery ?>&amp;tab=natal&amp;house=placidus&amp;zi=<?= e($ziMode) ?>&amp;tu=<?= e($tuMode) ?>&amp;y=<?= e($yMode) ?>">
            ✓ Placidus (Chuẩn quốc tế - Khuyên dùng)
          </a>
          <a class="btn btn-sm <?= $houseSystem === 'whole_sign' ? 'btn-primary' : 'btn-outline-secondary' ?>"
             href="<?= $baseQuery ?>&amp;tab=natal&amp;house=whole_sign&amp;zi=<?= e($ziMode) ?>&amp;tu=<?= e($tuMode) ?>&amp;y=<?= e($yMode) ?>">
            Whole Sign (Cung nguyên vẹn - Cổ điển)
          </a>
          <a class="btn btn-sm <?= $houseSystem === 'equal' ? 'btn-primary' : 'btn-outline-secondary' ?>"
             href="<?= $baseQuery ?>&amp;tab=natal&amp;house=equal&amp;zi=<?= e($ziMode) ?>&amp;tu=<?= e($tuMode) ?>&amp;y=<?= e($yMode) ?>">
            Equal House (Nhà bằng nhau 30°)
          </a>
        </div>
      </div>
    </div>
  <?php endif; ?>

<?php elseif ($activeTab === 'bazi'): ?>
  <!-- ================= BÁT TỰ (TỨ TRỤ) ================= -->
  <?php if ($baziError !== null): ?>
    <div class="alert alert-warning" role="alert">
      <strong>Chưa lấy được dữ liệu Bát Tự.</strong> <?= e($baziError) ?>
    </div>
  <?php elseif ($baziResult !== null):
      $dm = $baziResult['day_master'];
      $dmStrength = $dm['strength'];
      $pillars = $baziResult['pillars'];
      $majorCycles = $baziResult['major_cycles'];
      $mcInfo = $baziResult['major_cycles_info'];
      $fiveElems = $baziResult['five_elements'];
  ?>
    <!-- Cảnh báo múi giờ lịch sử nếu có -->
    <?php if (!empty($baziResult['timezone_note'])): ?>
      <div class="alert alert-info d-flex align-items-center gap-2 mb-4" role="alert">
        <span class="fs-5">ℹ️</span>
        <div>
          <strong>Hiệu chỉnh múi giờ lịch sử Việt Nam:</strong> <?= e($baziResult['timezone_note']) ?>
        </div>
      </div>
    <?php endif; ?>

    <!-- Tổng quan Nhật Chủ (Bản Mệnh) -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <div class="row align-items-center g-3">
          <div class="col-md-auto text-center text-md-start">
            <div class="d-inline-flex flex-column align-items-center p-3 rounded-3" style="background: rgba(139, 92, 246, 0.12); border: 1px solid rgba(139, 92, 246, 0.3);">
              <span class="small text-secondary text-uppercase fw-bold">Nhật Chủ (Can Ngày)</span>
              <span class="fs-1 fw-bold my-1 elem-badge <?= $elemClass($dm['element']) ?>">
                <?= e($dm['stem']) ?> (<?= e($dm['element']) ?>)
              </span>
              <span class="badge text-bg-secondary"><?= e($dm['yin_yang']) ?> <?= e($dm['element']) ?></span>
            </div>
          </div>
          <div class="col-md">
            <div class="d-flex flex-wrap align-items-center gap-2 mb-2">
              <span class="badge fs-6 <?= $dmStrength['status'] === 'Thân Vượng' ? 'text-bg-success' : ($dmStrength['status'] === 'Thân Nhược' ? 'text-bg-warning' : 'text-bg-info') ?>">
                <?= e($dmStrength['status']) ?>
              </span>
              <span class="badge bg-secondary-subtle text-secondary border">
                <?= $dmStrength['dack_lenh'] ? 'Đắc lệnh tháng' : 'Không đắc lệnh' ?>
              </span>
              <span class="small text-secondary">
                (Đồng hành &amp; Ấn tinh tương trợ: <strong><?= $dmStrength['support_percentage'] ?>%</strong>)
              </span>
            </div>
            <p class="mb-0 text-secondary">
              <?= e($dmStrength['description']) ?>
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Bảng 4 Cột Trụ (Năm, Tháng, Ngày, Giờ) -->
    <h2 class="h5 mb-3">Lá số Bát Tự (Tứ Trụ)</h2>
    <div class="bazi-grid mb-4">
      <?php foreach ($pillars as $p):
          $isDay = ($p['key'] === 'day');
      ?>
        <div class="pillar-col <?= $isDay ? 'is-day' : '' ?>">
          <div class="pillar-header">
            <?= e($p['title']) ?> Trụ
            <?php if ($isDay): ?>
              <span class="badge text-bg-primary ms-1" style="font-size: .65rem;">Bản Mệnh</span>
            <?php endif; ?>
          </div>
          <div class="pillar-ten-god"><?= e($p['ten_god']) ?></div>
          <div class="pillar-can-chi">
            <div class="pillar-char">
              <span class="elem-badge <?= $elemClass($p['stem_element']) ?>"><?= e($p['stem']) ?></span>
              <span class="sub-info text-secondary">(<?= e($p['stem_yin_yang']) ?> <?= e($p['stem_element']) ?>)</span>
            </div>
            <div class="pillar-char">
              <span class="elem-badge <?= $elemClass($p['branch_element']) ?>"><?= e($p['branch']) ?></span>
              <span class="sub-info text-secondary">(<?= e($p['animal']) ?> - <?= e($p['branch_element']) ?>)</span>
            </div>
          </div>
          <div class="pillar-nayin text-secondary">Nạp âm: <strong><?= e($p['na_yin']) ?></strong></div>
          <div class="pillar-stage">Tràng Sinh: <strong><?= e($p['life_stage']) ?></strong></div>
          <div class="pillar-hidden-stems">
            <div class="small fw-bold text-secondary mb-1">Tàng Can (Ẩn khí):</div>
            <?php foreach ($p['hidden_stems'] as $h): ?>
              <div class="hidden-stem-row">
                <span>
                  <strong class="elem-badge <?= $elemClass($h['element']) ?>" style="padding: 1px 4px; font-size: .75rem;"><?= e($h['stem']) ?></strong>
                  <span class="text-secondary" style="font-size: .75rem;">(<?= e($h['type']) ?>)</span>
                </span>
                <span class="badge bg-secondary-subtle text-secondary" style="font-size: .7rem;"><?= e($h['ten_god']) ?></span>
              </div>
            <?php endforeach; ?>
          </div>
          <div class="pillar-stars">
            <?php if (!empty($p['symbolic_stars'])): ?>
              <?php foreach ($p['symbolic_stars'] as $star): ?>
                <span class="star-tag" title="<?= e($baziTexts['symbolic_stars'][$star] ?? $star) ?>"><?= e($star) ?></span>
              <?php endforeach; ?>
            <?php else: ?>
              <span class="small text-secondary fst-italic">Không có thần sát chính</span>
            <?php endif; ?>
          </div>
        </div>
      <?php endforeach; ?>
    </div>

    <!-- Bảng Đại Vận -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <div class="d-flex flex-wrap justify-content-between align-items-center mb-3">
          <h2 class="h5 mb-0">Các bước Đại Vận</h2>
          <div class="small text-secondary">
            Chiều vận: <strong class="text-primary"><?= e($mcInfo['direction']) ?></strong> hành
            · Khởi vận lúc: <strong><?= e($mcInfo['display']) ?></strong>
            (khoảng cách tới tiết <?= e($mcInfo['target_solar_term']) ?> là <?= $mcInfo['delta_days'] ?> ngày)
          </div>
        </div>
        <div class="daivan-scroll">
          <table class="daivan-table">
            <thead>
              <tr>
                <?php foreach ($majorCycles as $c): ?>
                  <th class="text-center small text-secondary">Bước <?= $c['step'] ?></th>
                <?php endforeach; ?>
              </tr>
            </thead>
            <tbody>
              <tr>
                <?php foreach ($majorCycles as $c): ?>
                  <td class="daivan-cell">
                    <div class="age text-primary"><?= e($c['age_range']) ?> tuổi</div>
                    <div class="small text-secondary">(từ năm <?= $c['calendar_year_start'] ?>)</div>
                    <div class="canchi">
                      <span class="elem-badge <?= $elemClass($c['element_stem']) ?>" style="padding: 2px 5px; font-size: .95rem;"><?= e($c['stem']) ?></span>
                      <span class="elem-badge <?= $elemClass($c['element_branch']) ?>" style="padding: 2px 5px; font-size: .95rem;"><?= e($c['branch']) ?></span>
                    </div>
                    <div class="god"><?= e($c['ten_god']) ?></div>
                    <div class="stage"><?= e($c['life_stage']) ?></div>
                    <div class="nayin text-secondary"><?= e($c['na_yin']) ?></div>
                  </td>
                <?php endforeach; ?>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Thống kê Cân Bằng Ngũ Hành -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <h2 class="h5 mb-3">Thống kê Năng lượng Ngũ Hành</h2>
        <div class="five-elem-bars">
          <?php foreach ($fiveElems as $eName => $eData):
              $pct = $eData['percentage'];
              $score = $eData['score'];
              $eClass = match ($eName) {
                  'Kim' => 'Kim', 'Mộc' => 'Moc', 'Thủy' => 'Thuy', 'Hỏa' => 'Hoa', 'Thổ' => 'Tho', default => '',
              };
          ?>
            <div class="elem-bar-row">
              <div class="elem-bar-label elem-badge <?= $elemClass($eName) ?>" style="font-size: .8rem;"><?= e($eName) ?></div>
              <div class="elem-bar-track">
                <div class="elem-bar-fill <?= $eClass ?>" style="width: <?= min(100, max(4, $pct)) ?>%;"></div>
              </div>
              <div class="elem-bar-val">
                <strong><?= $pct ?>%</strong>
                <span class="text-secondary small">(<?= $score ?> đ)</span>
              </div>
            </div>
          <?php endforeach; ?>
        </div>
      </div>
    </div>

    <!-- Ý nghĩa tri thức Bát Tự -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <h2 class="h5 mb-3">Giải nghĩa Thập Thần &amp; Thần Sát xuất hiện trong lá số</h2>
        <h3 class="h6 text-uppercase fw-bold text-secondary mb-2" style="letter-spacing: .05em;">Thập Thần đối với Bản Mệnh</h3>
        <?php
        $foundGods = [];
        foreach ($pillars as $p) {
            if ($p['ten_god'] !== 'Nhật Chủ' && !empty($p['ten_god'])) { $foundGods[$p['ten_god']] = true; }
            foreach ($p['hidden_stems'] as $h) {
                if ($h['ten_god'] !== 'Nhật Chủ' && !empty($h['ten_god'])) { $foundGods[$h['ten_god']] = true; }
            }
        }
        foreach (array_keys($foundGods) as $godName):
            $gInfo = $baziTexts['ten_gods'][$godName] ?? null;
            if (!$gInfo) continue;
        ?>
          <details class="meaning">
            <summary>
              <span class="text-primary fw-bold me-2"><?= e($godName) ?></span>
              <span class="small text-secondary">(<?= e($gInfo['keyword']) ?>)</span>
            </summary>
            <p class="small mt-2 mb-0"><?= e($gInfo['meaning']) ?></p>
          </details>
        <?php endforeach; ?>

        <h3 class="h6 text-uppercase fw-bold text-secondary mt-4 mb-2" style="letter-spacing: .05em;">Thần Sát hội tụ</h3>
        <?php
        $foundStars = [];
        foreach ($pillars as $p) {
            foreach ($p['symbolic_stars'] as $s) { $foundStars[$s] = true; }
        }
        if (!empty($foundStars)):
            foreach (array_keys($foundStars) as $starName):
                $sDesc = $baziTexts['symbolic_stars'][$starName] ?? '';
        ?>
              <details class="meaning">
                <summary><span class="star-tag me-2"><?= e($starName) ?></span></summary>
                <p class="small mt-2 mb-0"><?= e($sDesc) ?></p>
              </details>
        <?php endforeach;
        else: ?>
          <p class="small text-secondary mb-0">Không có thần sát đặc biệt trong 4 trụ.</p>
        <?php endif; ?>
      </div>
    </div>

    <!-- Nút luận giải bằng AI -->
    <div class="mb-4">
      <button type="button" class="btn btn-ai btn-lg w-100" disabled aria-describedby="ai-note-bazi">
        Xem luận giải chi tiết Bát Tự bằng AI
      </button>
      <p id="ai-note-bazi" class="small text-secondary text-center mt-2 mb-0">
        Tính năng luận giải Bát Tự bằng AI sẽ được mở ở Giai đoạn 5. AI sẽ phân tích dựa trên toàn bộ dữ liệu Can Chi, Thập Thần và Đại Vận đã tính toán ở trên.
      </p>
    </div>

    <!-- Tùy chọn Trường Phái Bát Tự -->
    <div class="card shadow-sm mb-4">
      <div class="card-body small">
        <h3 class="h6 fw-bold mb-2">Lựa chọn trường phái tính toán Bát Tự</h3>
        <p class="text-secondary mb-3">
          Trong Tử Bình học có một số quan điểm khác nhau về việc tính giờ Tý và vòng Tràng Sinh của hành Thổ. Bạn có thể chọn trường phái dưới đây để quan sát sự thay đổi trên lá số:
        </p>
        <div class="mb-3">
          <div class="fw-bold mb-1">1. Quy ước Giờ Tý (23:00 – 01:00):</div>
          <div class="d-flex flex-wrap gap-2">
            <a class="btn btn-sm <?= $ziMode === 'next_day' ? 'btn-primary' : 'btn-outline-secondary' ?>"
               href="<?= $baseQuery ?>&amp;tab=bazi&amp;zi=next_day&amp;tu=<?= e($tuMode) ?>&amp;house=<?= e($houseSystem) ?>&amp;y=<?= e($yMode) ?>">
              ✓ 23h tính sang ngày mới (Nhất nhật tị Tý - Khuyên dùng)
            </a>
            <a class="btn btn-sm <?= $ziMode === 'early_late' ? 'btn-primary' : 'btn-outline-secondary' ?>"
               href="<?= $baseQuery ?>&amp;tab=bazi&amp;zi=early_late&amp;tu=<?= e($tuMode) ?>&amp;house=<?= e($houseSystem) ?>&amp;y=<?= e($yMode) ?>">
              Phân Dạ Tý (23h-24h ngày cũ) &amp; Tý sớm (0h-1h ngày mới)
            </a>
          </div>
        </div>
        <div>
          <div class="fw-bold mb-1">2. Vòng Tràng Sinh của Can Thổ (Mậu, Kỷ):</div>
          <div class="d-flex flex-wrap gap-2">
            <a class="btn btn-sm <?= $tuMode === 'fire' ? 'btn-primary' : 'btn-outline-secondary' ?>"
               href="<?= $baseQuery ?>&amp;tab=bazi&amp;zi=<?= e($ziMode) ?>&amp;tu=fire&amp;house=<?= e($houseSystem) ?>&amp;y=<?= e($yMode) ?>">
              ✓ Hỏa Thổ đồng cung (Mậu sinh Dần, Kỷ sinh Dậu - Tử Bình chuẩn)
            </a>
            <a class="btn btn-sm <?= $tuMode === 'water' ? 'btn-primary' : 'btn-outline-secondary' ?>"
               href="<?= $baseQuery ?>&amp;tab=bazi&amp;zi=<?= e($ziMode) ?>&amp;tu=water&amp;house=<?= e($houseSystem) ?>&amp;y=<?= e($yMode) ?>">
              Thủy Thổ đồng cung (Mậu sinh Thân, Kỷ sinh Mão)
            </a>
          </div>
        </div>
      </div>
    </div>
  <?php endif; ?>

<?php else: ?>
  <!-- ================= THẦN SỐ HỌC ================= -->
  <?php if ($apiError !== null): ?>
    <div class="alert alert-warning" role="alert">
      <strong>Chưa có kết quả Thần số học.</strong> <?= e($apiError) ?>
    </div>
  <?php elseif ($result !== null):
      $life = $result['life_path'];
      $lifeMeta = $texts['indices']['life_path'] ?? ['title' => 'Số chủ đạo', 'about' => ''];
      $py = $result['personal_year'];
      $curYear = (int) $py['year'];
  ?>
    <!-- Số chủ đạo -->
    <section class="text-center mb-4" aria-labelledby="hero-title">
      <h2 id="hero-title" class="h5 hero-label mb-3">Số chủ đạo</h2>
      <div class="hero-ring"><span class="hero-number"><?= (int) $life['value'] ?></span></div>
      <p class="mt-3 mb-1 small text-secondary"><?= e($howto('life_path', $life)) ?></p>
      <?php if (!empty($life['master'])): ?><span class="badge text-bg-warning">Số bậc thầy</span><?php endif; ?>
    </section>

    <!-- 6 ô chỉ số -->
    <div class="row row-cols-2 row-cols-md-3 row-cols-xl-6 g-3 mb-4">
      <?php foreach ($tiles as $key => $label): $item = $result[$key]; ?>
        <div class="col">
          <div class="tile">
            <div class="tile-label"><?= e($label) ?></div>
            <div class="tile-value"><?= (int) $item['value'] ?></div>
            <?php if (!empty($item['master'])): ?><span class="badge text-bg-warning">Số bậc thầy</span><?php endif; ?>
          </div>
        </div>
      <?php endforeach; ?>
    </div>

    <!-- Chu kỳ vận số -->
    <section class="card shadow-sm mb-4" aria-labelledby="cycle-title">
      <div class="card-body">
        <h2 id="cycle-title" class="h5 mb-1">Chu kỳ vận số của bạn</h2>
        <p class="small text-secondary mb-3">
          Năm cá nhân <?= $curYear ?> của bạn là số <strong><?= (int) $py['current']['value'] ?></strong>.
          Mỗi năm số tăng thêm 1, hết 9 thì quay về 1; độ cao của điểm không tỉ lệ với giá trị số.
        </p>
        <div class="chart-scroll"><?= Chart::personalYear($py['cycle'], $curYear) ?></div>
        <p class="small text-secondary mt-3 mb-1">
          Độ cao của điểm theo quy luật trũng và đỉnh: số 4 và 7 ở đáy chu kỳ; số 1 và 2 ngay trên đáy;
          số 3 và 5 ở mức giữa; số 6 và 8 ở mức cận đỉnh; số 9 ở đỉnh.
        </p>
        <p class="small text-secondary mb-0">
          Cách tính: ngày sinh + tháng sinh + năm xem, mỗi thành phần rút về một chữ số rồi cộng lại.
          Nếu tổng ra 11 hoặc 22 thì ghi cả hai số, điểm vẽ theo số rút gọn.
        </p>
      </div>
    </section>

    <!-- Ý nghĩa từng chỉ số -->
    <section class="card shadow-sm mb-4" aria-labelledby="meaning-title">
      <div class="card-body">
        <h2 id="meaning-title" class="h5 mb-3">Ý nghĩa ngắn từng chỉ số</h2>
        <?php foreach (['life_path' => 'Số chủ đạo'] + $tiles as $key => $label):
            $item = $result[$key];
            $meta = $texts['indices'][$key] ?? ['title' => $label, 'about' => ''];
            $meaning = $texts['numbers'][(string) (int) $item['value']] ?? '';
        ?>
          <details class="meaning"<?= $key === 'life_path' ? ' open' : '' ?>>
            <summary><?= e($meta['title']) ?><span class="num"><?= (int) $item['value'] ?></span></summary>
            <p class="small text-secondary mt-2 mb-1"><?= e($howto($key, $item)) ?></p>
            <p class="small mb-1"><?= e($meta['about']) ?></p>
            <p class="mb-0"><?= e($meaning) ?></p>
          </details>
        <?php endforeach; ?>
      </div>
    </section>

    <!-- Luận giải AI -->
    <div class="mb-4">
      <button type="button" class="btn btn-ai btn-lg w-100" disabled aria-describedby="ai-note">Xem chi tiết luận giải</button>
      <p id="ai-note" class="small text-secondary text-center mt-2 mb-0">
        Luận giải chi tiết bằng AI đang được phát triển. Bài luận sẽ chỉ diễn giải dựa trên các con số đã tính ở trên.
      </p>
    </div>

    <!-- Phân tích họ tên -->
    <h2 class="h5 mb-3">Bảng chữ cái trong họ tên</h2>
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <p class="small text-secondary">
          Họ tên đã bỏ dấu: <strong><?= e($result['input']['normalized_name']) ?></strong>.
          Ô xanh là nguyên âm (tính vào số linh hồn), ô xám là phụ âm (tính vào số nhân cách); mọi ô đều tính vào số sứ mệnh.
        </p>
        <div class="d-flex flex-wrap gap-3">
          <?php foreach ($result['name_breakdown'] as $word): ?>
            <div class="word">
              <?php foreach ($word['letters'] as $l): ?>
                <span class="letter <?= $l['kind'] === 'vowel' ? 'letter-vowel' : 'letter-consonant' ?>">
                  <span class="ch"><?= e($l['letter']) ?></span><span class="val"><?= (int) $l['value'] ?></span>
                </span>
              <?php endforeach; ?>
            </div>
          <?php endforeach; ?>
        </div>
      </div>
    </div>

    <!-- Lựa chọn cách tính Thần số học -->
    <h2 class="h5 mb-3">Lựa chọn cách tính Thần số học</h2>
    <div class="card shadow-sm mb-4">
      <div class="card-body small">
        <ul class="mb-3">
          <li>Bảng quy đổi chữ cái: <strong>Pythagoras</strong> (A=1 … I=9, J=1 … R=9, S=1 … Z=8).</li>
          <li>Số chủ đạo: rút gọn riêng ngày, tháng, năm rồi cộng lại; giữ nguyên các số bậc thầy 11, 22, 33.</li>
          <li>Chữ Y: đang dùng chế độ <strong><?= e($yLabels[$yMode]) ?></strong>.</li>
        </ul>
        <span class="me-2">Thử cách coi chữ Y khác:</span>
        <?php foreach ($yLabels as $mode => $label): ?>
          <a class="btn btn-sm <?= $mode === $yMode ? 'btn-primary' : 'btn-outline-secondary' ?>"
             href="<?= $baseQuery ?>&amp;tab=numerology&amp;y=<?= e($mode) ?><?= $queryPreset ?>"><?= e($label) ?></a>
        <?php endforeach; ?>
      </div>
    </div>
  <?php endif; ?>
<?php endif; ?>

<p class="text-secondary small mt-4"><?= e($texts['disclaimer'] ?? 'Dữ liệu tính toán dựa trên các quy luật lịch pháp và tri thức cổ truyền phương Đông và phương Tây mang tính tham khảo.') ?></p>
