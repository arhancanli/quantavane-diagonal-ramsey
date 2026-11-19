import QVC1113Split.Data

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.C1113
open RamseyAnalytic RamseyAnalytic.ControlGeometry

theorem integral_checked :
    ((ControlCertificate.totalExpr data).safe (AnalyticBounds.FixedPointInterval.point 0) &&
      decide (RamseyAnalytic.TangentExpressions.boundHi
        ((ControlCertificate.totalExpr data).bound (AnalyticBounds.FixedPointInterval.point 0)) < -data.margin)) = true := by
  decide +kernel

end QV.RamseyZBS.C1113
