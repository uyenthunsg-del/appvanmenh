<?php
declare(strict_types=1);

namespace TuVi;

/** Lỗi khi gọi FastAPI engine (không kết nối được, hết thời gian chờ, engine trả lỗi). */
final class EngineException extends \RuntimeException
{
}
