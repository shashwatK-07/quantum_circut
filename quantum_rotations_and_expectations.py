import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2 as Estimator

# Use the saved default account and the least busy real QPU
service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False)
print(f"Target QPU: {backend.name}")

# State preparation: Bell state (|00> + |11>)/sqrt(2)
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

# Pauli observables (Qiskit labels are little-endian: rightmost char = qubit 0)
paulis = ["IX", "XI", "IZ", "ZI", "XX", "ZZ"]
observables = [SparsePauliOp(p) for p in paulis]

# Transpile the circuit and map the observables onto the hardware layout
isa_circuit = generate_preset_pass_manager(optimization_level=1, backend=backend).run(qc)
isa_observables = [obs.apply_layout(isa_circuit.layout) for obs in observables]

# Run with the Estimator primitive
job = Estimator(mode=backend).run([(isa_circuit, isa_observables)])
print(f"Job ID: {job.job_id()}")
expectation_values = job.result()[0].data.evs

# Plot
plt.figure(figsize=(9, 5))
plt.bar([f"⟨{p}⟩" for p in paulis], expectation_values, color="#6366f1", edgecolor="black")
plt.axhline(0, color="black", linewidth=0.8, linestyle="--")
plt.ylim(-1.1, 1.1)
plt.ylabel("Expectation Value")
plt.title(f"Measured Expectation Values on {backend.name}")
plt.grid(axis="y", linestyle=":", alpha=0.6)
plt.tight_layout()
plt.savefig("expectation_values.png", dpi=150)
plt.show()
