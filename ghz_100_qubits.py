import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2 as Estimator, EstimatorOptions

n = 100

# Step 1: n-qubit GHZ state and the observables <Z_0 Z_i>, i = 1..n-1
qc = QuantumCircuit(n)
qc.h(0)
for i in range(n - 1):
    qc.cx(i, i + 1)

operators = [SparsePauliOp.from_sparse_list([("ZZ", [0, i], 1)], num_qubits=n) for i in range(1, n)]

# Step 2: transpile for a backend with enough qubits
service = QiskitRuntimeService()
backend = service.least_busy(simulator=False, operational=True, min_num_qubits=n)
print(f"Target QPU: {backend.name}")
isa_circuit = generate_preset_pass_manager(optimization_level=1, backend=backend).run(qc)
isa_operators = [op.apply_layout(isa_circuit.layout) for op in operators]

# Step 3: run with dynamical decoupling error suppression
options = EstimatorOptions()
options.resilience_level = 1
options.dynamical_decoupling.enable = True
options.dynamical_decoupling.sequence_type = "XY4"

job = Estimator(backend, options=options).run([(isa_circuit, isa_operators)])
print(f"Job ID: {job.job_id()}")

# Step 4: post-process. Normalize to the first value to show the decay with distance
values = job.result()[0].data.evs
values = [v / values[0] for v in values]

plt.plot(range(1, n), values, marker="o", label=f"{n}-qubit GHZ state")
plt.xlabel("Distance between qubits $i$")
plt.ylabel(r"$\langle Z_i Z_0 \rangle / \langle Z_1 Z_0 \rangle$")
plt.legend()
plt.savefig("ghz_100_qubits.png", dpi=150)
plt.show()
