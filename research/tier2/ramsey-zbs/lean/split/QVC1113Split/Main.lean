import QVC1113Split.Rows0
import QVC1113Split.Rows1
import QVC1113Split.Rows2
import QVC1113Split.Rows3
import QVC1113Split.Rows4
import QVC1113Split.Rows5
import QVC1113Split.Rows6
import QVC1113Split.Rows7
import QVC1113Split.Rows8
import QVC1113Split.Corner0
import QVC1113Split.Corner1
import QVC1113Split.Corner2
import QVC1113Split.Corner3
import QVC1113Split.Corner4
import QVC1113Split.Corner5
import QVC1113Split.Corner6
import QVC1113Split.Corner7
import QVC1113Split.Corner8
import QVC1113Split.Link
import QVC1113Split.Geo
import QVC1113Split.Integral
import QVC1113Split.Power

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.C1113
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

end QV.RamseyZBS.C1113
