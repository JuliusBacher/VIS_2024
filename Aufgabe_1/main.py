# main.py

import numpy as np
import model
import solver

def run_simulation():
    # Parameters
    m = 1.0      # mass (kg)
    k = 100.0     # stiffness (N/m)
    d = 0.01      # damping coefficient

    # initial conditions
    iniStates = np.array([0.0, 0.0])

    # Time parameters
    t_final = 10.0
    dt = 0.001
    num_steps = int(t_final / dt)

    # Create a model (SingleMassOscillator)
    myModel = model.SingleMassOscillator(iniStates, m, k, d)

    # Create a solver
    mySolver = solver.SolverExplicit()

    # Arrays to store time and position for plotting
    times = np.linspace(0, t_final, num_steps)
    positions = np.zeros_like(times)

    # Simulation loop
    for step in range(num_steps):
        t = step * dt
        # Store the current position for plotting
        positions[step] = myModel.get_state()[0]
        
        # Take a time step
        mySolver.step(t, model, dt)

    # Plotting the result

if __name__ == "__main__":
    run_simulation()
