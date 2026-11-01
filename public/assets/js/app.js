// Trên màn hình hẹp biểu đồ chu kỳ có thanh cuộn ngang: cuộn tới giữa để thấy năm hiện tại.
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.chart-scroll').forEach(function (box) {
    box.scrollLeft = (box.scrollWidth - box.clientWidth) / 2;
  });
});
