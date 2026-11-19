import QVRootSplit.Data

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
set_option linter.unusedSimpArgs false

namespace QV.RamseyZBS.Root
open RamseyAnalytic RamseyAnalytic.ControlGeometry

theorem geo_chain_deg : chain 0 data.degrees data.μ = true := by decide +kernel
theorem geo_chain_cells : chain 0 data.cells data.cutoff = true := by decide +kernel
theorem geo_deg_nonneg : data.degrees.all (fun d => decide (0 ≤ d.left ∧ 0 ≤ d.right)) = true := by decide +kernel
theorem geo_cells_ok : data.cells.all (fun i => decide (0 ≤ i.left ∧ i.left ≤ i.right)) = true := by decide +kernel
theorem geo_tail : data.degrees.all (fun d => decide (
    (d.slope+data.w-data.w*data.cutoff)*d.left+d.intercept ≤ 0 ∧
    (d.slope+data.w-data.w*data.cutoff)*d.right+d.intercept ≤ 0)) = true := by decide +kernel

end QV.RamseyZBS.Root
