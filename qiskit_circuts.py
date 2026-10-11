from qiskit_ibm_runtime import QiskitRuntimeService

from qiskit import QuantumCircuit
from qiskit. quantum_info import SparsePauliOp
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import EstimatorV2 as Estimator
from qiskit. transpiler import generate_preset_pass_manager

service = QiskitRuntimeService()

qc = QuantumCircuit (2)

# Add a Hadamard gate to qubit 0
qc.h(0)
# Perform a controlled -X gate on qubit 1, controlled by qubit 0
qc.cx(0, 1)
# - plot circuit - #
qc.draw("mpl")