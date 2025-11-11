#include "schedule.hpp"
#include <random>
#include <algorithm>
#include <cmath>


std::vector<Slice> build_schedule(const ScheduleCfg& cfg) {
    std::vector<Slice> out; out.reserve(cfg.slices);
    auto span = cfg.end - cfg.start;
    auto dt = span / cfg.slices;
    std::vector<double> w(cfg.slices, 1.0);
    if (cfg.vwap && !cfg.weights.empty()) w = cfg.weights;
    double sumw = 0; for (auto x:w) sumw += x;
    if (sumw <= 0) sumw = 1.0;
    std::mt19937 rgn(42);
    std::uniform_real_distribution<double> jit(1.0 - cfg.jitter_pct, 1.0 + cfg.jitter_pct);


    int32_t assigned = 0;
    for (int i = 0; i < cfg.slices; ++i){
        double target = cfg.total_qty * (w[i]/sumw);
        int32_t q = std::max(1, (int32_t)std::lround(target * jit(rgn)));
        assigned += q;
        out.push_back(Slice{(cfg.start + dt * i).count(), q});
    } 

    int32_t diff = cfg.total_qty - assigned;
    if (!out.empty()) out.back().qty += diff;
    return out;
}

