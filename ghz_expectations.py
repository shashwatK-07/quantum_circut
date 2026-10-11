import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2 as Estimator

service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False)
print(f"Target QPU: {backend.name}")

# GHZ state (|0000> + |1111>)/sqrt(2)
qc = QuantumCircuit(4)
qc.h(0)
for i in range(3):
    qc.cx(i, i + 1)

# Qiskit labels are little-endian: rightmost char = qubit 0
paulis = ["IIIZ", "IIZI", "IZII", "ZIII", "ZZZZ"]
theory = [0, 0, 0, 0, 1]
observables = [SparsePauliOp(p) for p in paulis]

isa_circuit = generate_preset_pass_manager(optimization_level=1, backend=backend).run(qc)
isa_observables = [obs.apply_layout(isa_circuit.layout) for obs in observables]

job = Estimator(mode=backend).run([(isa_circuit, isa_observables)])
print(f"Job ID: {job.job_id()}")
data = job.result()[0].data
evs, stds = data.evs, data.stds

for p, t, v, s in zip(paulis, theory, evs, stds):
    print(f"{p}: theory {t}, measured {v:.3f} +/- {s:.3f}")

# Plot measured values against theory
x = range(len(paulis))
plt.figure(figsize=(9, 5))
plt.bar(x, evs, yerr=stds, color="#6366f1", edgecolor="black", capsize=4, label="Measured")
plt.scatter(x, theory, color="#f59e0b", edgecolor="black", zorder=3, s=60, label="Theory")
plt.xticks(x, [f"⟨{p}⟩" for p in paulis])
plt.axhline(0, color="black", linewidth=0.8, linestyle="--")
plt.ylim(-1.1, 1.1)
plt.ylabel("Expectation Value")
plt.title(f"GHZ State Expectation Values on {backend.name}")
plt.grid(axis="y", linestyle=":", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig("ghz_expectation_values.png", dpi=150)
plt.show()
