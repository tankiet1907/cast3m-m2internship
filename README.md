# Thermo-Hydro-Chemical (THC) & Stochastic Modelling of Concrete at High Temperatures
## M2 Internship Research Project – 3SR Laboratory, Université Grenoble Alpes

This repository contains the numerical models, calibration scripts, and stochastic analysis frameworks developed during my Master 2 internship. The simulations are implemented using **Cast3M** and **OpenTURNS**, coupled with **Python** for automation.

---

## 1. Research Objective

Concrete structures exposed to extreme heat (e.g., fire accidents, nuclear containment) can suffer from *explosive spalling*—a violent failure driven by severe pore-pressure build-up and thermal stresses. 

While the theoretical framework covers fully coupled Thermo-Hydro-Mechanical (THM) behaviors, the primary numerical objective of this project is the implementation and stochastic assessment of a novel **Thermo-Hydro-Chemical (THC)** model. By utilizing the *effective hydration degree* ($\tilde{\Gamma}$), the model explicitly simulates the concrete's entire life cycle (from curing to the accident phase) and physically links the microstructural degradation (porosity, permeability) to the chemical dehydration of the cement paste.

---

## 2. Scientific Scope

The project encompasses the following key computational and analytical aspects:

- **THC Multiphase Formulation:** Implementation of strongly coupled thermal and hydric conservation equations with explicit chemical kinetics in Cast3M.
- **Automated Calibration:** Python-driven parameter sweeps to identify critical thermal ($C_p, \lambda$) and transport ($K_0, A_\Gamma$) parameters.
- **Experimental Validation:** Benchmarking numerical results against the reference **Kalifa et al. (2000)** high-temperature experiment.
- **Uncertainty Quantification (OpenTURNS):** 
  - Variance-based sensitivity analysis (Sobol indices) using Polynomial Chaos Expansion (PCE).
  - Reliability analysis and Probability of Failure ($P_f$) estimation using LHS and Kernel Density Estimation (KDE).
- **Spatial Heterogeneity:** Implementing spatial Random Fields for intrinsic permeability using the Turning Bands Method (`ALEA` operator) to capture localized deformation and pressure concentrations.

---

## 3. Repository Structure

The repository is organized to reflect the progression of the research, from deterministic simulation to stochastic assessment:

* `report/`  
  Contains the LaTeX source code, figures, and the final compiled PDF of the Master thesis.
* `simulation/`  
  Contains the core Cast3M (`.dgibi`) scripts for the THC multiphase model, explicitly simulating the three consecutive phases: early-age hydration, long-term drying, and the high-temperature accident.
* `calibration/`  
  Python automation scripts to perform parameter sweeps. It couples Python with Cast3M to iteratively run models and evaluate the most influential parameters (e.g., intrinsic permeability $K_0$, convective exchange coefficients).
* `validation/`  
  Post-processing scripts and experimental datasets. It extracts the calibrated Cast3M results and plots them against the Kalifa experimental data (temperature and gas-pressure histories at various depths) and previous TH models.
* `stochastic/`  
  Scripts for the probabilistic framework, combining Cast3M and OpenTURNS:
  - **Sensitivity & Reliability:** Python scripts using LHS, PCE, and KDE to compute Sobol indices and PDFs.
  - **Random Fields:** Cast3M models generating lognormal spatial random fields via the Turning Bands Method (TBM) to assess the impact of spatial heterogeneity on structural safety.

---

## 4. Software Environment

All simulations and post-processing routines are developed and tested using:

- **Cast3M** (Finite Element Analysis solver)
- **OpenTURNS** (Probabilistic and Uncertainty Quantification library)
- **Python 3** (Automation, Surrogate modeling, and Data visualization)
- **LaTeX** (Report typesetting)

---

## 5. Author

**Tan Kiet HONG**  
*M2 Geomechanics, Civil Engineering and Risks*  
*Université Grenoble Alpes*