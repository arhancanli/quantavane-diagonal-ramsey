import QVRootSplit.Data

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.Root
open RamseyAnalytic RamseyAnalytic.ControlGeometry

theorem rows5_0_ok : ControlCertificate.rowCheck data rows5_0 = true := by decide +kernel
theorem rows5_1_ok : ControlCertificate.rowCheck data rows5_1 = true := by decide +kernel
theorem rows5_2_ok : ControlCertificate.rowCheck data rows5_2 = true := by decide +kernel
theorem rows5_3_ok : ControlCertificate.rowCheck data rows5_3 = true := by decide +kernel
theorem rows5_4_ok : ControlCertificate.rowCheck data rows5_4 = true := by decide +kernel
theorem rows5_5_ok : ControlCertificate.rowCheck data rows5_5 = true := by decide +kernel
theorem rows5_6_ok : ControlCertificate.rowCheck data rows5_6 = true := by decide +kernel
theorem rows5_7_ok : ControlCertificate.rowCheck data rows5_7 = true := by decide +kernel
theorem rows5_8_ok : ControlCertificate.rowCheck data rows5_8 = true := by decide +kernel
theorem rows5_9_ok : ControlCertificate.rowCheck data rows5_9 = true := by decide +kernel
theorem rows5_10_ok : ControlCertificate.rowCheck data rows5_10 = true := by decide +kernel
theorem rows5_11_ok : ControlCertificate.rowCheck data rows5_11 = true := by decide +kernel
theorem rows5_12_ok : ControlCertificate.rowCheck data rows5_12 = true := by decide +kernel
theorem rows5_13_ok : ControlCertificate.rowCheck data rows5_13 = true := by decide +kernel
theorem rows5_14_ok : ControlCertificate.rowCheck data rows5_14 = true := by decide +kernel
theorem rows5_15_ok : ControlCertificate.rowCheck data rows5_15 = true := by decide +kernel
theorem rows5_16_ok : ControlCertificate.rowCheck data rows5_16 = true := by decide +kernel
theorem rows5_17_ok : ControlCertificate.rowCheck data rows5_17 = true := by decide +kernel
theorem rows5_18_ok : ControlCertificate.rowCheck data rows5_18 = true := by decide +kernel
theorem rows5_19_ok : ControlCertificate.rowCheck data rows5_19 = true := by decide +kernel
theorem rows5_20_ok : ControlCertificate.rowCheck data rows5_20 = true := by decide +kernel
theorem rows5_21_ok : ControlCertificate.rowCheck data rows5_21 = true := by decide +kernel
theorem rows5_22_ok : ControlCertificate.rowCheck data rows5_22 = true := by decide +kernel
theorem rows5_23_ok : ControlCertificate.rowCheck data rows5_23 = true := by decide +kernel
theorem rows5_24_ok : ControlCertificate.rowCheck data rows5_24 = true := by decide +kernel
theorem rows5_checked : rows5.all (ControlCertificate.rowCheck data) = true := by
  simp only [rows5, List.all_cons, List.all_nil, rows5_0_ok, rows5_1_ok, rows5_2_ok, rows5_3_ok, rows5_4_ok, rows5_5_ok, rows5_6_ok, rows5_7_ok, rows5_8_ok, rows5_9_ok, rows5_10_ok, rows5_11_ok, rows5_12_ok, rows5_13_ok, rows5_14_ok, rows5_15_ok, rows5_16_ok, rows5_17_ok, rows5_18_ok, rows5_19_ok, rows5_20_ok, rows5_21_ok, rows5_22_ok, rows5_23_ok, rows5_24_ok, Bool.and_self, Bool.true_and, Bool.and_true]

end QV.RamseyZBS.Root
