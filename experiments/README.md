# experiments

Short spikes that answer one question before you write production code (see `CLAUDE.md` → How we work).

Rules:
1. Make one folder for each spike: `YYYY-MM-DD-<question>/`.
2. Write the question and the answer in a `README.md` in that folder.
3. Production code must never import from `experiments/`.
4. Never put real keys or client data in a spike.
5. After the spike, move only the proven part into production code, with tests.
