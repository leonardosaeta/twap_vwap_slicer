#include "metrics.hpp"
#include <vector>

Summary summarize(const std::vector<Exec>& v){
    long long qsum=0, notional=0, slip_num=0;
    for (const auto& e: v){
        qsum += e.qty;
        notional += 1LL * e.qty * e.px;
        slip_num += 1LL * e.qty * e.side * (e.px - e.mid);
    }

    Summary s;
    if (qsum > 0){
        s.avg_px = double(notional)/qsum;
        s.slippage_bps = 100000.0 * (double(slip_num)/qsum) / s.avg_px;
    }
    return s;
}