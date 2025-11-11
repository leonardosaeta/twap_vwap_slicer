#pragma once
#include <vector>
#include <string>
#include <chrono>
#include <cstdint>

struct Slice{
    int64_t ts_ns; 
    int32_t qty; 
};


struct ScheduleCfg{
    std::chrono::nanoseconds start, end;
    int32_t total_qty;
    int32_t slices; 
    bool vwap = false;
    std::vector<double> weights;
    double jitter_pct = 0.05; 
};

std::vector<Slice> build_schedule(const ScheduleCfg& cfg);
