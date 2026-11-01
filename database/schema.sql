-- Schema cho dự án tuvi. Viết theo phần chung của MariaDB và MySQL 8.
-- Database `tuvi` đã được tạo sẵn trong FlyEnv (utf8mb4), file này chỉ tạo bảng.
-- Có thể chạy lại nhiều lần: dùng CREATE TABLE IF NOT EXISTS.

SET NAMES utf8mb4;

-- Người dùng đăng nhập (dùng từ Giai đoạn 6; hiện chưa bắt buộc).
CREATE TABLE IF NOT EXISTS users (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  username      VARCHAR(64)  NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Hồ sơ một người cần xem. user_id cho phép NULL vì Giai đoạn 1 chưa có đăng nhập.
-- latitude/longitude/timezone để trống cho tới Giai đoạn 3 (đổi tên thành phố sang tọa độ).
CREATE TABLE IF NOT EXISTS profiles (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id     INT UNSIGNED NULL,
  full_name   VARCHAR(150) NOT NULL,
  gender      ENUM('male','female') NOT NULL,
  birth_date  DATE         NOT NULL,
  birth_time  TIME         NULL,          -- NULL = không biết giờ sinh
  birth_place VARCHAR(150) NOT NULL,
  latitude    DECIMAL(9,6) NULL,
  longitude   DECIMAL(9,6) NULL,
  timezone    VARCHAR(64)  NULL,
  created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_profiles_user (user_id),
  CONSTRAINT fk_profiles_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bài luận giải AI (dùng từ Giai đoạn 5). input_hash = SHA-256 của JSON lá số + chủ đề,
-- nếu cùng profile/môn/chủ đề/hash đã có thì dùng lại, không gọi AI lần hai.
CREATE TABLE IF NOT EXISTS readings (
  id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
  profile_id INT UNSIGNED NOT NULL,
  module     VARCHAR(20)  NOT NULL,       -- numerology | bazi | natal | tuvi
  topic      VARCHAR(40)  NOT NULL,       -- personality | career | love | health | finance ...
  input_hash CHAR(64)     NOT NULL,
  content    MEDIUMTEXT   NOT NULL,
  model      VARCHAR(80)  NULL,
  created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_readings_cache (profile_id, module, topic, input_hash),
  CONSTRAINT fk_readings_profile FOREIGN KEY (profile_id) REFERENCES profiles (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
