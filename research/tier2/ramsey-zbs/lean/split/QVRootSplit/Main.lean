import QVRootSplit.Rows0
import QVRootSplit.Rows1
import QVRootSplit.Rows2
import QVRootSplit.Rows3
import QVRootSplit.Rows4
import QVRootSplit.Rows5
import QVRootSplit.Rows6
import QVRootSplit.Rows7
import QVRootSplit.Rows8
import QVRootSplit.Corner0
import QVRootSplit.Corner1
import QVRootSplit.Corner2
import QVRootSplit.Corner3
import QVRootSplit.Corner4
import QVRootSplit.Corner5
import QVRootSplit.Corner6
import QVRootSplit.Corner7
import QVRootSplit.Corner8
import QVRootSplit.Link
import QVRootSplit.Geo
import QVRootSplit.Integral
import QVRootSplit.Power

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.Root
open RamseyAnalytic RamseyAnalytic.ControlGeometry

theorem geometry_checked : ControlCertificate.GeometryChecks data := by
  refine ⟨by decide +kernel, by decide +kernel, geo_chain_deg, geo_chain_cells, geo_deg_nonneg, geo_cells_ok, ?_, geo_tail⟩
  change (cl0 ++ cl1 ++ cl2 ++ cl3 ++ cl4 ++ cl5 ++ cl6 ++ cl7 ++ cl8).all (fun i => data.degrees.all (fun d => ParametricEnvelope.cornerCheck data.w d i)) = true
  simp only [List.all_append, corner0, corner1, corner2, corner3, corner4, corner5, corner6, corner7, corner8, Bool.and_self]
theorem linkage_checked : data.degrees.all (fun d => data.tangents.any (fun t => decide (d.slope=t.m ∧ d.intercept=t.c))) = true := by
  change (dg0 ++ dg1 ++ dg2 ++ dg3 ++ dg4 ++ dg5 ++ dg6 ++ dg7 ++ dg8).all (fun d => data.tangents.any (fun t => decide (d.slope=t.m ∧ d.intercept=t.c))) = true
  simp only [List.all_append, link0, link1, link2, link3, link4, link5, link6, link7, link8, Bool.and_self]
theorem checked : ControlCertificate.Checks data := by
  refine ⟨by decide +kernel, by decide +kernel, ?_, geometry_checked, linkage_checked, integral_checked, power_checked⟩
  change (rows0 ++ rows1 ++ rows2 ++ rows3 ++ rows4 ++ rows5 ++ rows6 ++ rows7 ++ rows8).all (ControlCertificate.rowCheck data) = true
  simp only [List.all_append, rows0_checked, rows1_checked, rows2_checked, rows3_checked, rows4_checked, rows5_checked, rows6_checked, rows7_checked, rows8_checked, Bool.and_self]
theorem sound : ControlCertificate.Sound data := ControlCertificate.sound data checked
#print axioms sound
theorem cert_ok : ctl.CertOK := by
  apply PublishedControlBridge.certOK_of_parameters data ctl sound
  all_goals decide +kernel
#print axioms cert_ok

end QV.RamseyZBS.Root
