import QVC1113Split.Data

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.C1113
open RamseyAnalytic RamseyAnalytic.ControlGeometry

theorem rows0_0_ok : ControlCertificate.rowCheck data rows0_0 = true := by decide +kernel
theorem rows0_1_ok : ControlCertificate.rowCheck data rows0_1 = true := by decide +kernel
theorem rows0_2_ok : ControlCertificate.rowCheck data rows0_2 = true := by decide +kernel
theorem rows0_3_ok : ControlCertificate.rowCheck data rows0_3 = true := by decide +kernel
theorem rows0_4_ok : ControlCertificate.rowCheck data rows0_4 = true := by decide +kernel
theorem rows0_5_ok : ControlCertificate.rowCheck data rows0_5 = true := by decide +kernel
theorem rows0_6_ok : ControlCertificate.rowCheck data rows0_6 = true := by decide +kernel
theorem rows0_7_ok : ControlCertificate.rowCheck data rows0_7 = true := by decide +kernel
theorem rows0_8_ok : ControlCertificate.rowCheck data rows0_8 = true := by decide +kernel
theorem rows0_9_ok : ControlCertificate.rowCheck data rows0_9 = true := by decide +kernel
theorem rows0_10_ok : ControlCertificate.rowCheck data rows0_10 = true := by decide +kernel
theorem rows0_11_ok : ControlCertificate.rowCheck data rows0_11 = true := by decide +kernel
theorem rows0_12_ok : ControlCertificate.rowCheck data rows0_12 = true := by decide +kernel
theorem rows0_13_ok : ControlCertificate.rowCheck data rows0_13 = true := by decide +kernel
theorem rows0_14_ok : ControlCertificate.rowCheck data rows0_14 = true := by decide +kernel
theorem rows0_15_ok : ControlCertificate.rowCheck data rows0_15 = true := by decide +kernel
theorem rows0_16_ok : ControlCertificate.rowCheck data rows0_16 = true := by decide +kernel
theorem rows0_17_ok : ControlCertificate.rowCheck data rows0_17 = true := by decide +kernel
theorem rows0_18_ok : ControlCertificate.rowCheck data rows0_18 = true := by decide +kernel
theorem rows0_19_ok : ControlCertificate.rowCheck data rows0_19 = true := by decide +kernel
theorem rows0_20_ok : ControlCertificate.rowCheck data rows0_20 = true := by decide +kernel
theorem rows0_21_ok : ControlCertificate.rowCheck data rows0_21 = true := by decide +kernel
theorem rows0_22_ok : ControlCertificate.rowCheck data rows0_22 = true := by decide +kernel
theorem rows0_23_ok : ControlCertificate.rowCheck data rows0_23 = true := by decide +kernel
theorem rows0_24_ok : ControlCertificate.rowCheck data rows0_24 = true := by decide +kernel
theorem rows0_checked : rows0.all (ControlCertificate.rowCheck data) = true := by
  simp only [rows0, List.all_cons, List.all_nil, rows0_0_ok, rows0_1_ok, rows0_2_ok, rows0_3_ok, rows0_4_ok, rows0_5_ok, rows0_6_ok, rows0_7_ok, rows0_8_ok, rows0_9_ok, rows0_10_ok, rows0_11_ok, rows0_12_ok, rows0_13_ok, rows0_14_ok, rows0_15_ok, rows0_16_ok, rows0_17_ok, rows0_18_ok, rows0_19_ok, rows0_20_ok, rows0_21_ok, rows0_22_ok, rows0_23_ok, rows0_24_ok, Bool.and_self, Bool.true_and, Bool.and_true]

end QV.RamseyZBS.C1113
