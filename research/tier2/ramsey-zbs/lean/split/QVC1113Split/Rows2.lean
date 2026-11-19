import QVC1113Split.Data

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.C1113
open RamseyAnalytic RamseyAnalytic.ControlGeometry

theorem rows2_0_ok : ControlCertificate.rowCheck data rows2_0 = true := by decide +kernel
theorem rows2_1_ok : ControlCertificate.rowCheck data rows2_1 = true := by decide +kernel
theorem rows2_2_ok : ControlCertificate.rowCheck data rows2_2 = true := by decide +kernel
theorem rows2_3_ok : ControlCertificate.rowCheck data rows2_3 = true := by decide +kernel
theorem rows2_4_ok : ControlCertificate.rowCheck data rows2_4 = true := by decide +kernel
theorem rows2_5_ok : ControlCertificate.rowCheck data rows2_5 = true := by decide +kernel
theorem rows2_6_ok : ControlCertificate.rowCheck data rows2_6 = true := by decide +kernel
theorem rows2_7_ok : ControlCertificate.rowCheck data rows2_7 = true := by decide +kernel
theorem rows2_8_ok : ControlCertificate.rowCheck data rows2_8 = true := by decide +kernel
theorem rows2_9_ok : ControlCertificate.rowCheck data rows2_9 = true := by decide +kernel
theorem rows2_10_ok : ControlCertificate.rowCheck data rows2_10 = true := by decide +kernel
theorem rows2_11_ok : ControlCertificate.rowCheck data rows2_11 = true := by decide +kernel
theorem rows2_12_ok : ControlCertificate.rowCheck data rows2_12 = true := by decide +kernel
theorem rows2_13_ok : ControlCertificate.rowCheck data rows2_13 = true := by decide +kernel
theorem rows2_14_ok : ControlCertificate.rowCheck data rows2_14 = true := by decide +kernel
theorem rows2_15_ok : ControlCertificate.rowCheck data rows2_15 = true := by decide +kernel
theorem rows2_16_ok : ControlCertificate.rowCheck data rows2_16 = true := by decide +kernel
theorem rows2_17_ok : ControlCertificate.rowCheck data rows2_17 = true := by decide +kernel
theorem rows2_18_ok : ControlCertificate.rowCheck data rows2_18 = true := by decide +kernel
theorem rows2_19_ok : ControlCertificate.rowCheck data rows2_19 = true := by decide +kernel
theorem rows2_20_ok : ControlCertificate.rowCheck data rows2_20 = true := by decide +kernel
theorem rows2_21_ok : ControlCertificate.rowCheck data rows2_21 = true := by decide +kernel
theorem rows2_22_ok : ControlCertificate.rowCheck data rows2_22 = true := by decide +kernel
theorem rows2_23_ok : ControlCertificate.rowCheck data rows2_23 = true := by decide +kernel
theorem rows2_24_ok : ControlCertificate.rowCheck data rows2_24 = true := by decide +kernel
theorem rows2_checked : rows2.all (ControlCertificate.rowCheck data) = true := by
  simp only [rows2, List.all_cons, List.all_nil, rows2_0_ok, rows2_1_ok, rows2_2_ok, rows2_3_ok, rows2_4_ok, rows2_5_ok, rows2_6_ok, rows2_7_ok, rows2_8_ok, rows2_9_ok, rows2_10_ok, rows2_11_ok, rows2_12_ok, rows2_13_ok, rows2_14_ok, rows2_15_ok, rows2_16_ok, rows2_17_ok, rows2_18_ok, rows2_19_ok, rows2_20_ok, rows2_21_ok, rows2_22_ok, rows2_23_ok, rows2_24_ok, Bool.and_self, Bool.true_and, Bool.and_true]

end QV.RamseyZBS.C1113
