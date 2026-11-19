import QVC1113Split.Data

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.C1113
open RamseyAnalytic RamseyAnalytic.ControlGeometry

theorem power_checked : ControlPower.check data.μ data.w data.x = true := by decide +kernel
theorem ctl_ok : ctl.ok = true := by decide +kernel

end QV.RamseyZBS.C1113
