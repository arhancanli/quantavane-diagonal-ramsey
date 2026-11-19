import QVRootSplit.Data

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.Root
open RamseyAnalytic RamseyAnalytic.ControlGeometry

theorem rows4_0_ok : ControlCertificate.rowCheck data rows4_0 = true := by decide +kernel
theorem rows4_1_ok : ControlCertificate.rowCheck data rows4_1 = true := by decide +kernel
theorem rows4_2_ok : ControlCertificate.rowCheck data rows4_2 = true := by decide +kernel
theorem rows4_3_ok : ControlCertificate.rowCheck data rows4_3 = true := by decide +kernel
theorem rows4_4_ok : ControlCertificate.rowCheck data rows4_4 = true := by decide +kernel
theorem rows4_5_ok : ControlCertificate.rowCheck data rows4_5 = true := by decide +kernel
theorem rows4_6_ok : ControlCertificate.rowCheck data rows4_6 = true := by decide +kernel
theorem rows4_7_ok : ControlCertificate.rowCheck data rows4_7 = true := by decide +kernel
theorem rows4_8_ok : ControlCertificate.rowCheck data rows4_8 = true := by decide +kernel
theorem rows4_9_ok : ControlCertificate.rowCheck data rows4_9 = true := by decide +kernel
theorem rows4_10_ok : ControlCertificate.rowCheck data rows4_10 = true := by decide +kernel
theorem rows4_11_ok : ControlCertificate.rowCheck data rows4_11 = true := by decide +kernel
theorem rows4_12_ok : ControlCertificate.rowCheck data rows4_12 = true := by decide +kernel
theorem rows4_13_ok : ControlCertificate.rowCheck data rows4_13 = true := by decide +kernel
theorem rows4_14_ok : ControlCertificate.rowCheck data rows4_14 = true := by decide +kernel
theorem rows4_15_ok : ControlCertificate.rowCheck data rows4_15 = true := by decide +kernel
theorem rows4_16_ok : ControlCertificate.rowCheck data rows4_16 = true := by decide +kernel
theorem rows4_17_ok : ControlCertificate.rowCheck data rows4_17 = true := by decide +kernel
theorem rows4_18_ok : ControlCertificate.rowCheck data rows4_18 = true := by decide +kernel
theorem rows4_19_ok : ControlCertificate.rowCheck data rows4_19 = true := by decide +kernel
theorem rows4_20_ok : ControlCertificate.rowCheck data rows4_20 = true := by decide +kernel
theorem rows4_21_ok : ControlCertificate.rowCheck data rows4_21 = true := by decide +kernel
theorem rows4_22_ok : ControlCertificate.rowCheck data rows4_22 = true := by decide +kernel
theorem rows4_23_ok : ControlCertificate.rowCheck data rows4_23 = true := by decide +kernel
theorem rows4_24_ok : ControlCertificate.rowCheck data rows4_24 = true := by decide +kernel
theorem rows4_checked : rows4.all (ControlCertificate.rowCheck data) = true := by
  simp only [rows4, List.all_cons, List.all_nil, rows4_0_ok, rows4_1_ok, rows4_2_ok, rows4_3_ok, rows4_4_ok, rows4_5_ok, rows4_6_ok, rows4_7_ok, rows4_8_ok, rows4_9_ok, rows4_10_ok, rows4_11_ok, rows4_12_ok, rows4_13_ok, rows4_14_ok, rows4_15_ok, rows4_16_ok, rows4_17_ok, rows4_18_ok, rows4_19_ok, rows4_20_ok, rows4_21_ok, rows4_22_ok, rows4_23_ok, rows4_24_ok, Bool.and_self, Bool.true_and, Bool.and_true]

end QV.RamseyZBS.Root
