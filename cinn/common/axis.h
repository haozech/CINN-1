#pragma once
#include <functional>
#include <string>
#include <utility>
#include <vector>

namespace cinn {
namespace ir {

struct Var;
struct Expr;

}  // namespace ir
}  // namespace cinn

namespace cinn {
namespace common {

//! Get the predifined axis name.
const std::string& axis_name(int level);

//! Generate `naxis` axis using the global names (i,j,k...).
std::vector<ir::Var> GenDefaultAxis(int naxis);
std::vector<ir::Expr> GenDefaultAxisAsExpr(int naxis);

bool IsAxisNameReserved(const std::string& x);

}  // namespace common
}  // namespace cinn
