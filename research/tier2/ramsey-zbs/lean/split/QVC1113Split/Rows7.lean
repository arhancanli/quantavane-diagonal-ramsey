import QVC1113Split.Data

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.C1113
open RamseyAnalytic RamseyAnalytic.ControlGeometry

theorem rows7_0_ok : ControlCertificate.rowCheck data rows7_0 = true := by decide +kernel
theorem rows7_1_ok : ControlCertificate.rowCheck data rows7_1 = true := by decide +kernel
theorem rows7_2_ok : ControlCertificate.rowCheck data rows7_2 = true := by decide +kernel
theorem rows7_3_ok : ControlCertificate.rowCheck data rows7_3 = true := by decide +kernel
theorem rows7_4_ok : ControlCertificate.rowCheck data rows7_4 = true := by decide +kernel
theorem rows7_5_ok : ControlCertificate.rowCheck data rows7_5 = true := by decide +kernel
theorem rows7_6_ok : ControlCertificate.rowCheck data rows7_6 = true := by decide +kernel
theorem rows7_7_ok : ControlCertificate.rowCheck data rows7_7 = true := by decide +kernel
theorem rows7_8_ok : ControlCertificate.rowCheck data rows7_8 = true := by decide +kernel
theorem rows7_9_ok : ControlCertificate.rowCheck data rows7_9 = true := by decide +kernel
theorem rows7_10_ok : ControlCertificate.rowCheck data rows7_10 = true := by decide +kernel
theorem rows7_11_ok : ControlCertificate.rowCheck data rows7_11 = true := by decide +kernel
theorem rows7_12_ok : ControlCertificate.rowCheck data rows7_12 = true := by decide +kernel
theorem rows7_13_ok : ControlCertificate.rowCheck data rows7_13 = true := by decide +kernel
theorem rows7_14_ok : ControlCertificate.rowCheck data rows7_14 = true := by decide +kernel
theorem rows7_15_ok : ControlCertificate.rowCheck data rows7_15 = true := by decide +kernel
theorem rows7_16_ok : ControlCertificate.rowCheck data rows7_16 = true := by decide +kernel
theorem rows7_17_ok : ControlCertificate.rowCheck data rows7_17 = true := by decide +kernel
theorem rows7_18_ok : ControlCertificate.rowCheck data rows7_18 = true := by decide +kernel
theorem rows7_19_ok : ControlCertificate.rowCheck data rows7_19 = true := by decide +kernel
theorem rows7_20_ok : ControlCertificate.rowCheck data rows7_20 = true := by decide +kernel
theorem rows7_21_ok : ControlCertificate.rowCheck data rows7_21 = true := by decide +kernel
theorem rows7_22_ok : ControlCertificate.rowCheck data rows7_22 = true := by decide +kernel
theorem rows7_23_ok : ControlCertificate.rowCheck data rows7_23 = true := by decide +kernel
theorem rows7_24_ok : ControlCertificate.rowCheck data rows7_24 = true := by decide +kernel
theorem rows7_checked : rows7.all (ControlCertificate.rowCheck data) = true := by
  simp only [rows7, List.all_cons, List.all_nil, rows7_0_ok, rows7_1_ok, rows7_2_ok, rows7_3_ok, rows7_4_ok, rows7_5_ok, rows7_6_ok, rows7_7_ok, rows7_8_ok, rows7_9_ok, rows7_10_ok, rows7_11_ok, rows7_12_ok, rows7_13_ok, rows7_14_ok, rows7_15_ok, rows7_16_ok, rows7_17_ok, rows7_18_ok, rows7_19_ok, rows7_20_ok, rows7_21_ok, rows7_22_ok, rows7_23_ok, rows7_24_ok, Bool.and_self, Bool.true_and, Bool.and_true]

end QV.RamseyZBS.C1113
