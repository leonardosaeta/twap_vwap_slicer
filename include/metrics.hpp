#pragma once
#include <cstdint>
#include <vector>

struct Exec {
    int64_t ts_ns;
    int32_t qty;
    int32_t px;
    int32_t mid;
    int8_t side;
};

struct Summary{
    double avg_px = 0.0;
    double slippage_bps = 0.0;
};

Summary summarize (const std::vector<Exec>& fills);