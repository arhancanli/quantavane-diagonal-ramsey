import QVC1113Split.Data

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.C1113
open RamseyAnalytic RamseyAnalytic.ControlGeometry

theorem rows8_0_ok : ControlCertificate.rowCheck data rows8_0 = true := by decide +kernel
theorem rows8_1_ok : ControlCertificate.rowCheck data rows8_1 = true := by decide +kernel
theorem rows8_2_ok : ControlCertificate.rowCheck data rows8_2 = true := by decide +kernel
theorem rows8_checked : rows8.all (ControlCertificate.rowCheck data) = true := by
  simp only [rows8, List.all_cons, List.all_nil, rows8_0_ok, rows8_1_ok, rows8_2_ok, Bool.and_self, Bool.true_and, Bool.and_true]

end QV.RamseyZBS.C1113
