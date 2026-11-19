import QVC1113Split.Data

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.C1113
open RamseyAnalytic RamseyAnalytic.ControlGeometry

theorem rows1_0_ok : ControlCertificate.rowCheck data rows1_0 = true := by decide +kernel
theorem rows1_1_ok : ControlCertificate.rowCheck data rows1_1 = true := by decide +kernel
theorem rows1_2_ok : ControlCertificate.rowCheck data rows1_2 = true := by decide +kernel
theorem rows1_3_ok : ControlCertificate.rowCheck data rows1_3 = true := by decide +kernel
theorem rows1_4_ok : ControlCertificate.rowCheck data rows1_4 = true := by decide +kernel
theorem rows1_5_ok : ControlCertificate.rowCheck data rows1_5 = true := by decide +kernel
theorem rows1_6_ok : ControlCertificate.rowCheck data rows1_6 = true := by decide +kernel
theorem rows1_7_ok : ControlCertificate.rowCheck data rows1_7 = true := by decide +kernel
theorem rows1_8_ok : ControlCertificate.rowCheck data rows1_8 = true := by decide +kernel
theorem rows1_9_ok : ControlCertificate.rowCheck data rows1_9 = true := by decide +kernel
theorem rows1_10_ok : ControlCertificate.rowCheck data rows1_10 = true := by decide +kernel
theorem rows1_11_ok : ControlCertificate.rowCheck data rows1_11 = true := by decide +kernel
theorem rows1_12_ok : ControlCertificate.rowCheck data rows1_12 = true := by decide +kernel
theorem rows1_13_ok : ControlCertificate.rowCheck data rows1_13 = true := by decide +kernel
theorem rows1_14_ok : ControlCertificate.rowCheck data rows1_14 = true := by decide +kernel
theorem rows1_15_ok : ControlCertificate.rowCheck data rows1_15 = true := by decide +kernel
theorem rows1_16_ok : ControlCertificate.rowCheck data rows1_16 = true := by decide +kernel
theorem rows1_17_ok : ControlCertificate.rowCheck data rows1_17 = true := by decide +kernel
theorem rows1_18_ok : ControlCertificate.rowCheck data rows1_18 = true := by decide +kernel
theorem rows1_19_ok : ControlCertificate.rowCheck data rows1_19 = true := by decide +kernel
theorem rows1_20_ok : ControlCertificate.rowCheck data rows1_20 = true := by decide +kernel
theorem rows1_21_ok : ControlCertificate.rowCheck data rows1_21 = true := by decide +kernel
theorem rows1_22_ok : ControlCertificate.rowCheck data rows1_22 = true := by decide +kernel
theorem rows1_23_ok : ControlCertificate.rowCheck data rows1_23 = true := by decide +kernel
theorem rows1_24_ok : ControlCertificate.rowCheck data rows1_24 = true := by decide +kernel
theorem rows1_checked : rows1.all (ControlCertificate.rowCheck data) = true := by
  simp only [rows1, List.all_cons, List.all_nil, rows1_0_ok, rows1_1_ok, rows1_2_ok, rows1_3_ok, rows1_4_ok, rows1_5_ok, rows1_6_ok, rows1_7_ok, rows1_8_ok, rows1_9_ok, rows1_10_ok, rows1_11_ok, rows1_12_ok, rows1_13_ok, rows1_14_ok, rows1_15_ok, rows1_16_ok, rows1_17_ok, rows1_18_ok, rows1_19_ok, rows1_20_ok, rows1_21_ok, rows1_22_ok, rows1_23_ok, rows1_24_ok, Bool.and_self, Bool.true_and, Bool.and_true]

end QV.RamseyZBS.C1113
