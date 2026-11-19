import QVC1113Split.Data

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.C1113
open RamseyAnalytic RamseyAnalytic.ControlGeometry

theorem corner2 : cl2.all (fun i => data.degrees.all (fun d => ParametricEnvelope.cornerCheck data.w d i)) = true := by decide +kernel

end QV.RamseyZBS.C1113
