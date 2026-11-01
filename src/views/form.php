<?php
/** @var array<string,string> $errors */
/** @var array<string,string> $old */
/** @var string $csrf */
/** @var string $today */
$val = static fn (string $k): string => e($old[$k] ?? '');
$invalid = static fn (string $k): string => isset($errors[$k]) ? ' is-invalid' : '';
?>
<div class="row justify-content-center">
  <div class="col-lg-7">
    <div class="card shadow-sm">
      <div class="card-body p-4">
        <h1 class="h4 mb-3">Nhập thông tin để xem lá số</h1>
        <form method="post" action="submit.php" novalidate>
          <input type="hidden" name="csrf" value="<?= e($csrf) ?>">

          <div class="mb-3">
            <label for="full_name" class="form-label">Họ tên đầy đủ</label>
            <input type="text" class="form-control<?= $invalid('full_name') ?>" id="full_name" name="full_name"
                   maxlength="150" required value="<?= $val('full_name') ?>" placeholder="Ví dụ: Nguyễn Văn An">
            <?php if (isset($errors['full_name'])): ?><div class="invalid-feedback"><?= e($errors['full_name']) ?></div><?php endif; ?>
            <div class="form-text">Nhập đúng thứ tự họ, tên đệm, tên như trên giấy khai sinh. Hệ thống tự bỏ dấu khi tính.</div>
          </div>

          <div class="mb-3">
            <span class="form-label d-block">Giới tính</span>
            <?php foreach (['male' => 'Nam', 'female' => 'Nữ'] as $v => $label): ?>
              <div class="form-check form-check-inline">
                <input class="form-check-input<?= $invalid('gender') ?>" type="radio" name="gender" id="gender_<?= $v ?>"
                       value="<?= $v ?>" <?= ($old['gender'] ?? '') === $v ? 'checked' : '' ?>>
                <label class="form-check-label" for="gender_<?= $v ?>"><?= $label ?></label>
              </div>
            <?php endforeach; ?>
            <?php if (isset($errors['gender'])): ?><div class="text-danger small mt-1"><?= e($errors['gender']) ?></div><?php endif; ?>
          </div>

          <div class="row g-3 mb-3">
            <div class="col-sm-6">
              <label for="birth_date" class="form-label">Ngày sinh (dương lịch)</label>
              <input type="date" class="form-control<?= $invalid('birth_date') ?>" id="birth_date" name="birth_date"
                     min="1900-01-01" max="<?= e($today) ?>" required value="<?= $val('birth_date') ?>">
              <?php if (isset($errors['birth_date'])): ?><div class="invalid-feedback"><?= e($errors['birth_date']) ?></div><?php endif; ?>
            </div>
            <div class="col-sm-6">
              <label for="birth_time" class="form-label">Giờ sinh <span class="text-secondary">(nếu biết)</span></label>
              <input type="time" class="form-control<?= $invalid('birth_time') ?>" id="birth_time" name="birth_time"
                     value="<?= $val('birth_time') ?>">
              <?php if (isset($errors['birth_time'])): ?><div class="invalid-feedback"><?= e($errors['birth_time']) ?></div><?php endif; ?>
              <div class="form-text">Thần số học không cần giờ sinh; các môn sau này thì cần.</div>
            </div>
          </div>

          <div class="mb-4">
            <label for="birth_place" class="form-label">Nơi sinh</label>
            <input type="text" class="form-control<?= $invalid('birth_place') ?>" id="birth_place" name="birth_place"
                   maxlength="150" required value="<?= $val('birth_place') ?>" placeholder="Ví dụ: Hà Nội">
            <?php if (isset($errors['birth_place'])): ?><div class="invalid-feedback"><?= e($errors['birth_place']) ?></div><?php endif; ?>
            <div class="form-text">Tên thành phố hoặc tỉnh. Giai đoạn 3 sẽ tự đổi sang kinh độ, vĩ độ và múi giờ.</div>
          </div>

          <button type="submit" class="btn btn-primary btn-lg w-100">Xem kết quả</button>
        </form>
      </div>
    </div>
  </div>
</div>
