#include "schedule.hpp"
#include "metrics.hpp"
#include <iostream>
#include <fstream>
#include <sstream>

int main(int argc, char** argv) {
    ScheduleCfg cfg;
    cfg.total_qty = 10000;
    cfg.slices = 20;
    cfg.start = std::chrono::seconds(0);
    cfg.end   = std::chrono::minutes(10);
    cfg.vwap = false;

    auto sched = build_schedule(cfg);

    std::vector<Exec> fills; fills.reserve(sched.size());
    int32_t mid = 10000;
    int8_t side = +1;   

    std::ofstream orders("orders.csv");
    orders << "ts_ns,qty,limit_px\n";
    for (auto& s : sched) {
        int32_t limit_px = mid + (side>0 ? +1 : -1);
        orders << s.ts_ns << "," << s.qty << "," << limit_px << "\n";
        fills.push_back(Exec{ s.ts_ns, s.qty, limit_px, mid, side });
    }
    orders.close();

    auto sum = summarize(fills);
    std::ofstream summary("summary.csv");
    summary << "avg_px,slippage_bps\n" << sum.avg_px << "," << sum.slippage_bps << "\n";
    summary.close();

    std::cout << "Wrote orders.csv and summary.csv\n";
    return 0;
}