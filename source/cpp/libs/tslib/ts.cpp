#include "ts.h"

/*Linearly weighted decay*/
std::vector<double> run_decay(const std::vector<double>& v, const std::vector<double>& w, const int min_valid, const bool exclude_nans) {
	int n = v.size();
	int window = w.size();
    double nan1 = std::numeric_limits<double>::quiet_NaN();
    std::vector<double> res(n, nan1);
    double w_tot_glob = 0.0;
    double TOL = 1e-8;

    for (int i = 0; i < window; ++i) {
        w_tot_glob += std::abs(w[i]);
    }

    std::vector<double> w_window(window, 0.0);
    int valid_count = 0;

    // First partial windows
    for (int i = 0; i < window; ++i) {
        int j = i;
        double w_tot = 0;
        valid_count = 0;
        res[i] = 0.0;
        if (v[i] == v[i]) {
            w_window[i] = w[i];
        }
        while (j >= 0) {
            if (v[j] == v[j]) {
                ++valid_count;
                res[i] += w[window - 1 - i + j] * v[j];
                w_tot += std::abs(w[window - 1 - i + j]);
            }
            --j;
        }
        if (valid_count >= min_valid) {
            if (exclude_nans) {
                res[i] /= w_tot;
            }
            else {
                res[i] /= w_tot_glob;
            }
        }
        else {
            res[i] = nan1;
        }
    }

    for (int i = window; i <= n - 1; ++i) {
        double w_tot = 0.0;
        res[i] = 0.0;
        if (std::abs(w_window[0]) > TOL) {
            --valid_count;
        }
        // Shift old weights left by 1 and build new weights
        for (int k = 0; k < window - 1; ++k) {
            w_window[k] = std::abs(w_window[k + 1]) > TOL ? w[k] : 0.0;
            w_tot += std::abs(w_window[k]);
            if (std::abs(w_window[k]) > TOL) {
                res[i] += w_window[k] * v[i - window + k + 1];
            }
        }
        w_window[window - 1] = 0.0;
        if (v[i] == v[i]) {
            ++valid_count;
            w_window[window - 1] = w.back();
            w_tot += std::abs(w_window[window - 1]);
            res[i] += w_window[window - 1] * v[i];
        }
        if (std::abs(w_tot) < TOL || valid_count < min_valid) {
            res[i] = nan1;
        }
        else {
            if (exclude_nans) {
                    res[i] /= w_tot;
            }
            else {
                res[i] /= w_tot_glob;
            }
        }
    }
    return res;
}

/* Strictly linear run_mean */
std::vector<double> run_mean(const std::vector<double>& v, const int window, const int min_valid) {
    int n = v.size();
    std::vector<double> result(n);
    int from = 0;
    int count_valid = 0;
    double sum = 0;
    for (int to = 0; to < n; ++to) {
        // add new observation
        if (std::isfinite(v[to])) {
            ++count_valid;
            sum += v[to];
        }
        // delete old observation
        if (to - from == window) {
            if (std::isfinite(v[from])) {
                --count_valid;
                sum -= v[from];
            }
            ++from;
        }
        // evaluate
        result[to] = (count_valid >= min_valid ? sum / count_valid : NAN);
    }
    return result;
}

/* Strictly linear run_var */
std::vector<double> run_var(const std::vector<double>& v, const int window, const int min_valid, const bool mean_zero, const int extra_df) // internal
{
    const int _min_valid = std::max<int>(min_valid, 2);
    const int n = v.size();
    std::vector<double> result(n);
    std::vector<double> mean(n, 0.0);
    if (!mean_zero) {
        mean = run_mean(v, window, min_valid);
    }
    int from = 0;
    int count_valid = 0;
    double sum = 0;
    for (int to = 0; to < n; ++to) {
        // add new observation
        if (std::isfinite(v[to])) {
            ++count_valid;
            sum += v[to] * v[to];
        }
        // delete old observation
        if (to - from == window) {
            if (std::isfinite(v[from])) {
                --count_valid;
                sum -= v[from] * v[from];
            }
            ++from;
        }
        // evaluate
        result[to] = (count_valid >= _min_valid ? 
            (sum - count_valid * mean[to] * mean[to]) / (count_valid - 1 + extra_df) : NAN);
    }
    return result;
}

/* Strictly linear run_sd */
std::vector<double> run_sd(const std::vector<double>& v, const int window, const int min_valid, const bool mean_zero, const int extra_df) // internal
{
    std::vector<double> result = run_var(v, window, min_valid, mean_zero, extra_df);
    int n = result.size();
    for (int i = 0; i < n; ++i) {
        result[i] = sqrt(result[i]);
    }
    return result;
}

 /* Complexity is between linear and O(length * window) depending on data*/
 std::vector<double> run_min(const std::vector<double>& v, const int window, const int min_valid = 1) {
     const int n = v.size();
     std::vector<double> result(n);
     int from = 0;
     double curr_min = NAN;
     int curr_count = 0;
     int count_valid = 0;
     for (int i = 0; i < n; ++i) {
         // add new observation
         if (std::isfinite(v[i])) {
             ++count_valid;
             if (!std::isfinite(curr_min) || v[i] < curr_min) {
                 curr_min = v[i];
                 curr_count = 1;
             } else if (curr_min == v[i]) {
                 ++curr_count;
             }
         }
         // remove old observation
         if (i - from == window) {
             if (std::isfinite(v[from])) {
                 --count_valid;
                 if (v[from] == curr_min) --curr_count;
                 if (curr_count == 0) {
                     // find new min
                     curr_min = NAN;
                     for (int j = from+1; j <= i; ++j) {
                         if (!std::isfinite(v[j])) continue;
                         if (!std::isfinite(curr_min) || v[j] < curr_min) {
                             curr_min = v[j];
                             curr_count = 1;
                         } else if (v[j] == curr_min) {
                             ++curr_count;
                         }
                     }
                 }
             }
             ++from;
         }
         // evaluate
         result[i] = (count_valid >= min_valid ? curr_min : NAN);
     }
     return result;
 }

 /* Complexity is between linear and O(length * window) depending on data*/
 std::vector<double> run_max(const std::vector<double>& v, const int window, const int min_valid = 1) {
     return -run_min(-v, window, min_valid);
 }

 /* Complexity is between linear and O(length * window) depending on data */
 std::vector<double> run_argmin(const std::vector<double>& v, const int window, const int min_valid) {
     const int n = v.size();
     std::vector<double> result(n);
     int from = 0;
     double curr_min = NAN;
     int curr_count = 0;
     int count_valid = 0;
     int last_position = 0;
     for (int i = 0; i < n; ++i) {
         // add new observation
         if (std::isfinite(v[i])) {
             ++count_valid;
             if (!std::isfinite(curr_min) || v[i] < curr_min) {
                 curr_min = v[i];
                 curr_count = 1;
                 last_position = i;
             } else if (curr_min == v[i]) {
                 ++curr_count;
                 last_position = i;
             }
         }
         // remove old observation
         if (i - from == window) {
             if (std::isfinite(v[from])) {
                 --count_valid;
                 if (v[from] == curr_min) --curr_count;
                 if (curr_count == 0) {
                     // find new min
                     curr_min = NAN;
                     for (int j = from+1; j <= i; ++j) {
                         if (!std::isfinite(v[j])) continue;
                         if (!std::isfinite(curr_min) || v[j] < curr_min) {
                             curr_min = v[j];
                             curr_count = 1;
                             last_position = j;
                         } else if (v[j] == curr_min) {
                             ++curr_count;
                             last_position = j;
                         }
                     }
                 }
             }
             ++from;
         }
         // evaluate
         result[i] = (count_valid >= min_valid ? i - last_position : NAN);
     }
     return result;
 }

 /* Complexity is between linear and O(length * window) depending on data */
 std::vector<double> run_argmax(const std::vector<double>& v, const int window, const int min_valid) {
     return run_argmin(-v, window, min_valid);
 }

 inline double smallest_set_element(const std::multiset<double>& s) {
     if (s.size() == 0) return NAN;
     return (*s.begin());
 }
 inline double pick_smallest_set_element(std::multiset<double>& s) {
     if (s.size() == 0) return NAN;
     double result = *s.begin();
     s.erase(s.begin());
     return result;
 }

 inline double largest_set_element(const std::multiset<double>& s) {
     if (s.size() == 0) return NAN;
     return(*(--(s.end())));
 }
 inline double pick_largest_set_element(std::multiset<double>& s) {
     if (s.size() == 0) return NAN;
     std::multiset<double>::iterator i = --(s.end());
     double result = *i;
     s.erase(i);
     return result;
 }

 /* Complexity is O(length * log(window)) */
 std::vector<double> run_quantile(const std::vector<double> v, const int window, const double q, const int min_valid = 1) {
     std::multiset<double> lower;
     std::multiset<double> upper;
     std::vector<double> result(v.size());
     int from = 0;
     for (int i = 0; i < v.size(); ++i) {
         // add new element
         if (std::isfinite(v[i])) {
             if (upper.size() == 0 || v[i] < smallest_set_element(upper)) lower.insert(v[i]);
             else upper.insert(v[i]);
         }
         // remove old element
         if (i - from == window) {
             if (std::isfinite(v[from])) {
                 std::multiset<double>::const_iterator i = lower.find(v[from]);
                 if (i != lower.end()) lower.erase(i);
                 else upper.erase(upper.find(v[from]));
             }
             ++from;
         }
         // redistribute
         int count_valid = lower.size() + upper.size();
         while (lower.size() > 0 && q <= (lower.size() - 0.5) / count_valid) {
             upper.insert(pick_largest_set_element(lower));
         }
         while (upper.size() > 0 && q >= (lower.size() + 0.5) / count_valid) {
             lower.insert(pick_smallest_set_element(upper));
         }
         // evaluate
         if (count_valid < min_valid) result[i] = NAN;
         else {
             if (lower.size() == 0) result[i] = smallest_set_element(upper);
             else if (upper.size() == 0) result[i] = largest_set_element(lower);
             else {
                 double r = q * count_valid - (lower.size() - 0.5);
                 result[i] = (1.0 - r) * largest_set_element(lower) + r * smallest_set_element(upper);
             }
         }
     }
     return result;
 }


 /* Complexity is O(length * log(window)) */
 std::vector<double> run_median(const std::vector<double> v, const int window, const int min_valid = 1) {
     return run_quantile(v, window, 0.5, min_valid);
 }


 /* Slope of simple linear regression
    Complexity is strictly linear */
 std::vector<double> run_ls_slope(const std::vector<double> x, const std::vector<double> y, const int window, const int min_valid = 2) {
     std::vector<double> sd_x = run_sd(x, window, min_valid, false, 1);
     for (int i = 0; i < sd_x.size(); ++i) if (sd_x[i] <= 0) sd_x[i] = NAN;
     std::vector<double> result = (run_mean(x * y, window, min_valid) -
         run_mean(x, window, min_valid) * run_mean(y, window, min_valid)) / pow(sd_x, 2.0);
     return result;
 }

 /* Sample covariance between two variables
    Complexity is strictly linear */
 std::vector<double> run_cov(const std::vector<double> x, const std::vector<double> y, const int window, const int min_valid = 2, const bool mean_zero_x = false, const bool mean_zero_y = false, const int extra_df = 0) { // internal
     int n = x.size();
     std::vector<double> mean_x(n, 0.0), mean_y(n, 0.0);
     if (!mean_zero_x) {
         mean_x = run_mean(x, window, min_valid);
     }
     if (!mean_zero_y) {
         mean_y = run_mean(y, window, min_valid);
     }
     std::vector<double> result(n);
     int from = 0;
     int count_valid = 0;
     double sum_x = 0.0, sum_y = 0.0, sum_xy = 0.0;
     for (int i = 0; i < n; ++i) {
         // add new observation
         if (std::isfinite(x[i]) && std::isfinite(y[i])) {
             ++count_valid;
             sum_x += x[i];
             sum_y += y[i];
             sum_xy += x[i] * y[i];
         }
         // delete old observation
         if (i - from == window) {
             if (std::isfinite(x[from]) && std::isfinite(y[from])) {
                 --count_valid;
                 sum_x -= x[from];
                 sum_y -= y[from];
                 sum_xy -= x[from] * y[from];
             }
             ++from;
         }
         // evaluate
         result[i] = (count_valid >= min_valid ? (sum_xy - sum_x * mean_y[i] - sum_y * mean_x[i] +
                      count_valid * mean_x[i] * mean_y[i]) / (count_valid - 1 + extra_df) : NAN);
     }
     return result;
 }

 /* Correlation between two variables
    Complexity is strictly linear */
 std::vector<double> run_cor(const std::vector<double> x, const std::vector<double> y, const int window, const int min_valid = 3, const bool mean_zero_x = false, const bool mean_zero_y = false) {
     // filter only pairwise complete
     std::vector<double> x_ = clone<std::vector<double>>(x);
     std::vector<double> y_ = clone<std::vector<double>>(y);
     for (int i = 0; i < x_.size(); ++i) {
         if (!std::isfinite(x_[i]) || !std::isfinite(y_[i])) {
             x_[i] = NAN;
             y_[i] = NAN;
         }
     }
     std::vector<double> result = run_cov(x_, y_, window, min_valid, mean_zero_x, mean_zero_y, 1);
     std::vector<double> sd_x = run_sd(x_, window, min_valid, mean_zero_x, 1);
     std::vector<double> sd_y = run_sd(y_, window, min_valid, mean_zero_y, 1);
     for (int i = 0; i < result.size(); ++i) {
         if (result[i] == 0) continue;
         if (sd_x[i] <= 0 || sd_y[i] <= 0) result[i] = NAN;
         else result[i] = result[i] / sd_x[i] / sd_y[i];
     }
     return result;
 }

 /* Complexity is strictly linear */
 std::vector<double> run_skew(const std::vector<double> x, const int window, const int min_valid = 2, const bool mean_zero = false) {
     int n = x.size();
     std::vector<double> mean(n, 0.0);
     if (!mean_zero) {
         mean = run_mean(x, window, min_valid);
     }
     std::vector<double> sd = run_sd(x, window, min_valid, mean_zero);
     std::vector<double> result(n, NAN);
     int from = 0;
     int count_valid = 0;
     double sum_x = 0;
     double sum_x2 = 0;
     double sum_x3 = 0;
     for (int i = 0; i < n; ++i) {
         // add new observation
         if (std::isfinite(x[i])) {
             ++count_valid;
             sum_x += x[i];
             sum_x2 += x[i] * x[i];
             sum_x3 += x[i] * x[i] * x[i];
         }
         // remove old beservation
         if (i - from == window) {
             if (std::isfinite(x[from])) {
                 --count_valid;
                 sum_x -= x[i];
                 sum_x2 -= x[i] * x[i];
                 sum_x3 -= x[i] * x[i] * x[i];
             }
             ++from;
         }
         // evaluate
         if (count_valid >= min_valid && sd[i] > 0) {
             result[i] = (sum_x3 - 3 * sum_x2 * mean[i] + 3 * sum_x * mean[i] * mean[i] +
                 count_valid * mean[i] * mean[i] * mean[i]) / count_valid / sd[i] / sd[i] / sd[i];
         }
     }
     return result;
 }

 /* Complexity is O(length(x) * length(kernel)) */
 /* Kernels with negative values are possible
    BUT analyze the code to understand how they
    interact with missing values */
 std::vector<double> run_smooth(const std::vector<double> x, const std::vector<double> kernel, const int min_valid = 1, const bool keep_na = false) {
     int n = x.size();
     int m = kernel.size();
     std::vector<double> result(n, NAN);
     int from = 0;
     int count_valid = 0;
     for (int i = 0; i < n; ++i) {
         // add point
         if (std::isfinite(x[i])) ++count_valid;
         // remove point
         if (i - from == m) {
             if (std::isfinite(x[from])) {
                 --count_valid;
                 ++from;
             }
         }
         // evaluate integral
         if (count_valid >= min_valid && (std::isfinite(x[i]) || !keep_na)) {
             double sum_wt = 0.0;
             double integral = 0.0;
             int to = std::min<int>(m, i + 1);
             for (int j = 0; j < to; ++j) {
                 if (std::isfinite(x[i - j])) {
                     sum_wt += fabs(kernel[j]);
                     integral += x[i - j] * kernel[j];
                 }
             }
             if (sum_wt > 0) result[i] = integral / sum_wt;
         }
     }
     return result;
 }

 /* fast lag */
 std::vector<double> lag_vector(const std::vector<double>& x, const int lag = 1) {
     if (lag == 0 || lag >= x.size() || -lag >= x.size()) return x;
     std::vector<double> result(x.size(), NAN);
     if (lag > 0) {
         std::memcpy(result.begin() + lag, x.begin(), (x.size() - lag) * sizeof(double));
         return result;
     }
     if (lag < 0) {
         std::memcpy(result.begin(), x.begin() + (-lag), (x.size() + lag) * sizeof(double));
         return result;
     }
     return result;
 }

 /* run_mdd */
 std::vector<double> run_mdd(const std::vector<double>& x, const int window, const int min_valid = 1) {
     int n = x.size();
     std::vector<double> result(n, NAN);
     int count_valid = 0;
     int from = 0;
     for (int i = 0; i < n; ++i) {
         // add observation
         if (std::isfinite(x[i])) {
             ++count_valid;
         }
         // remove old
         if (i - from == window) {
             if (std::isfinite(x[from])) {
                 --count_valid;
             }
             ++from;
         }
         // evaluate
         if (count_valid >= min_valid) {
             double curr_eqy = 0, max_eqy = 0, max_depth = 0, since = std::max<int>(0, i - window + 1);
             for (int j = since; j <= i; ++j) {
                 if (std::isfinite(x[j])) {
                     curr_eqy += x[j];
                     max_eqy = std::max<double>(curr_eqy, max_eqy);
                     max_depth = std::max(max_depth, max_eqy - curr_eqy);
                 }
             }
             result[i] = max_depth;
         }
     }
     return result;
 }

/* binary search in vector */
int binary_search_vector(const std::vector<double>& v, const double value) {
    int from = 0;
    int to = v.size();
    while (to - from > 1) {
        int mid = (from + to) / 2;
        if (v[mid] > value) to = mid;
        else from = mid;
    }
    return from;
}

/* run_rank */
std::vector<double> run_rank(const std::vector<double>& v, const int window, const double min_value, const double max_value, const int min_valid) {
    int n = v.size();
    std::vector<double> result(n, NAN);
    int from = 0;
    std::vector<double> buf;
    for (int i = 0; i < n; ++i) {
        // remove old observation
        if (i - from == window) {
            if (std::isfinite(v[from])) {
                buf.erase(buf.begin() + binary_search_vector(buf, v[from]));
            }
            ++from;
        }
        // add new observation
        if (std::isfinite(v[i])) {
            buf.push_back(v[i]);
            int pos = buf.size(); --pos;
            while (pos > 0 && buf[pos - 1] > buf[pos]) {
                std::swap(buf[pos - 1], buf[pos]);
                --pos;
            }
            if ((int)buf.size() >= min_valid) {
                int first_pos = pos;
                while (first_pos > 0 && buf[first_pos] == buf[first_pos - 1]) --first_pos;
                if (buf.size() == 1) result[i] = (min_value + max_value) / 2.0;
                else {
                    double q = 0.5 / (buf.size() - 1) * (first_pos + pos);
                    result[i] = min_value + q * (max_value - min_value);
                }
            }
        }
    }
    return result;
}

 /* run_zscore */
 std::vector<double> run_zscore(const std::vector<double>& v, const int window, const double min_value = -3.0, const double max_value = 3.0, const int min_valid = 2) {
     std::vector<double> result = v - run_mean(v, window, min_valid);
     std::vector<double> sd = run_sd(v, window, min_valid);
     for (int i = 0; i < sd.size(); ++i) {
         if (std::isfinite(sd[i]) && sd[i] > 0) {
             result[i] /= sd[i];
             if (std::isfinite(result[i])) {
                 result[i] = std::min<double>(max_value, std::max<double>(min_value, result[i]));
             }
         }
     }
     return result;
 }

 /* run_tapply */
 std::vector<double> run_tapply_mean(const std::vector<double>& v, const std::vector<int>& group, const int window, const int min_valid = 1) {
     // find all different groups
     int num_groups = 0;
     std::map<int, int> group_to_ix;
     for (int i = 0; i < group.size(); ++i) {
         if (!std::isfinite(v[i])) continue;
         if (group_to_ix.find(group[i]) == group_to_ix.end()) {
             group_to_ix[group[i]] = num_groups++;
         }
     }
     std::vector<double> sum(num_groups, 0.0);
     std::vector<int> count_valid(num_groups, 0);
     std::vector<double> result(v.size(), NAN);
     int from = 0;
     // go and count
     for (int i = 0; i < v.size(); ++i) {
         if (group_to_ix.find(group[i]) == group_to_ix.end()) continue;
         int ix = group_to_ix[group[i]];
         // add observation
         if (std::isfinite(v[i])) {
             sum[ix] += v[i];
             ++count_valid[ix];
         }
         // remove observation
         if (i - from == window) {
             if (std::isfinite(v[from])) {
                 int ix_from = group_to_ix[group[from]];
                 sum[ix_from] -= v[from];
                 --count_valid[ix_from];
             }
             ++from;
         }
         // assign value
         if (count_valid[ix] >= min_valid) {
             result[i] = sum[ix] / count_valid[ix];
         }
     }
     return result;
 }
