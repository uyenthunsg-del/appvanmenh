<?php
declare(strict_types=1);

namespace TuVi;

/**
 * Vẽ biểu đồ "Chu kỳ vận số" (năm cá nhân) bằng SVG, render ở phía server.
 * Màu lấy từ CSS (class chart-*) nên tự đổi theo chế độ sáng/tối.
 */
final class Chart
{
    /**
     * Độ cao (mức 0 = đáy, 4 = đỉnh) của từng số 1-9 trên biểu đồ, theo quy luật trũng/đỉnh:
     *   đáy: 4, 7 | ngay trên đáy: 1, 2 | giữa: 3, 5 | cận đỉnh: 6, 8 | đỉnh: 9.
     * Độ cao KHÔNG tỉ lệ với giá trị số, nên đường nối các năm uốn lượn thành sóng.
     */
    private const LEVELS = [4 => 0, 7 => 0, 1 => 1, 2 => 1, 3 => 2, 5 => 2, 6 => 3, 8 => 3, 9 => 4];
    private const MAX_LEVEL = 4;

    /** Mức độ cao (0-4) của một số 1-9. */
    public static function level(int $single): int
    {
        return self::LEVELS[$single] ?? 0;
    }

    /**
     * @param list<array{year:int,value:int,single:int,master:bool}> $cycle
     */
    public static function personalYear(array $cycle, int $currentYear): string
    {
        $n = count($cycle);
        if ($n === 0) {
            return '';
        }

        $w = 720; 
        $h = 290; // Tăng nhẹ chiều cao một chút để chứa nhãn năm xoay 45 độ thoải mái hơn
        $left = 48; 
        $right = 48; 
        $top = 38; 
        $bottom = 80; // Tăng không gian lề dưới cho text xoay 45 độ

        $plotW = $w - $left - $right;
        $plotH = $h - $top - $bottom;
        $baseY = $top + $plotH;   // mức thấp nhất của đường (số 4 và 7)
        $axisY = $baseY + 12;     // trục năm nằm thấp hơn một chút

        $pts = [];
        foreach ($cycle as $i => $c) {
            $x = $n === 1 ? $left + $plotW / 2 : $left + $plotW * $i / ($n - 1);
            $y = $top + $plotH * (self::MAX_LEVEL - self::level((int) $c['single'])) / self::MAX_LEVEL;
            $pts[] = [$x, $y];
        }

        // Đường cong mượt (Catmull-Rom -> Bezier), kẹp control point trong khung
        $f = static fn (float $v): string => number_format($v, 1, '.', '');
        $clamp = static fn (float $y): float => max((float) $top, min((float) $baseY, $y));
        
        $d = 'M' . $f($pts[0][0]) . ' ' . $f($pts[0][1]);
        for ($i = 0; $i < $n - 1; $i++) {
            $p0 = $pts[max($i - 1, 0)];
            $p1 = $pts[$i];
            $p2 = $pts[$i + 1];
            $p3 = $pts[min($i + 2, $n - 1)];

            $c1x = $p1[0] + ($p2[0] - $p0[0]) / 6;
            $c1y = $clamp($p1[1] + ($p2[1] - $p0[1]) / 6);
            $c2x = $p2[0] - ($p3[0] - $p1[0]) / 6;
            $c2y = $clamp($p2[1] - ($p3[1] - $p1[1]) / 6);

            $d .= ' C' . $f($c1x) . ' ' . $f($c1y) . ' ' . $f($c2x) . ' ' . $f($c2y) . ' ' . $f($p2[0]) . ' ' . $f($p2[1]);
        }

        $aria = 'Biểu đồ chu kỳ vận số các năm ' . (int) $cycle[0]['year'] . ' đến ' . (int) $cycle[$n - 1]['year'];
        $svg = '<svg class="chart-svg" viewBox="0 0 ' . $w . ' ' . $h . '" role="img" aria-label="' . e($aria) . '" xmlns="http://www.w3.org/2000/svg">';

        // Thêm đoạn CSS nhỏ bên trong SVG để hỗ trợ xoay chữ 45 độ đẹp mắt
        $svg .= '<style>
            .chart-year { font-size: 12px; dominant-baseline: middle; text-anchor: end; }
            .chart-year-now { font-weight: bold; }
        </style>';

        foreach ($cycle as $i => $c) {
            $x = $f($pts[$i][0]);
            $isNow = (int) $c['year'] === $currentYear;
            $svg .= '<line class="' . ($isNow ? 'chart-now' : 'chart-guide') . '" x1="' . $x . '" y1="' . $top . '" x2="' . $x . '" y2="' . $axisY . '"/>';
        }

        $svg .= '<line class="chart-axis" x1="' . $left . '" y1="' . $axisY . '" x2="' . ($w - $right) . '" y2="' . $axisY . '"/>';
        $svg .= '<path class="chart-line" d="' . $d . '"/>';

        foreach ($cycle as $i => $c) {
            $x = $f($pts[$i][0]);
            $y = $f($pts[$i][1]);
            $year = (int) $c['year'];
            $isNow = $year === $currentYear;
            $label = !empty($c['master']) ? (int) $c['value'] . '/' . (int) $c['single'] : (string) (int) $c['single'];
            $tip = 'Năm ' . $year . ': số ' . $label;

            // Chấm tròn & số giá trị phía trên
            $svg .= '<circle class="chart-dot' . ($isNow ? ' chart-dot-now' : '') . '" cx="' . $x . '" cy="' . $y . '" r="' . ($isNow ? 6 : 4.5) . '"><title>' . e($tip) . '</title></circle>';
            $svg .= '<text class="chart-value' . ($isNow ? ' chart-value-now' : '') . '" x="' . $x . '" y="' . $f($pts[$i][1] - 13) . '" text-anchor="middle">' . e($label) . '</text>';
            
            // Xoay nghiêng nhãn năm 45 độ quanh tọa độ điểm ($x, $axisY + 16)
            $svg .= '<text class="chart-year' . ($isNow ? ' chart-year-now' : '') . '" x="' . $x . '" y="' . ($axisY + 16) . '" transform="rotate(-45 ' . $x . ' ' . ($axisY + 16) . ')" text-anchor="end">' . ($isNow ? '[' . $year . ']' : (string) $year) . '</text>';
        }

        return $svg . '</svg>';
    }
}