import QVRootSplit.Data

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.Root
open RamseyAnalytic RamseyAnalytic.ControlGeometry

theorem rows3_0_ok : ControlCertificate.rowCheck data rows3_0 = true := by decide +kernel
theorem rows3_1_ok : ControlCertificate.rowCheck data rows3_1 = true := by decide +kernel
theorem rows3_2_ok : ControlCertificate.rowCheck data rows3_2 = true := by decide +kernel
theorem rows3_3_ok : ControlCertificate.rowCheck data rows3_3 = true := by decide +kernel
theorem rows3_4_ok : ControlCertificate.rowCheck data rows3_4 = true := by decide +kernel
theorem rows3_5_ok : ControlCertificate.rowCheck data rows3_5 = true := by decide +kernel
theorem rows3_6_ok : ControlCertificate.rowCheck data rows3_6 = true := by decide +kernel
theorem rows3_7_ok : ControlCertificate.rowCheck data rows3_7 = true := by decide +kernel
theorem rows3_8_ok : ControlCertificate.rowCheck data rows3_8 = true := by decide +kernel
theorem rows3_9_ok : ControlCertificate.rowCheck data rows3_9 = true := by decide +kernel
theorem rows3_10_ok : ControlCertificate.rowCheck data rows3_10 = true := by decide +kernel
theorem rows3_11_ok : ControlCertificate.rowCheck data rows3_11 = true := by decide +kernel
theorem rows3_12_ok : ControlCertificate.rowCheck data rows3_12 = true := by decide +kernel
theorem rows3_13_ok : ControlCertificate.rowCheck data rows3_13 = true := by decide +kernel
theorem rows3_14_ok : ControlCertificate.rowCheck data rows3_14 = true := by decide +kernel
theorem rows3_15_ok : ControlCertificate.rowCheck data rows3_15 = true := by decide +kernel
theorem rows3_16_ok : ControlCertificate.rowCheck data rows3_16 = true := by decide +kernel
theorem rows3_17_ok : ControlCertificate.rowCheck data rows3_17 = true := by decide +kernel
theorem rows3_18_ok : ControlCertificate.rowCheck data rows3_18 = true := by decide +kernel
theorem rows3_19_ok : ControlCertificate.rowCheck data rows3_19 = true := by decide +kernel
theorem rows3_20_ok : ControlCertificate.rowCheck data rows3_20 = true := by decide +kernel
theorem rows3_21_ok : ControlCertificate.rowCheck data rows3_21 = true := by decide +kernel
theorem rows3_22_ok : ControlCertificate.rowCheck data rows3_22 = true := by decide +kernel
theorem rows3_23_ok : ControlCertificate.rowCheck data rows3_23 = true := by decide +kernel
theorem rows3_24_ok : ControlCertificate.rowCheck data rows3_24 = true := by decide +kernel
theorem rows3_checked : rows3.all (ControlCertificate.rowCheck data) = true := by
  simp only [rows3, List.all_cons, List.all_nil, rows3_0_ok, rows3_1_ok, rows3_2_ok, rows3_3_ok, rows3_4_ok, rows3_5_ok, rows3_6_ok, rows3_7_ok, rows3_8_ok, rows3_9_ok, rows3_10_ok, rows3_11_ok, rows3_12_ok, rows3_13_ok, rows3_14_ok, rows3_15_ok, rows3_16_ok, rows3_17_ok, rows3_18_ok, rows3_19_ok, rows3_20_ok, rows3_21_ok, rows3_22_ok, rows3_23_ok, rows3_24_ok, Bool.and_self, Bool.true_and, Bool.and_true]

end QV.RamseyZBS.Root
