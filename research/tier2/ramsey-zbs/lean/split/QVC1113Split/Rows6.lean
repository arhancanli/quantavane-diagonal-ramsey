import QVC1113Split.Data

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.C1113
open RamseyAnalytic RamseyAnalytic.ControlGeometry

theorem rows6_0_ok : ControlCertificate.rowCheck data rows6_0 = true := by decide +kernel
theorem rows6_1_ok : ControlCertificate.rowCheck data rows6_1 = true := by decide +kernel
theorem rows6_2_ok : ControlCertificate.rowCheck data rows6_2 = true := by decide +kernel
theorem rows6_3_ok : ControlCertificate.rowCheck data rows6_3 = true := by decide +kernel
theorem rows6_4_ok : ControlCertificate.rowCheck data rows6_4 = true := by decide +kernel
theorem rows6_5_ok : ControlCertificate.rowCheck data rows6_5 = true := by decide +kernel
theorem rows6_6_ok : ControlCertificate.rowCheck data rows6_6 = true := by decide +kernel
theorem rows6_7_ok : ControlCertificate.rowCheck data rows6_7 = true := by decide +kernel
theorem rows6_8_ok : ControlCertificate.rowCheck data rows6_8 = true := by decide +kernel
theorem rows6_9_ok : ControlCertificate.rowCheck data rows6_9 = true := by decide +kernel
theorem rows6_10_ok : ControlCertificate.rowCheck data rows6_10 = true := by decide +kernel
theorem rows6_11_ok : ControlCertificate.rowCheck data rows6_11 = true := by decide +kernel
theorem rows6_12_ok : ControlCertificate.rowCheck data rows6_12 = true := by decide +kernel
theorem rows6_13_ok : ControlCertificate.rowCheck data rows6_13 = true := by decide +kernel
theorem rows6_14_ok : ControlCertificate.rowCheck data rows6_14 = true := by decide +kernel
theorem rows6_15_ok : ControlCertificate.rowCheck data rows6_15 = true := by decide +kernel
theorem rows6_16_ok : ControlCertificate.rowCheck data rows6_16 = true := by decide +kernel
theorem rows6_17_ok : ControlCertificate.rowCheck data rows6_17 = true := by decide +kernel
theorem rows6_18_ok : ControlCertificate.rowCheck data rows6_18 = true := by decide +kernel
theorem rows6_19_ok : ControlCertificate.rowCheck data rows6_19 = true := by decide +kernel
theorem rows6_20_ok : ControlCertificate.rowCheck data rows6_20 = true := by decide +kernel
theorem rows6_21_ok : ControlCertificate.rowCheck data rows6_21 = true := by decide +kernel
theorem rows6_22_ok : ControlCertificate.rowCheck data rows6_22 = true := by decide +kernel
theorem rows6_23_ok : ControlCertificate.rowCheck data rows6_23 = true := by decide +kernel
theorem rows6_24_ok : ControlCertificate.rowCheck data rows6_24 = true := by decide +kernel
theorem rows6_checked : rows6.all (ControlCertificate.rowCheck data) = true := by
  simp only [rows6, List.all_cons, List.all_nil, rows6_0_ok, rows6_1_ok, rows6_2_ok, rows6_3_ok, rows6_4_ok, rows6_5_ok, rows6_6_ok, rows6_7_ok, rows6_8_ok, rows6_9_ok, rows6_10_ok, rows6_11_ok, rows6_12_ok, rows6_13_ok, rows6_14_ok, rows6_15_ok, rows6_16_ok, rows6_17_ok, rows6_18_ok, rows6_19_ok, rows6_20_ok, rows6_21_ok, rows6_22_ok, rows6_23_ok, rows6_24_ok, Bool.and_self, Bool.true_and, Bool.and_true]

end QV.RamseyZBS.C1113
