#include <vector>
#include <numeric>
#include <algorithm>
#include <iostream>
#include <iostream>
#include <cmath>
#include <cfloat>
#include <map>
#include <limits>

std::vector<double> run_mean(const std::vector<double>& v, const int window, const int min_valid = 1);
std::vector<double> run_var(const std::vector<double>& v, const int window, const int min_valid = 2, const bool mean_zero = false, const int extra_df = 0);
std::vector<double> run_sd(const std::vector<double>& v, const int window, const int min_valid = 2, const bool mean_zero = false, const int extra_df = 0) ;
std::vector<double> run_min(const std::vector<double>& v, const int window, const int min_valid = 1);
std::vector<double> run_max(const std::vector<double>& v, const int window, const int min_valid = 1);
std::vector<double> run_argmin(const std::vector<double>& v, const int window, const int min_valid = 1);
std::vector<double> run_argmax(const std::vector<double>& v, const int window, const int min_valid = 1) ;
std::vector<double> run_quantile(const std::vector<double> v, const int window, const double q, const int min_valid = 1) ;
std::vector<double> run_median(const std::vector<double> v, const int window, const int min_valid = 1) ;
std::vector<double> run_ls_slope(const std::vector<double> x, const std::vector<double> y, const int window, const int min_valid = 2);
std::vector<double> run_cov(const std::vector<double> x, const std::vector<double> y, const int window, const int min_valid = 2, const bool mean_zero_x = false, const bool mean_zero_y = false, const int extra_df = 0);
std::vector<double> run_cor(const std::vector<double> x, const std::vector<double> y, const int window, const int min_valid = 3, const bool mean_zero_x = false, const bool mean_zero_y = false);
std::vector<double> run_skew(const std::vector<double> x, const int window, const int min_valid = 2, const bool mean_zero = false) ;
std::vector<double> run_smooth(const std::vector<double> x, const std::vector<double> kernel, const int min_valid = 1, const bool keep_na = false);
std::vector<double> lag_vector(const std::vector<double>& x, const int lag = 1) ;
std::vector<double> run_mdd(const std::vector<double>& x, const int window, const int min_valid = 1);
std::vector<double> run_rank(const std::vector<double>& v, const int window, const double min_value = -1.0, const double max_value = 1.0, const int min_valid = 1);
std::vector<double> run_zscore(const std::vector<double>& v, const int window, const double min_value = -3.0, const double max_value = 3.0, const int min_valid = 2);
std::vector<double> run_tapply_mean(const std::vector<double>& v, const std::vector<int>& group, const int window, const int min_valid = 1);
std::vector<double> run_decay(const std::vector<double>& v, const std::vector<double>& w, const int min_valid = 1, const bool exclude_nans = false);
