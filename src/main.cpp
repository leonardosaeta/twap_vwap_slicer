#include <iostream>
#include <vector>
#include <chrono>
#include "schedule.hpp"

int main() {
  ScheduleCfg cfg{};
  cfg.start = std::chrono::nanoseconds(0);
  cfg.end = std::chrono::seconds(10);
  cfg.total_qty = 1000;
  cfg.slices = 10;
  cfg.vwap = false;
  cfg.jitter_pct = 0.05;

  auto schedule = build_schedule(cfg);

  int64_t sum_qty = 0;
  std::cout << "Generated " << schedule.size() << " slices:\n";
  for (const auto& s : schedule) {
    std::cout << "ts_ns=" << s.ts_ns << " qty=" << s.qty << "\n";
    sum_qty += s.qty;
  }
  std::cout << "Total qty assigned = " << sum_qty << " (target " << cfg.total_qty << ")\n";
  return 0;
}