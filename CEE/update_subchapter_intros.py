#!/usr/bin/env python
"""Generate and apply updated subchapter intro texts."""
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CEE.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()

from CEE_Quiz.models import SubChapter

TEXTS = {}

TEXTS["Physical quantities, vectors and scalars"] = (
    "Physical quantities, vectors and scalars covers the fundamental concepts of "
    "physical quantities, measurement, SI base and derived units, dimensional analysis, "
    "significant figures, and vector operations including addition, subtraction, "
    "resolution into components, and finding resultants. These basics appear in nearly "
    "every CEE physics question because almost every calculation requires correct unit "
    "handling and dimensional consistency. Master unit conversions across different "
    "systems, the parallelogram and triangle methods for vector addition, and "
    "component resolution into perpendicular axes. CEE frequently tests your ability "
    "to distinguish between scalar and vector quantities in multi-concept problems "
    "and to apply significant figure rules in numerical answers. Pay special attention "
    "to common traps such as confusing displacement with distance or velocity with "
    "speed, as these conceptual distinctions appear in nearly every exam."
)

TEXTS["Kinematics"] = (
    "Kinematics deals with the mathematical description of motion in one and two "
    "dimensions, covering equations of motion, projectile motion, relative velocity, "
    "and the interpretation of displacement-time, velocity-time, and acceleration-time "
    "graphs. CEE frequently tests projectile motion with tricky angle and height "
    "combinations, including cases where the landing point differs from the launch "
    "point and problems involving projectiles on inclined planes. Graphical questions "
    "interpreting slope and area under kinematic graphs appear regularly and require "
    "quick thinking about what each graph feature physically represents. Build a habit "
    "of listing given values first and selecting the correct equation of motion before "
    "solving. Practise problems involving horizontal projectile motion from heights, "
    "relative velocity between two moving objects, and maximum range conditions, as "
    "these are among the most commonly tested patterns in the exam."
)

TEXTS["Dynamics"] = (
    "Dynamics explains the causes of motion through Newton's three laws, covering "
    "force analysis, free-body diagrams, momentum, impulse, conservation of momentum "
    "in elastic and inelastic collisions. CEE often frames problems involving "
    "connected bodies on inclined planes, pulley systems, and horizontal surfaces "
    "where you must correctly isolate forces acting on each body separately. "
    "Practice identifying action-reaction pairs and applying the impulse-momentum "
    "theorem to collision problems, as these are high-frequency CEE topics. Common "
    "mistakes include forgetting to account for friction, misidentifying the normal "
    "force on curved surfaces, and confusing the mass of individual bodies with the "
    "total mass of a system. Work through problems systematically by drawing free-body "
    "diagrams for each body before writing equations of motion."
)

TEXTS["Rotational dynamics"] = (
    "Rotational dynamics extends Newton's laws to rotational motion, covering torque, "
    "moment of inertia, angular momentum, rolling motion without slipping, and the "
    "relationship between linear and angular quantities. CEE frequently asks for "
    "moment of inertia of standard shapes and problems combining translational and "
    "rotational kinetic energy in rolling objects like discs, spheres, and cylinders. "
    "Focus on the parallel and perpendicular axis theorems, as these are commonly "
    "tested for calculating moments of inertia of composite shapes. Understand the "
    "relationship between torque and angular acceleration and practise problems where "
    "a force is applied at an angle to a lever arm. Conservation of angular momentum "
    "problems involving a person walking on a rotating platform or a figure skater "
    "pulling in their arms appear regularly in the exam."
)

TEXTS["Fluid statics and dynamics"] = (
    "Fluid statics and dynamics covers pressure at a depth, Pascal's law and its "
    "applications in hydraulic systems, Archimedes' principle for buoyancy, "
    "Bernoulli's principle relating pressure and velocity in flowing fluids, "
    "viscosity, surface tension, and Torricelli's theorem for fluid flow. CEE "
    "questions often combine buoyancy problems with Newton's laws or ask about "
    "practical applications of Bernoulli's principle such as aircraft lift, venturi "
    "meters, and atomisers. Pay close attention to problems involving apparent weight "
    "of submerged objects, floating bodies in layered fluids, and capillary rise due "
    "to surface tension. The excess pressure inside soap bubbles and the distinction "
    "between ideal fluid flow and real fluid behaviour with viscosity are also commonly "
    "tested topics in this subchapter."
)

TEXTS["Circular and Periodic motion"] = (
    "Circular motion covers centripetal acceleration, centripetal force, banked curves, "
    "vertical circular motion, and the conditions for a body to complete a full circle "
    "without leaving the track. Periodic motion covers simple harmonic motion, energy "
    "in oscillations, the simple pendulum, and damped oscillations. CEE questions often "
    "combine centripetal force with friction on banked roads or ask about the minimum "
    "speed at the top of a vertical loop. For SHM, practise problems involving "
    "mass-spring systems and pendulums where you must determine amplitude, frequency, "
    "and energy at various positions. The relationship between circular motion and SHM "
    "as a projection onto a diameter is a frequent conceptual question that tests deep "
    "understanding of both topics simultaneously."
)

TEXTS["Gravity"] = (
    "Gravity covers Newton's law of gravitation, gravitational field strength, "
    "gravitational potential energy, Kepler's three laws of planetary motion, and "
    "satellite motion including orbital velocity, escape velocity, and geostationary "
    "orbits. CEE questions frequently combine gravitational concepts with circular "
    "motion or ask about energy changes as a satellite moves in its elliptical orbit. "
    "Understand the relationship between Kepler's third law and Newton's gravitational "
    "law, as this connection appears in multiple-choice questions almost every year. "
    "Practise calculating how gravitational field strength and potential vary with "
    "altitude, and solve problems involving the energy required to move a mass between "
    "two points in a gravitational field. Escape velocity derivations and comparisons "
    "between planets are high-frequency exam topics."
)

TEXTS["Elasticity"] = (
    "Elasticity covers stress, strain, Hooke's law, Young's modulus, bulk modulus, "
    "shear modulus, Poisson's ratio, and the elastic potential energy stored in a "
    "deformed body. CEE questions often ask you to compare elastic moduli of different "
    "materials or calculate the extension of wires under combined loads. Focus on "
    "understanding the physical meaning of each modulus: Young's modulus relates to "
    "stretching, bulk modulus to uniform compression, and shear modulus to deformation "
    "under sideways forces. Practise problems involving composite wires made of "
    "different materials hung end to end, hollow spheres under internal pressure, and "
    "the energy stored per unit volume in a stretched wire. These problem types appear "
    "regularly and reward careful application of definitions rather than rote memorisation."
)

TEXTS["Thermal energy, heat, temperature and thermometers"] = (
    "Thermal energy, heat, temperature and thermometers covers the zeroth law of "
    "thermometry, temperature scale conversions between Celsius, Fahrenheit, and "
    "Kelvin, thermometric properties, and the construction and working of "
    "constant-volume and constant-pressure gas thermometers. The CEE often tests "
    "temperature scale conversions and the conceptual basis of thermometric "
    "equilibrium. Understand why the triple point of water is used as a standard "
    "reference point and how different types of thermometers can give slightly "
    "different readings for the same temperature due to different thermometric "
    "substances. Practise converting between absolute and relative temperature "
    "scales quickly, as these calculations often appear as part of larger "
    "thermodynamics problems where speed matters for time management."
)

TEXTS["Thermal expansion"] = (
    "Thermal expansion covers linear, superficial, and volumetric expansion of "
    "solids, expansion of liquids including the anomalous expansion of water near 4 "
    "degrees Celsius, and expansion of gases. CEE frequently asks about bimetallic "
    "strip problems, the anomalous behaviour of water and its ecological significance "
    "for aquatic life, and the construction of mercury thermometers. Practise problems "
    "involving expansion of hollow spheres, composite rods made of different materials "
    "that are riveted together, and the rise of liquid levels in glass containers when "
    "heated. Understand why water density is maximum at 4 degrees and how this prevents "
    "lakes from freezing solid from the bottom. These application-based questions "
    "connecting thermal expansion to real-world scenarios appear regularly in the exam."
)

TEXTS["Quantity of heat"] = (
    "Quantity of heat covers specific heat capacity, molar heat capacity, latent heat "
    "of fusion and vaporisation, the principle of heat exchange in calorimetry, and the "
    "concept of water equivalent. The CEE regularly tests calorimetry problems where "
    "you must apply the principle that heat lost equals heat gained when substances at "
    "different temperatures are mixed and reach thermal equilibrium. Practise problems "
    "involving phase changes where you must account for both sensible heat and latent "
    "heat in a single calculation. Common mistakes include forgetting to include the "
    "latent heat during phase transitions or mixing up the signs of heat gained and "
    "lost. Work through mixture problems systematically by listing all substances, "
    "their masses, specific heats, and initial and final temperatures before writing "
    "the heat balance equation."
)

TEXTS["Ideal gas"] = (
    "Ideal gas covers Boyle's law, Charles's law, pressure law, the combined gas "
    "equation, the ideal gas law PV equals nRT, the kinetic theory of gases, and the "
    "relationship between temperature and average kinetic energy of molecules. CEE "
    "questions often combine gas laws with thermodynamic processes or ask about the "
    "distribution of molecular speeds at different temperatures. Practise problems "
    "involving gas mixtures using Dalton's law of partial pressures, and understand "
    "how root mean square speed changes with temperature and molar mass. Common "
    "mistakes include using the wrong temperature unit in Kelvin or failing to account "
    "for the number of moles when comparing two gas samples. Master the connection "
    "between macroscopic gas properties and microscopic molecular behaviour."
)

TEXTS["First law of thermodynamics"] = (
    "First law of thermodynamics covers the conservation of energy in thermodynamic "
    "systems, internal energy, work done by gases during expansion and compression, "
    "and heat transfer in isothermal, isobaric, isochoric, and adiabatic processes. "
    "CEE frequently asks you to identify the correct process type from a PV diagram "
    "and calculate changes in internal energy, heat, and work for each process. "
    "Master the sign conventions for heat added to the system, work done by the "
    "system, and internal energy change, as getting these wrong is the most common "
    "mistake. Practise drawing and interpreting PV diagrams for cyclic processes and "
    "calculating the area enclosed by the cycle to find net work done. The molar "
    "heat capacities at constant pressure and constant volume and their ratio gamma "
    "are frequently tested concepts."
)

TEXTS["Second law of thermodynamics"] = (
    "Second law of thermodynamics covers entropy, the direction of spontaneous "
    "processes, heat engines, refrigerators, heat pumps, the Carnot cycle as an "
    "idealised reversible cycle, and the Carnot efficiency limit. The CEE often "
    "tests the Carnot efficiency formula and the relationship between entropy changes "
    "and the irreversibility of real processes. Understand the distinction between a "
    "heat engine that converts heat to work and a refrigerator that transfers heat "
    "from cold to hot using external work. Practise calculating the coefficient of "
    "performance of refrigerators and the maximum theoretical efficiency of heat "
    "engines operating between two temperature reservoirs. Know why no engine can be "
    "100 percent efficient and how this connects to the Kelvin-Planck statement."
)

TEXTS["Electric charge and electric field"] = (
    "Electric charge and electric field covers Coulomb's law, the principle of "
    "superposition for multiple charges, electric field due to point charges and "
    "continuous charge distributions, Gauss's law, and its applications to symmetric "
    "charge configurations including infinite planes, charged spheres, and long "
    "cylinders. CEE questions often combine Gauss's law with symmetry arguments to "
    "find electric fields. Practise applying Gauss's law to non-standard geometries "
    "and understand when it can and cannot be applied based on available symmetry. "
    "Common mistakes include choosing incorrect Gaussian surfaces or miscounting the "
    "enclosed charge. Work through problems involving electric field and potential due "
    "to systems of multiple point charges, as these require both conceptual "
    "understanding and careful calculation of vector quantities."
)

TEXTS["Electric field strength, potential and potential energy"] = (
    "Electric field strength, potential and potential energy covers electric potential "
    "due to point charges, equipotential surfaces, the relationship between electric "
    "field and potential gradient, and potential energy of charge configurations. The "
    "CEE regularly tests problems involving work done in moving charges between two "
    "points and the kinetic energy gained by a charge released from rest in an "
    "electric field. Focus on understanding the sign conventions for electric potential "
    "and potential energy, particularly when dealing with positive and negative charges. "
    "Practise finding the potential at a point due to a combination of charges using "
    "scalar addition (not vector addition, unlike electric field). The relationship "
    "between field lines and equipotential surfaces, always being perpendicular, is a "
    "common conceptual question."
)

TEXTS["Capacitors"] = (
    "Capacitors covers capacitance of parallel plate capacitors, series and parallel "
    "combinations, energy stored in a charged capacitor, the effect of inserting "
    "dielectric slabs, and capacitors in DC circuits with resistors. CEE questions "
    "often involve circuits where capacitors are combined with resistors in charging "
    "and discharging scenarios, or problems about inserting and removing dielectric "
    "materials partway. Practise problems involving capacitors in mixed series-parallel "
    "configurations where you must first simplify the circuit, then calculate charge "
    "and energy distribution. Understand what happens when a charged capacitor is "
    "reconnected with polarity reversed or when switches are opened and closed in "
    "sequence. These multi-step problems are among the most challenging and frequently "
    "tested topics in electrostatics."
)

TEXTS["Electrical quantities"] = (
    "Electrical quantities covers electric current as rate of flow of charge, potential "
    "difference, resistance, Ohm's law, resistivity, the effect of temperature on "
    "resistance, and the microscopic model of conduction involving drift velocity. The "
    "CEE often tests the distinction between ohmic and non-ohmic conductors and asks "
    "about the relationship between resistivity, length, and cross-sectional area. "
    "Understanding the microscopic model of current and how drift velocity relates to "
    "current and electron density will help with conceptual questions. Practise problems "
    "involving the effect of stretching a wire on its resistance, as these combine the "
    "resistance formula with geometric changes and appear regularly. Know the difference "
    "between resistance and resistivity and when each concept applies."
)

TEXTS["Electrical circuits"] = (
    "Electrical circuits covers series and parallel resistor combinations, Kirchhoff's "
    "current law and voltage law, the Wheatstone bridge for measuring unknown resistances, "
    "the potentiometer for comparing EMFs and measuring internal resistance, and the "
    "meter bridge. CEE frequently tests Kirchhoff's laws applied to multi-loop circuits "
    "and the balanced Wheatstone bridge condition where no current flows through the "
    "galvanometer. Practise problems where you must identify series-parallel combinations "
    "embedded in complex circuit diagrams, as these are common time-consuming questions "
    "that become quick with practice. Understand the principle behind the potentiometer "
    "method for comparing EMFs and measuring internal resistance of a cell, as the "
    "underlying concepts are tested in various forms each year."
)

TEXTS["Thermoelectric effect"] = (
    "The thermoelectric effect covers the Seebeck effect where a temperature difference "
    "between two junctions of dissimilar metals produces an EMF, the Peltier effect "
    "where current flow produces heating or cooling at a junction, the Thomson effect, "
    "and practical applications of thermocouples for temperature measurement. The CEE "
    "asks about neutral temperature and inversion temperature of thermocouples and the "
    "factors affecting the magnitude of thermoelectric EMF. Focus on understanding how "
    "different combinations of metals produce different Seebeck coefficients and how "
    "thermocouples are used in practice for precise temperature measurement. Know the "
    "difference between the Seebeck and Peltier effects, as confusing these two is a "
    "common mistake in the exam."
)

TEXTS["Alternating currents"] = (
    "Alternating currents covers the generation of AC, RMS and peak values, average "
    "values, AC circuits containing resistors, inductors, and capacitors separately and "
    "in combination, impedance, phase angle, resonance in series LCR circuits, and power "
    "in AC circuits including power factor. CEE questions often involve calculating "
    "impedance and phase angle for a given LCR combination and finding the resonance "
    "frequency where impedance is minimum and current is maximum. Practise problems "
    "involving series LCR circuits at resonance and understand the concept of power "
    "factor and why purely resistive loads have a power factor of one. The phasor "
    "diagram approach for adding voltages across different components is essential for "
    "solving most AC circuit problems efficiently."
)

TEXTS["Magnetic properties of materials"] = (
    "Magnetic properties of materials covers diamagnetic, paramagnetic, and "
    "ferromagnetic behaviour, the Curie temperature above which ferromagnets become "
    "paramagnetic, magnetic domains, hysteresis loops showing magnetisation versus "
    "applied field, and soft and hard magnetic materials. The CEE tests your ability "
    "to classify materials based on their magnetic behaviour and interpret hysteresis "
    "curves for practical applications. Focus on understanding why different materials "
    "respond differently to external magnetic fields at the atomic level. Practise "
    "identifying the correct type of magnetic behaviour from given descriptions of "
    "material response. Know the practical applications of soft iron in transformer "
    "cores and hard steel in permanent magnets, as these application-based questions "
    "appear regularly in the exam."
)

TEXTS["Magnetic field"] = (
    "Magnetic field covers the Biot-Savart law for calculating magnetic fields of "
    "current-carrying wires, circular coils, and solenoids, Ampere's circuital law "
    "for long solenoids and toroids, the Lorentz force on moving charges in magnetic "
    "fields, and the force between parallel current-carrying conductors. CEE questions "
    "often involve calculating magnetic fields at the centre of circular coils or along "
    "the axis of a solenoid. Master the right-hand rule applications for determining "
    "the direction of magnetic fields and forces. Practise problems involving the force "
    "on a charged particle moving at an angle to a magnetic field, as these require "
    "decomposing the velocity into parallel and perpendicular components. The definition "
    "of the ampere in terms of force between parallel wires is a frequently tested point."
)

TEXTS["Electromagnetic induction"] = (
    "Electromagnetic induction covers Faraday's laws of electromagnetic induction, "
    "Lenz's law for determining the direction of induced EMF, motional EMF in "
    "conducting rods moving through magnetic fields, self and mutual inductance, and "
    "the working principle of transformers. The CEE frequently tests problems involving "
    "motional EMF in conducting rods sliding on rails and the application of Lenz's "
    "law to predict direction of induced currents in loops entering or leaving magnetic "
    "fields. Practise problems involving transformers including energy losses due to "
    "resistance, eddy currents, hysteresis, and flux leakage. Understand the "
    "relationship between the number of turns ratio and voltage ratio for ideal "
    "transformers, as these calculations appear regularly in the exam."
)

TEXTS["Wave motion"] = (
    "Wave motion covers the classification of mechanical and electromagnetic waves, "
    "the wave equation, wave speed as a function of medium properties, superposition "
    "principle, energy transport by progressive waves, and the distinction between "
    "transverse and longitudinal waves. CEE questions often ask about the relationship "
    "between frequency, wavelength, and wave speed, and how changing the medium affects "
    "wave parameters while frequency remains constant. Understanding how wave speed "
    "depends on the tension and linear mass density of a string, or the bulk modulus "
    "and density of a fluid, will help solve many numerical problems. Practise applying "
    "the superposition principle to find the resultant displacement at a point where "
    "two waves meet, and understand how energy is distributed throughout one complete "
    "cycle of a progressive wave."
)

TEXTS["Stationary waves"] = (
    "Stationary waves covers the formation of standing waves by superposition of two "
    "identical travelling waves moving in opposite directions, nodes and antinodes, "
    "the harmonics of vibrating strings with different boundary conditions, and "
    "resonant frequencies of open and closed air columns. The CEE regularly tests the "
    "harmonics of closed pipes where only odd harmonics are present and open pipes "
    "where all harmonics are present, along with the corresponding node-antinode "
    "positions. Practise identifying the fundamental frequency and overtones for strings "
    "fixed at both ends, strings with one end free, and air columns of different "
    "lengths. Understand how the length of the air column relates to the wavelength of "
    "each harmonic, as these relationships form the basis of most exam questions in "
    "this subchapter."
)

TEXTS["Acoustic phenomena"] = (
    "Acoustic phenomena covers the Doppler effect for sound with moving source and "
    "moving observer combinations, beat frequency from superposition of slightly "
    "different frequencies, the characteristics of musical sound (loudness, pitch, "
    "quality and timbre), resonance in air columns, and ultrasound applications. The "
    "CEE frequently asks about the Doppler effect when both source and observer are "
    "moving and beat frequency calculations. Pay careful attention to sign conventions "
    "in Doppler effect problems where approaching is positive and receding is negative "
    "for both source and observer. Common mistakes include applying the formula "
    "incorrectly when the source reflects off a wall, creating a double Doppler shift. "
    "Practise problems involving superposition of sound waves from two sources to "
    "produce beats and understand the relationship between beat frequency and the "
    "individual source frequencies."
)

TEXTS["Reflection, refraction and dispersion"] = (
    "Reflection, refraction and dispersion covers Snell's law, total internal "
    "reflection and the critical angle, the lens formula and magnification, mirror "
    "formula, optical instruments, and dispersion of white light through a prism "
    "producing the visible spectrum. The CEE often tests problems involving apparent "
    "depth, lateral shift through glass slabs, and the angle of minimum deviation in "
    "a prism. Master the Cartesian sign convention for mirrors and lenses, as getting "
    "signs wrong is the most common source of errors. Practise problems involving "
    "combinations of mirrors or lenses where the image formed by one becomes the object "
    "for the next. Understand how the refractive index varies with wavelength and why "
    "violet light deviates more than red light in a prism due to different speeds in "
    "the glass medium."
)

TEXTS["Interference"] = (
    "Interference covers Young's double-slit experiment, the conditions for "
    "constructive and destructive interference based on path difference, fringe width "
    "calculation, phase difference, and thin-film interference in soap bubbles and oil "
    "films. CEE questions often ask about fringe width changes when slit separation, "
    "slit-to-screen distance, or wavelength is modified. Master the relationship "
    "between path difference and phase difference, as this is the key to solving most "
    "interference problems. Understand why the central maximum is bright and how fringe "
    "spacing changes with experimental parameters. Practise problems involving the "
    "replacement of one slit with a glass slab and the resulting fringe shift, as these "
    "combine refraction concepts with interference and appear regularly in the exam."
)

TEXTS["Diffraction and polarization"] = (
    "Diffraction and polarization covers single-slit diffraction, the conditions for "
    "maxima and minima, diffraction grating equations, resolving power, polarized light, "
    "Malus's law for intensity through polarizers, and Brewster's law for complete "
    "polarization of reflected light. The CEE tests the diffraction grating formula "
    "for finding wavelengths of light and the angle of diffraction for different orders. "
    "Focus on Brewster's law applications where reflected light is completely polarized "
    "and the relationship between the polarizing angle and refractive index. Understand "
    "how the number of slits in a grating affects the sharpness of maxima compared to "
    "Young's double-slit experiment. Practise calculating the maximum number of "
    "observable orders for a given wavelength and grating spacing."
)

TEXTS["Nuclear physics"] = (
    "Nuclear physics covers the structure of the atomic nucleus, nuclear forces, "
    "binding energy and the mass defect, Einstein's mass-energy equivalence, nuclear "
    "fission of heavy nuclei, nuclear fusion of light nuclei, and radioactive decay "
    "processes. CEE questions often involve calculating the binding energy per nucleon "
    "of a nucleus, the energy released in fission or fusion reactions, and balancing "
    "nuclear equations by conserving mass number and atomic number. Practise problems "
    "involving the mass defect and converting it to energy using E equals mc squared, "
    "as these are high-frequency exam topics. Understand the difference between fission "
    "and fusion and why fusion requires extremely high temperatures. Know the conditions "
    "for a nuclear chain reaction and the concept of critical mass."
)

TEXTS["Electron"] = (
    "The electron subtopic covers J.J. Thomson's cathode ray experiment and the "
    "discovery of the electron, Thomson's charge-to-mass ratio measurement using "
    "balanced electric and magnetic fields, and Millikan's oil drop experiment for "
    "determining the elementary charge. The CEE tests the experimental logic and "
    "conclusions of these foundational experiments that shaped modern atomic theory. "
    "Focus on understanding how Thomson balanced electric and magnetic forces to "
    "measure the e/m ratio and how Millikan determined the charge on individual oil "
    "drops by observing their terminal velocities under gravity and an applied electric "
    "field. Know the significance of each experiment in building the modern "
    "understanding of atomic structure, as conceptual questions about the implications "
    "of these discoveries appear regularly."
)

TEXTS["Photon and photoelectric effect"] = (
    "Photon and photoelectric effect covers Einstein's photon theory of light, the "
    "photoelectric equation relating maximum kinetic energy of emitted electrons to "
    "frequency, threshold frequency, work function of the metal surface, and stopping "
    "potential. The CEE frequently asks about the relationship between light intensity, "
    "frequency, and photocurrent. Understand why increasing intensity increases the "
    "number of emitted electrons but not their maximum kinetic energy, and why there is "
    "a threshold frequency below which no electrons are emitted regardless of intensity. "
    "Practise problems involving work function calculations and stopping potential "
    "measurements, as these are among the most commonly tested modern physics topics. "
    "Know the graph of stopping potential versus frequency and what its slope and "
    "intercept represent physically."
)

TEXTS["Wave particle duality and X-rays"] = (
    "Wave particle duality and X-rays covers de Broglie's hypothesis that particles "
    "have wave-like properties with wavelength inversely proportional to momentum, the "
    "Davisson-Germer experiment confirming electron diffraction, the production of "
    "X-rays in an X-ray tube, continuous and characteristic X-ray spectra, and Bragg's "
    "law for X-ray diffraction from crystal planes. CEE questions often involve de "
    "Broglie wavelength calculations for accelerated electrons and Bragg diffraction "
    "problems. Understand the relationship between accelerating voltage and the minimum "
    "wavelength of continuous X-rays. Practise calculating the de Broglie wavelength "
    "of particles at different kinetic energies and applying Bragg's law to find the "
    "interplanar spacing. Know the distinction between continuous and characteristic "
    "X-ray spectra and what each reveals about the target material."
)

TEXTS["Radioactivity"] = (
    "Radioactivity covers alpha, beta, and gamma decay processes, the law of "
    "radioactive decay, half-life, mean lifetime, activity measured in Becquerels, "
    "and the radioactive decay series from uranium to lead. The CEE regularly tests "
    "half-life calculations, the identification of decay products, and the changes in "
    "mass number and atomic number during each type of decay. Practise problems "
    "involving activity calculations where the initial activity and half-life are given "
    "and you must find the remaining activity after a certain time. Understand the "
    "difference between alpha particles (helium nuclei with high ionising power), beta "
    "particles (electrons with moderate penetrating power), and gamma rays (photons with "
    "high penetrating power). Radioactive dating problems using carbon-14 half-life "
    "also appear in the exam."
)

TEXTS["Solid and semiconductor devices"] = (
    "Solid and semiconductor devices covers energy bands in solids, the distinction "
    "between conductors, insulators, and semiconductors based on band gaps, intrinsic "
    "and extrinsic (n-type and p-type) semiconductors through doping, p-n junction "
    "diodes and their V-I characteristics, rectifier circuits, Zener diodes as voltage "
    "regulators, and transistor action as amplifiers and switches. CEE questions often "
    "involve identifying the behaviour of p-n junctions under forward and reverse bias "
    "and reading transistor characteristics. Focus on understanding how doping with "
    "pentavalent or trivalent impurities creates n-type or p-type semiconductors. "
    "Practise drawing and analysing half-wave and full-wave rectifier circuits with "
    "filter capacitors, as these practical circuit problems are high-yield exam topics."
)

TEXTS["Particle physics and recent trends"] = (
    "Particle physics and recent trends covers the classification of elementary "
    "particles into quarks (up, down, strange, charm, bottom, top) and leptons "
    "(electron, muon, tau and their neutrinos), the four fundamental forces "
    "(gravitational, electromagnetic, weak nuclear, strong nuclear), the Standard "
    "Model of particle physics, and recent developments including the Higgs boson "
    "discovery. The CEE tests basic classification of particles by spin, charge, and "
    "interaction type. Understand the distinction between fermions (matter particles "
    "with half-integer spin) and bosons (force carriers with integer spin). Know which "
    "particles interact via the strong force versus the weak force, as these distinctions "
    "form the basis of conceptual questions in the exam."
)

TEXTS["Basic Concepts in Chemistry"] = (
    "Basic Concepts in Chemistry covers the laws of chemical combination (definite "
    "proportions, multiple proportions, conservation of mass), atomic and molecular "
    "mass determination, the mole concept and Avogadro's number, empirical and "
    "molecular formula calculations, percentage composition, and equivalent weight. "
    "The CEE frequently tests mole-based calculations and the relationship between "
    "mass, moles, and number of particles. Master the mole concept as almost every "
    "numerical problem in chemistry requires converting between mass, moles, and "
    "particles as a starting step. Practise problems involving mixed samples where "
    "you must find the average atomic mass from isotopic abundances, and percentage "
    "yield calculations from limited reagent problems."
)

TEXTS["Stoichiometry"] = (
    "Stoichiometry covers quantitative relationships in chemical reactions, balancing "
    "chemical equations, identifying the limiting reagent, calculating theoretical "
    "yield and percentage yield, and concentration units including molarity, molality, "
    "and normality. CEE questions often involve determining which reactant runs out "
    "first and how much product can be formed from the given amounts. Practise problems "
    "involving simultaneous reactions where a product of one reaction becomes a reactant "
    "in another, as these multi-step stoichiometric calculations test both your "
    "balancing skills and arithmetic accuracy. Understanding the concept of equivalent "
    "weight and its application in neutralisation reactions will help with both "
    "stoichiometry and volumetric analysis questions. Master unit conversions between "
    "mass, moles, and particles as a foundation for all chemistry numericals."
)

TEXTS["Atomic Structure"] = (
    "Atomic structure covers the Bohr model of the hydrogen atom and its limitations, "
    "the quantum mechanical model with orbitals and probability distributions, quantum "
    "numbers (principal, azimuthal, magnetic, spin), the aufbau principle, Hund's rule "
    "of maximum multiplicity, the Pauli exclusion principle, and electronic "
    "configurations of elements. The CEE tests electronic configurations of elements, "
    "especially those with exceptions like chromium (3d5 4s1) and copper (3d10 4s1) "
    "where half-filled or fully-filled subshells are preferred. Practise writing "
    "configurations for transition metals, lanthanides, and actinides. Understand the "
    "relationship between quantum numbers and orbital shapes and sizes. Problems "
    "involving the calculation of the number of unpaired electrons and magnetic moment "
    "of atoms appear regularly in the exam."
)

TEXTS["Classification of Elements and Periodicity"] = (
    "Classification of elements and periodicity covers the modern periodic table "
    "organized by atomic number, periodic trends in atomic radius, ionic radius, "
    "ionisation energy, electron affinity, and electronegativity across periods and "
    "down groups. CEE questions often ask about the direction of trends and specific "
    "anomalies such as the ionisation energy dip from nitrogen to oxygen due to "
    "electron-electron repulsion in the half-filled p subshell. Focus on understanding "
    "why trends exist based on nuclear charge and electron shielding rather than just "
    "memorising the patterns. Practise explaining anomalies using electronic "
    "configuration arguments, as these conceptual questions test deeper understanding. "
    "Know the electronegativity values of common elements and how they relate to bond "
    "polarity in chemical bonding questions."
)

TEXTS["Chemical Bonding and Shape of Molecules"] = (
    "Chemical bonding and shape of molecules covers ionic bonding and lattice energy, "
    "covalent bonding and Lewis structures, metallic bonding, VSEPR theory for "
    "predicting molecular geometry and bond angles, hybridisation (sp, sp2, sp3, sp3d, "
    "sp3d2), and molecular orbital theory for diatomic molecules. The CEE frequently "
    "asks about molecular geometry and bond angles using VSEPR theory, and the magnetic "
    "properties of diatomic molecules using MOT. Practise predicting shapes and "
    "hybridisation for a wide range of molecules including those with lone pairs that "
    "affect geometry. Understand the difference between sigma and pi bonds and how "
    "multiple bonds affect molecular shape. Drawing Lewis structures correctly is the "
    "first step for most bonding questions, so practise this skill extensively."
)

TEXTS["Redox Reaction"] = (
    "Redox reaction covers the assignment of oxidation numbers in complex molecules "
    "and ions, the identification of oxidation and reduction in a reaction, balancing "
    "redox equations by the ion-electron method in acidic and basic solutions and the "
    "oxidation number method, and disproportionation reactions where the same element "
    "is simultaneously oxidised and reduced. CEE questions often involve assigning "
    "oxidation states in unusual compounds and balancing complex equations. Master both "
    "balancing methods as the exam sometimes asks which method is appropriate for a given "
    "reaction. Practise problems involving comproportionation reactions and understand "
    "the relationship between oxidation number changes and electron transfer, which "
    "connects redox concepts directly to electrochemistry."
)

TEXTS["States of Matter"] = (
    "States of Matter covers the properties of solids (crystalline and amorphous, "
    "unit cells), liquids (surface tension, viscosity, vapour pressure), and gases "
    "(gas laws, kinetic molecular theory, Maxwell-Boltzmann distribution). The van "
    "der Waals equation for real gases and the deviation of real gases from ideal "
    "behaviour near liquefaction are also tested. The CEE tests gas law calculations "
    "involving pressure, volume, and temperature changes, as well as the distinction "
    "between ideal and real gas behaviour. Practise problems involving gas mixtures "
    "and Dalton's law of partial pressures. Know the critical temperature and pressure "
    "concepts and the units conversion between Pascal, atmosphere, and mm of mercury, "
    "as quick unit conversion saves valuable time."
)

TEXTS["Chemical Equilibrium"] = (
    "Chemical equilibrium covers the equilibrium constant (Kc for concentration and Kp "
    "for partial pressures), the relationship between Kc and Kp using delta-n, Le "
    "Chatelier's principle for predicting the effect of changes in concentration, "
    "pressure, and temperature on the equilibrium position, and the extent of reaction. "
    "CEE questions often ask about the effect of changing conditions on the equilibrium "
    "position of industrial processes like the Haber process and the contact process. "
    "Practise writing equilibrium constant expressions for heterogeneous reactions where "
    "pure solids and liquids are excluded. Understand the relationship between the "
    "magnitude of K and the direction of spontaneity. Problems involving simultaneous "
    "equilibria and the common ion effect on equilibrium position appear regularly."
)

TEXTS["Volumetric Analysis"] = (
    "Volumetric analysis covers titration principles, the calculation of unknown "
    "concentrations from titration data, concentration units (molarity, normality, "
    "molality), acid-base indicators and their selection based on pH at equivalence, "
    "and acid-base titration curves showing pH changes. The CEE regularly tests the "
    "selection of appropriate indicators for different titration types and the "
    "calculation of endpoint versus equivalence point. Practise problems involving "
    "polyprotic acids where multiple equivalence points appear on the titration curve, "
    "and back titrations where an excess of standard reagent is added and the remaining "
    "amount is determined by a second titration. Understand the relationship between "
    "normality and molarity and how equivalent weight relates to the valence factor."
)

TEXTS["Ionic Equilibrium"] = (
    "Ionic Equilibrium covers the dissociation of weak acids and bases, pH calculations "
    "for strong and weak electrolytes, buffer solution preparation and pH calculation "
    "using the Henderson-Hasselbalch equation, salt hydrolysis of acidic, basic, and "
    "amphiprotic salts, and solubility product calculations for sparingly soluble "
    "salts. CEE questions often involve buffer pH calculations and predicting "
    "precipitation by comparing ionic product with solubility product. Practise problems "
    "involving the common ion effect on the solubility of sparingly soluble salts. "
    "Understand the relationship between Ka, Kb, and Kw for conjugate acid-base pairs. "
    "Problems involving the pH of salt solutions formed from weak acid-strong base or "
    "strong acid-weak base combinations appear frequently."
)

TEXTS["Chemical Kinetics"] = (
    "Chemical kinetics covers the rate of reaction, rate laws and rate constants, "
    "integrated rate equations for zero-order and first-order reactions, half-life "
    "calculations, molecularity versus order, the Arrhenius equation relating rate "
    "constant to temperature, and the effect of catalysts on activation energy. CEE "
    "questions often ask about determining the order of reaction from experimental data "
    "and the effect of doubling temperature on rate constant. Practise problems "
    "involving graphical determination of rate constants from concentration-time and "
    "rate-concentration plots. Understand the distinction between molecularity (a "
    "theoretical concept for elementary reactions) and order (experimentally determined). "
    "The Arrhenius equation and activation energy calculations from rate constants at "
    "two temperatures appear regularly in the exam."
)

TEXTS["Electrochemistry"] = (
    "Electrochemistry covers electrolytic cells and Faraday's laws of electrolysis "
    "for calculating mass deposited and volume of gas evolved, galvanic cells and cell "
    "EMF calculation from standard reduction potentials, the Nernst equation for "
    "non-standard conditions, and the electrochemical series for predicting reaction "
    "spontaneity. CEE questions often involve calculating the mass of substance "
    "deposited during electrolysis or the cell potential under non-standard conditions. "
    "Practise problems connecting the Nernst equation to equilibrium constants, where "
    "at equilibrium the cell EMF becomes zero. Understand how concentration cells work "
    "and why they produce EMF despite using the same electrode materials. The relationship "
    "between free energy change and cell EMF is also frequently tested."
)

TEXTS["Chemical Thermodynamics"] = (
    "Chemical thermodynamics covers internal energy, enthalpy, calorimetry, Hess's law "
    "for calculating enthalpy changes indirectly, standard enthalpies of formation and "
    "combustion, entropy as a measure of disorder, Gibbs free energy, and spontaneity "
    "criteria. The CEE frequently asks about enthalpy calculations using Hess's law "
    "cycles and predicting spontaneity from the signs of delta H, delta S, and delta G. "
    "Practise problems involving Born-Haber cycles for ionic compounds and the "
    "relationship between Gibbs energy and the equilibrium constant. Understand how "
    "temperature affects spontaneity when delta H and delta S have opposite signs, as "
    "these conceptual questions test whether you truly understand the Gibbs energy "
    "equation rather than just memorising it."
)

TEXTS["Nuclear Chemistry"] = (
    "Nuclear Chemistry covers radioactive decay types (alpha, beta minus, beta plus, "
    "electron capture, gamma emission), balancing nuclear reaction equations, artificial "
    "transmutation, radioisotopes and their applications in medicine (technetium-99m "
    "for imaging, cobalt-60 for cancer therapy), industry, and archaeology (carbon-14 "
    "dating). The CEE tests balancing nuclear equations, half-life calculations, and the "
    "identification of decay products in natural decay series. Focus on practical "
    "applications and understand the difference between nuclear fission (splitting heavy "
    "nuclei) and fusion (combining light nuclei) and the conditions required for each. "
    "Problems involving the energy released in nuclear reactions using the mass-energy "
    "equivalence also appear regularly in the exam."
)

TEXTS["Chemistry of Non-metals"] = (
    "Chemistry of Non-metals covers the properties, preparation, and reactions of "
    "hydrogen, oxygen, nitrogen, halogens, and their important compounds including "
    "water, ammonia, hydrogen peroxide, and various oxides. The CEE tests knowledge "
    "of industrial preparations, anomalous behaviour of first elements in each group "
    "(like nitrogen's triple bond making it less reactive than expected), and the "
    "structures of oxoacids of phosphorus and sulfur. Practise problems involving "
    "interhalogen compounds and their structures, the preparation and uses of hydrogen "
    "peroxide as both oxidising and reducing agent, and the anomalous behaviour of "
    "fluorine compared to other halogens. Know the industrial processes for ammonia "
    "and nitric acid manufacture including the conditions and catalysts used."
)

TEXTS["Chemistry of Metals"] = (
    "Chemistry of Metals covers metallurgy and extraction processes (calcination, "
    "roasting, smelting, electrolytic refining), the properties of s-block, p-block, "
    "d-block, and f-block elements, alloys and their compositions, and the lanthanoid "
    "contraction. The CEE tests knowledge of extraction methods matched to the "
    "reactivity of the metal and the properties of transition metal compounds including "
    "their coloured ions and variable oxidation states. Focus on understanding the "
    "lanthanoid contraction and its consequences for the chemistry of the third "
    "transition series. Practise matching alloys to their compositions and uses, such "
    "as brass, bronze, duralumin, and stainless steel. The焰色 reactions of s-block "
    "elements and magnetic properties of transition metal ions are commonly tested."
)

TEXTS["Bio-inorganic Chemistry"] = (
    "Bio-inorganic chemistry covers the role of metal ions in biological systems, "
    "including iron in hemoglobin (oxygen transport) and cytochromes (electron "
    "transport), magnesium in chlorophyll (photosynthesis), zinc in carbonic anhydrase "
    "and carboxypeptidase, copper in plastocyanin and ceruloplasmin, and the biological "
    "importance of sodium, potassium, and calcium ions in nerve impulse transmission "
    "and muscle contraction. CEE questions often ask about the specific metal ions "
    "present in biological molecules and the functions they serve. Understand the "
    "difference between the iron in hemoglobin which binds oxygen reversibly and the "
    "iron in cytochromes which participates in electron transfer. Know the role of "
    "essential trace elements like selenium, iodine, and fluorine in human health."
)

TEXTS["Chemical Tests"] = (
    "Chemical tests covers the systematic identification of cations using reagents "
    "like NaOH, ammonia solution, and hydrogen sulphide in acidic and basic media, "
    "the identification of anions using specific confirmatory tests (barium chloride "
    "for sulphate, silver nitrate for chloride, etc.), and the identification of gases "
    "by their characteristic properties. Flame tests for Group 1 and Group 2 metals "
    "are also covered. The CEE frequently tests your knowledge of the colour changes "
    "and precipitate colours that result from each confirmatory test. Practise organising "
    "cation identification into analytical groups based on their behaviour with reagents. "
    "Know the specific tests for chloride, sulphate, nitrate, and carbonate anions, as "
    "matching ions to their test results appears in almost every exam."
)

TEXTS["Separation Techniques"] = (
    "Separation techniques covers filtration for insoluble solids, distillation and "
    "fractional distillation for separating miscible liquids with different boiling "
    "points, crystallisation for purifying dissolved solids, chromatography (paper, "
    "thin-layer, and column) for separating mixtures of similar substances based on "
    "differential partition, and solvent extraction for separating solutes between "
    "immiscible solvents. CEE questions often ask about the appropriate separation "
    "method for specific types of mixtures and the principles underlying each technique. "
    "Focus on understanding when to use each method based on the physical properties "
    "of the components, such as solubility differences, boiling point differences, or "
    "molecular size. Paper chromatography applications in identifying plant pigments "
    "and amino acids appear regularly in the exam."
)

TEXTS["Types of Titration"] = (
    "Types of titration covers acid-base titrations with strong and weak acids and "
    "bases, redox titrations including iodometric and permanganometric methods, "
    "complexometric titrations with EDTA for determining hardness of water and metal "
    "ion concentrations, and precipitation titrations such as Mohr's method (using "
    "chromate indicator) and Volhard's method (back titration with thiocyanate). "
    "Indicator selection and endpoint detection for each type is a key topic. The CEE "
    "tests the choice of indicator based on the pH at the equivalence point. Practise "
    "calculating unknown concentrations from titration data including back titrations. "
    "Understand the principle behind iodometric titrations where liberated iodine is "
    "titrated with sodium thiosulphate, as this multi-step method is a favourite."
)

TEXTS["Manufacturing Processes"] = (
    "Manufacturing processes covers the industrial production of ammonia (Haber "
    "process), sulfuric acid (Contact process), sodium hydroxide (chlor-alkali "
    "electrolysis), sodium carbonate (Solvay process), and Portland cement. The CEE "
    "tests the conditions, catalysts, and chemical equations involved in each process. "
    "Focus on understanding the economic and chemical reasoning behind the chosen "
    "conditions, such as why the Haber process uses 450 degrees Celsius and 200 atm "
    "with an iron catalyst, and why the Contact process uses vanadium pentoxide. Know "
    "the raw materials and products of the Solvay process and how it recycles ammonia "
    "efficiently. These industrial chemistry questions test both factual knowledge and "
    "conceptual understanding of equilibrium and reaction kinetics principles."
)

TEXTS["Applications of Non-metals, Metals and Compounds"] = (
    "Applications of non-metals, metals and compounds covers the practical uses of "
    "elements and compounds in industry, agriculture, and daily life, including "
    "fertilisers (urea, ammonium sulphate, superphosphate), cleaning agents (washing "
    "soda, baking soda, soap), dental compounds, and building materials. The CEE tests "
    "specific applications such as the uses of aluminium compounds (alum, aluminium "
    "oxide as refractory material), sodium compounds (sodium carbonate in glass "
    "manufacture), and common fertilisers and their nutrient content. Practise matching "
    "compounds to their applications by creating organised tables. These memory-based "
    "questions are quick to answer if you have studied them well, and they free up time "
    "for harder problems elsewhere in the exam."
)

TEXTS["Chemistry in Service to Mankind"] = (
    "Chemistry in service to mankind covers the role of chemistry in health (medicines, "
    "antacids, antibiotics like penicillin), agriculture (fertilisers, pesticides, "
    "herbicides), food technology (preservatives, artificial flavours, colouring agents), "
    "polymers and their applications in daily life, and water treatment and purification "
    "methods (chlorination, filtration, reverse osmosis). CEE questions often focus on "
    "the chemistry behind everyday products and processes. Understand the chemical basis "
    "of water chlorination for purification, the composition and action of common "
    "antacids ( magnesium hydroxide, sodium hydrogen carbonate), and the types of "
    "polymers used in daily life. Know the differences between biodegradable and "
    "non-biodegradable polymers and their environmental impact."
)

TEXTS["General Organic Chemistry"] = (
    "General organic chemistry covers IUPAC nomenclature of organic compounds, "
    "structural isomerism (chain, position, functional group), stereoisomerism "
    "(geometric cis-trans and optical enantiomerism), reaction intermediates "
    "(carbocations, carbanions, free radicals), and electronic effects (inductive, "
    "resonance, hyperconjugation). The CEE frequently tests IUPAC naming of complex "
    "molecules and the stability order of reaction intermediates. Practise identifying "
    "the correct IUPAC name from multiple similar options and understanding how "
    "electronic effects influence the reactivity of organic molecules. Know the "
    "conditions for geometric isomerism (restricted rotation and different groups on "
    "each carbon) and optical isomerism (chirality and non-superimposable mirror "
    "images), as these foundational concepts are essential throughout organic chemistry."
)

TEXTS["Hydrocarbons"] = (
    "Hydrocarbons covers alkanes (free radical substitution with chlorine or bromine), "
    "alkenes (electrophilic addition, Markovnikov's rule, anti-Markovnikov addition "
    "with peroxide effect), alkynes (addition reactions, acidic hydrogen of terminal "
    "alkynes), their preparation methods, physical properties, and polymerisation "
    "reactions. CEE questions often test the products of addition reactions and the "
    "mechanisms involved. Practise distinguishing between Markovnikov and "
    "anti-Markovnikov addition, and understand Baeyer's reagent test (cold dilute "
    "KMnO4) and bromine water test for unsaturation. Know the preparation methods for "
    "each type of hydrocarbon and the conditions required. The distinction between "
    "addition and substitution reactions is a fundamental concept tested throughout "
    "organic chemistry questions in the exam."
)

TEXTS["Aromatic Hydrocarbons"] = (
    "Aromatic hydrocarbons covers benzene and its derivatives, the concept of "
    "aromaticity according to Huckel's rule (4n+2 pi electrons), electrophilic "
    "aromatic substitution reactions (nitration, sulphonation, halogenation, "
    "Friedel-Crafts alkylation and acylation), and the directing effects of "
    "substituents (ortho-para directors like -OH and -NH2 versus meta directors like "
    "-NO2 and -COOH). The CEE tests the products of substitution on disubstituted "
    "benzenes based on the combined directing effects of existing groups. Practise "
    "predicting the major product when two different substituents compete for directing "
    "the next incoming group. Understand why activating groups increase both rate and "
    "ortho-para selectivity, while deactivating groups decrease rate but direct meta."
)

TEXTS["Haloalkanes and Haloarenes"] = (
    "Haloalkanes and haloarenes covers alkyl and aryl halides, nucleophilic "
    "substitution reactions (SN1 unimolecular and SN2 bimolecular mechanisms), "
    "elimination reactions (E1 and E2 mechanisms), the Wurtz reaction, and Grignard "
    "reagent formation from alkyl halides. CEE frequently asks about the conditions "
    "favouring SN1 versus SN2 and E1 versus E2 mechanisms. Practise distinguishing "
    "between substitution and elimination products based on the nature of the substrate "
    "(primary favours SN2, tertiary favours SN1/E1), the nucleophile (strong base "
    "favours E2), and the solvent (polar protic favours SN1, polar aprotic favours "
    "SN2). Understanding the competition between these pathways is essential for "
    "predicting the major product in organic synthesis problems."
)

TEXTS["Alcohols and Phenols"] = (
    "Alcohols and Phenols covers preparation methods (hydration of alkenes, reduction "
    "of carbonyls, Grignard reaction), chemical reactions (oxidation to aldehydes, "
    "ketones, or carboxylic acids, dehydration to alkenes, esterification with "
    "carboxylic acids, reaction with metallic sodium), acidic character comparison "
    "(phenols more acidic than alcohols due to resonance stabilisation of phenoxide), "
    "and distinguishing tests (Lucas test, Victor Meyer test, neutral ferric chloride "
    "test for phenols). The CEE tests the Lucas test for distinguishing primary, "
    "secondary, and tertiary alcohols based on turbidity time. Understand why phenols "
    "are more acidic than alcohols and practise problems involving the oxidation "
    "products of different classes of alcohols and their reactions with sodium metal."
)

TEXTS["Ethers"] = (
    "Ethers covers the preparation of symmetrical and unsymmetrical ethers by "
    "Williamson synthesis (alkoxide plus alkyl halide), physical properties including "
    "low boiling points due to absence of hydrogen bonding, and chemical reactions "
    "including cleavage by concentrated HI and HBr. CEE questions often ask about the "
    "limitations of Williamson synthesis where it fails with tertiary alkyl halides due "
    "to competing elimination, and the products formed when unsymmetrical ethers are "
    "cleaved by acids. Practise predicting which C-O bond breaks during acid cleavage "
    "and which alkyl halide and alcohol products form. The fact that ethers are "
    "relatively unreactive and commonly used as solvents is also tested. Understand "
    "why aromatic ethers like anisole undergo electrophilic substitution rather than "
    "nucleophilic substitution on the ring."
)

TEXTS["Aldehydes and Ketones"] = (
    "Aldehydes and ketones covers preparation methods (oxidation of primary and "
    "secondary alcohols, ozonolysis of alkenes, hydration of alkynes), nucleophilic "
    "addition reactions, oxidation reactions distinguishing aldehydes from ketones "
    "(Tollen's silver mirror test, Fehling's solution, Schiff's reagent), reduction "
    "(Clemmensen reduction with Zn-Hg, Wolff-Kishner reduction with hydrazine), and "
    "named reactions including aldol condensation and Cannizzaro reaction. The CEE "
    "frequently asks about the reactivity order of carbonyl compounds and distinguishing "
    "tests between aldehydes and ketones. Practise predicting the products of "
    "nucleophilic addition and understanding why aldehydes are more reactive than "
    "ketones due to both steric hindrance and electronic effects around the carbonyl "
    "group in substituted compounds."
)

TEXTS["Carboxylic Acid and its Derivatives"] = (
    "Carboxylic acids and derivatives covers preparation methods, reactions including "
    "acid chloride formation with SOCl2, amide formation with ammonia, esterification "
    "with alcohols, and the interconversion of derivatives. The reactivity order of acyl "
    "derivatives (acid chloride > anhydride > ester > amide) and nucleophilic acyl "
    "substitution mechanisms are key topics. CEE questions often involve converting one "
    "derivative to another in a synthesis sequence or predicting the products of "
    "reactions with specific reagents. Practise understanding why acid chlorides are the "
    "most reactive and amides the least reactive. The Hell-Volhard-Zelinsky reaction "
    "for alpha-halogenation and the hydrolysis of amides back to carboxylic acids are "
    "also commonly tested."
)

TEXTS["Nitro-compounds"] = (
    "Nitro-compounds covers the preparation and reactions of nitroalkanes and "
    "nitroarenes, reduction to amines using different reducing agents (Sn/HCl, "
    "Fe/HCl, catalytic hydrogenation), and the Victor Meyer test for distinguishing "
    "isomeric primary amines derived from nitro compounds. The CEE tests the reduction "
    "products of nitro compounds under different conditions and the Victor Meyer test "
    "procedure and colour observations. Focus on the difference between reduction of "
    "nitroarenes by Sn/HCl which gives aromatic amines selectively versus catalytic "
    "hydrogenation which can reduce the ring as well. Practise the Victor Meyer test "
    "sequence and the colours produced for primary (red), secondary (blue), and "
    "tertiary (no colour change) nitro compounds."
)

TEXTS["Amines"] = (
    "Amines covers classification into primary, secondary, and tertiary amines, "
    "preparation methods (reduction of nitro compounds, amide reduction, Gabriel "
    "phthalimide synthesis for pure primary amines), chemical reactions, basicity "
    "order in gas phase versus aqueous solution, the Hinsberg test for distinguishing "
    "amine classes, diazotisation of aromatic amines at low temperature, and coupling "
    "reactions with phenols and amines to form azo dyes. The CEE tests the basicity "
    "order considering both inductive effects and solvation effects, as the order "
    "differs between gas and aqueous phases. Practise predicting the products of "
    "diazonium salt reactions with different reagents. Understand why aromatic primary "
    "amines form stable diazonium salts at 0-5 degrees Celsius while aliphatic amines "
    "do not."
)

TEXTS["Organometallic Compounds"] = (
    "Organometallic compounds covers Grignard reagents (RMgX) as the main focus, "
    "including their preparation in dry ether, reactions with water (forming alkanes), "
    "carbon dioxide (forming carboxylic acids after acidification), formaldehyde "
    "(forming primary alcohols), other aldehydes (forming secondary alcohols), ketones "
    "(forming tertiary alcohols), esters, and nitriles. The CEE tests the wide range "
    "of Grignard reactions and the products formed with different electrophilic "
    "substrates. Practise tracing the carbon chain extension that occurs in each "
    "reaction, as Grignard reagents are one of the most versatile tools for organic "
    "synthesis. Understand why Grignard reagents must be prepared and used in the "
    "absolute absence of moisture, as this practical detail is commonly tested."
)

TEXTS["Carbohydrates, lipids and minerals"] = (
    "Carbohydrates, lipids and minerals covers the classification of carbohydrates "
    "into mono-, di-, and polysaccharides, the structure and functions of lipids "
    "(fats for energy storage, phospholipids in cell membranes, steroids as hormones), "
    "and the biological roles of essential minerals like calcium (bones and teeth), "
    "phosphorus (ATP and DNA), iron (hemoglobin), and iodine (thyroid hormones). CEE "
    "questions often ask about the structural differences between glucose and fructose, "
    "the glycosidic bonds in sucrose, starch, and cellulose, and the functions of "
    "different lipid types. Practise identifying which biomolecules serve structural "
    "roles versus energy storage roles. Understand the Benedict's test and iodine test "
    "for identifying different carbohydrate types, as these practical identification "
    "questions appear frequently in the exam."
)

TEXTS["Proteins and enzymes"] = (
    "Proteins and enzymes covers amino acids and their classification (essential and "
    "non-essential), peptide bond formation, the four levels of protein structure "
    "(primary sequence, secondary alpha-helix and beta-sheet, tertiary 3D folding, "
    "quaternary multi-subunit assembly), enzyme classification by reaction type (six "
    "major classes), the lock-and-key and induced-fit models of enzyme action, and "
    "factors affecting enzyme activity including temperature, pH, substrate "
    "concentration, and inhibitors. The CEE tests enzyme specificity, the effect of "
    "competitive versus non-competitive inhibitors, and the concept of activation "
    "energy lowering. Practise understanding how denaturation by heat or extreme pH "
    "disrupts protein structure and function irreversibly. Know how enzyme-substrate "
    "complex formation works and the Michaelis-Menten kinetics basics."
)

TEXTS["Prokaryotic and eukaryotic cells"] = (
    "Prokaryotic and eukaryotic cells covers the fundamental structural differences "
    "between both cell types, including the presence or absence of a membrane-bound "
    "nucleus, organelle composition, cell wall composition (peptidoglycan in bacteria "
    "versus cellulose in plants), DNA organisation (circular versus linear), ribosome "
    "size (70S versus 80S), and modes of cell division. CEE questions often involve "
    "comparing specific features in a table format or identifying which cell type "
    "performs a given function. Practise distinguishing between plant and animal cells "
    "alongside prokaryotic cells in three-way comparisons. Understand why prokaryotic "
    "cells divide by binary fission while eukaryotic cells undergo mitosis, and know "
    "the structural basis for antibiotic selectivity between cell types."
)

TEXTS["Cell organelles"] = (
    "Cell organelles covers the structure and functions of the nucleus (nuclear "
    "envelope, nucleolus, chromatin), mitochondria (cristae, matrix, ATP synthesis by "
    "oxidative phosphorylation), chloroplasts (thylakoids, stroma, light reactions), "
    "endoplasmic reticulum (rough with ribosomes for protein synthesis, smooth for "
    "lipid synthesis), Golgi apparatus (modification and packaging), lysosomes "
    "(intracellular digestion), ribosomes (free and bound, protein synthesis), and "
    "vacuoles. The CEE frequently tests the endomembrane system and the flow of "
    "proteins through the secretory pathway from rough ER to Golgi to cell membrane. "
    "Practise matching organelles to their functions and identifying which are absent "
    "in animal versus plant cells. Understand the double-membrane structure of "
    "mitochondria and chloroplasts supporting the endosymbiotic theory."
)

TEXTS["Cell cycle and cell division"] = (
    "Cell cycle and cell division covers the stages of interphase (G1 growth, S DNA "
    "synthesis, G2 preparation for division), the phases of mitosis (prophase, "
    "metaphase, anaphase, telophase), meiosis I (reduction division with crossing "
    "over and independent assortment) and meiosis II (equational division), and the "
    "regulation of the cell cycle by checkpoints and cyclin-dependent kinases. CEE "
    "questions often ask about the differences between mitosis and meiosis, the "
    "significance of crossing over and independent assortment in generating genetic "
    "variation, and the chromosome number at each stage. Practise identifying "
    "chromosome and chromatid counts at each phase and the consequences of "
    "non-disjunction leading to aneuploidy and genetic disorders."
)

TEXTS["Introduction and classification systems"] = (
    "Introduction and classification systems covers the need for biological "
    "classification, the progression from the two-kingdom system through to the "
    "five-kingdom system (Monera, Protista, Fungi, Plantae, Animalia) proposed by "
    "Whittaker based on cell type, cell wall, nutrition mode, and body organisation, "
    "and the three-domain system (Bacteria, Archaea, Eukarya) proposed by Carl Woese "
    "based on ribosomal RNA analysis. The CEE tests the criteria used to distinguish "
    "kingdoms and the reasons each new system was developed. Understand why "
    "classification systems evolved as new organisms were discovered and why molecular "
    "data led to the three-domain system. Know the distinguishing features of each "
    "kingdom and the organisms belonging to them, as comparison questions form the "
    "basis of many exam items."
)

TEXTS["Monera and Virus"] = (
    "Monera and virus covers the characteristics of bacteria (prokaryotic cell "
    "structure, flagella for motility, cell wall with peptidoglycan, reproduction by "
    "binary fission and genetic recombination through conjugation), their economic "
    "importance (beneficial in nitrogen fixation and fermentation, harmful as "
    "pathogens), and the structure of viruses (capsid protein coat, nucleic acid "
    "genome, sometimes lipid envelope), classification, replication cycles (lytic "
    "immediate replication and lysogenic dormant integration), and viral diseases. "
    "CEE questions often ask about bacterial reproduction methods and the differences "
    "between lytic and lysogenic viral cycles. Practise distinguishing between Gram-"
    "positive and Gram-negative bacteria based on cell wall structure and understanding "
    "how bacteriophages replicate using host cell machinery."
)

TEXTS["Fungi and Lichens"] = (
    "Fungi and Lichens covers the characteristics of fungi (heterotrophic absorption, "
    "chitinous cell walls, body made of hyphae forming mycelium), their classification "
    "into Zygomycetes (bread mould Mucor), Ascomycetes (yeast, Penicillium), "
    "Basidiomycetes (mushroom, rust), and Deuteromycetes (imperfect fungi), "
    "reproduction by spores (sexual and asexual), economic importance (decomposers, "
    "fermentation, antibiotics, food, diseases), and lichens as symbiotic associations "
    "between fungi and algae or cyanobacteria. The CEE tests the structure of fungal "
    "reproductive bodies and the role of lichens as air pollution indicators. Practise "
    "identifying fungal groups based on reproductive structures and understanding the "
    "mutualistic relationship where the algal partner provides food through "
    "photosynthesis while the fungal partner provides shelter and moisture."
)

TEXTS["Algae"] = (
    "Algae covers the general characteristics (autotrophic, chlorophyll-bearing, "
    "thalloid plant body without true roots, stems, or leaves), classification into "
    "Chlorophyceae (green algae like Spirogyra, Chlamydomonas), Phaeophyceae (brown "
    "algae like Fucus, Sargassum), and Rhodophyceae (red algae like Polysiphonia) "
    "based on pigments and stored food, life cycles of Spirogyra (scalariform "
    "conjugation) and Chlamydomonas (isogamy, anisogamy, oogamy), and economic "
    "importance. The CEE often compares the life cycles of different algae and asks "
    "about the pigments and stored food in each class. Understand alternation of "
    "generations and how sexual reproduction methods become more complex from isogamy "
    "to oogamy. Know the specific features used to classify algae into the three classes."
)

TEXTS["Bryophytes"] = (
    "Bryophytes covers the characteristics of the non-vascular land plants often "
    "called the amphibians of the plant kingdom because they require water for "
    "fertilisation, classification into liverworts (Hepaticae like Marchantia), "
    "mosses (Musci like Funaria), and hornworts (Anthocerotae), the life cycle of "
    "Marchantia (thalloid gametophyte with archegoniophore and antheridiophore, "
    "dependent sporophyte), and the life cycle of Funaria (leafy gametophyte with "
    "seta and capsule). The CEE tests the dominant gametophyte generation, the "
    "structure of reproductive organs, and the dependence on water for fertilisation. "
    "Practise identifying the different parts of the Marchantia thallus and the "
    "capsule structure of Funaria, as identification questions on these organisms "
    "appear regularly."
)

TEXTS["Pteridophytes"] = (
    "Pteridophytes covers the characteristics of the first vascular cryptogams, "
    "classification into Psilopsida (Psilotum), Lycopsida (Selaginella), Sphenopsida "
    "(Equisetum), and Pteropsida (true ferns), the life cycle showing a dominant "
    "sporophyte generation, the structure of fern leaves (fronds) with sori on the "
    "underside containing sporangia, and the independent free-living gametophyte "
    "(prothallus). The CEE tests the structure of sori, why pteridophytes still "
    "require water for fertilisation despite having vascular tissue, and the "
    "evolutionary significance of being the first plants with true xylem and phloem. "
    "Know specific examples like Psilotum, Selaginella, Equisetum, and ferns, as "
    "matching organisms to their class appears in the exam regularly."
)

TEXTS["Gymnosperms"] = (
    "Gymnosperms covers the characteristics of naked-seed plants where ovules are "
    "not enclosed in an ovary, classification into Cycas, Pinus, Ginkgo, and Ephedra, "
    "the structure of male (small pollen cones) and female (large ovulate cones) "
    "reproductive structures in Pinus, the life cycle including wind pollination and "
    "fertilisation, and unique features like coralloid roots containing cyanobacteria "
    "in Cycas and ectomycorrhizal associations in Pinus. The CEE tests the "
    "differences between male and female cones in Pinus and the structure of the Cycas "
    "megasporophyll. Understand the evolutionary position of gymnosperms between "
    "pteridophytes and angiosperms. Practise comparing reproductive structures of "
    "Cycas (dioecious, motile sperm) and Pinus (monoecious, non-motile sperm)."
)

TEXTS["Angiosperms"] = (
    "Angiosperms covers the characteristics distinguishing flowering plants (vessel "
    "elements in xylem, double fertilisation, fruit formation from ovary wall), "
    "classification into monocots (one cotyledon, parallel venation, scattered "
    "vascular bundles, fibrous roots) and dicots (two cotyledons, reticulate "
    "venation, ring vascular bundles, tap root), and the life cycle including the "
    "unique process of double fertilisation forming both zygote (2n) and endosperm "
    "(3n). The CEE frequently tests monocot versus dicot differences in a comparative "
    "table format and the significance of double fertilisation as unique to "
    "angiosperms. Practise identifying monocots or dicots from anatomical features. "
    "Understand why endosperm is triploid and its nutritional role in seed development."
)

TEXTS["Economic importance of plant groups"] = (
    "Economic importance covers the useful aspects of different plant groups including "
    "food crops (rice, wheat, maize), medicinal plants, timber trees (sal, teak, "
    "sandalwood), fibre plants (cotton, jute, flax), and plants used for industrial "
    "products (rubber, oils, resins). It also covers harmful aspects including "
    "parasitic plants (Cuscuta), insectivorous plants (Nepenthes, Venus flytrap), "
    "and weeds. The CEE tests specific examples of plants matched to their economic "
    "uses and the classification of crop plants by their botanical families. Practise "
    "matching plants to their economic uses by creating organised tables grouping food "
    "plants, medicine plants, timber plants, and fibre plants. These direct recall "
    "questions appear regularly and are quick to answer with proper preparation."
)

TEXTS["Medicinal plants of Nepal"] = (
    "Medicinal plants of Nepal covers the identification, active chemical compounds, "
    "and traditional and modern medicinal uses of important plants found in Nepal "
    "including Yarsagumba (Ophiocordyceps sinensis used for vitality and endurance), "
    "Panchaunle (Dactylorhiza hatagirea used for general weakness), Timur (Zanthoxylum "
    "armatum used for dental and digestive problems), Asparagus racemosus (Shatavari "
    "for digestive health), and other plants listed in the Nepal national pharmacopoeia. "
    "CEE questions often ask about the specific medicinal uses of plants endemic to "
    "Nepal and the plant parts used. Focus on understanding which parts (root, leaf, "
    "bark, flower, fruit) are used medicinally. Know the conservation status of "
    "endangered medicinal plants and the legal framework protecting them in Nepal."
)

TEXTS["Plant tissues and vascular bundles"] = (
    "Plant tissues covers meristematic tissues (apical for primary growth, lateral "
    "for secondary growth, intercalary in grasses) and permanent tissues divided into "
    "simple tissues (parenchyma for storage and photosynthesis, collenchyma for "
    "flexible support, sclerenchyma for rigid support with thick walls) and complex "
    "tissues (xylem for water transport with tracheids and vessels, phloem for food "
    "transport with sieve tubes and companion cells). The classification of vascular "
    "bundles (open with cambium versus closed without, conjoint versus radial) is also "
    "tested. The CEE tests the functions of each tissue type and distinguishing "
    "features. Practise identifying tissue types from descriptions and distinguishing "
    "between protoxylem and metaxylem based on vessel size and wall thickening."
)

TEXTS["Anatomy of monocot and dicot root, stem and leaf"] = (
    "Anatomy of monocot and dicot root, stem and leaf covers the internal structures "
    "of each organ showing the arrangement of epidermis, cortex, endodermis with "
    "Casparian strip, pericycle, vascular bundles, and pith. Key differences include "
    "dicot root having a central stele with exarch xylem versus monocot root having "
    "a large pith, dicot stem having vascular bundles arranged in a ring versus "
    "monocot stem with scattered bundles, and dicot leaf having branched veins versus "
    "monocot leaf with parallel venation. The CEE often presents cross-section "
    "descriptions and asks you to identify the specimen. Practise the specific "
    "arrangement of tissues in each case. Understanding these patterns makes "
    "identification questions straightforward."
)

TEXTS["Genetic material - DNA and RNA"] = (
    "Genetic material covers the structure of DNA as a double helix with complementary "
    "base pairing (A-T, G-C) held by hydrogen bonds, the types of RNA (mRNA carrying "
    "code, tRNA carrying amino acids, rRNA forming ribosomes) and their roles in protein "
    "synthesis, the semi-conservative mechanism of DNA replication proven by Meselson-"
    "Stahl experiment, transcription of DNA to mRNA in the nucleus, translation of mRNA "
    "to protein at ribosomes in the cytoplasm, and the genetic code including codons "
    "and their meanings. The CEE tests the central dogma of molecular biology and the "
    "steps involved in protein synthesis. Practise problems involving codon-anticodon "
    "pairing during translation and mutations that alter the reading frame."
)

TEXTS["Mendelian Genetics and Linkage"] = (
    "Mendelian genetics covers Mendel's law of segregation (alleles separate during "
    "gamete formation) and law of independent assortment (genes on different "
    "chromosomes assort independently), monohybrid and dihybrid crosses with their "
    "expected phenotype and genotype ratios, test crosses to determine unknown "
    "genotypes, incomplete dominance (snapdragon flower colour), co-dominance (ABO "
    "blood groups), epistasis, linkage, and crossing over. CEE questions often "
    "involve predicting offspring ratios from complex crosses involving multiple gene "
    "interactions. Practise problems where you must work backwards from offspring "
    "ratios to determine parental genotypes. Understand the difference between linkage "
    "(genes on same chromosome) and independent assortment (genes on different "
    "chromosomes), as this distinction is essential for solving genetics problems."
)

TEXTS["Sex-linked Inheritance"] = (
    "Sex-linked inheritance covers X-linked dominant and recessive inheritance "
    "patterns, Y-linked (holandric) inheritance, criss-cross inheritance where a "
    "mother passes X-linked traits to sons, and common sex-linked disorders including "
    "red-green colour blindness and haemophilia A and B. The CEE frequently asks you "
    "to trace the inheritance of sex-linked traits through family pedigrees and predict "
    "the probability of affected offspring in the next generation. Practise identifying "
    "whether a trait is X-linked dominant, X-linked recessive, or Y-linked based on "
    "pedigree data. Common patterns include more males affected in X-linked recessive "
    "traits and the absence of male-to-male transmission. Understanding why males are "
    "more susceptible to X-linked recessive disorders due to their hemizygous condition "
    "is a frequently tested conceptual point."
)

TEXTS["Mutation, Polyploidy and Genetic Disorders"] = (
    "Mutation, polyploidy and genetic disorders covers types of gene mutations (point "
    "mutations including substitution and frameshift mutations), chromosomal mutations "
    "(deletion, duplication, inversion, translocation), polyploidy mechanisms in plants "
    "(autopolyploidy from genome doubling and allopolyploidy from hybridisation), and "
    "human genetic disorders (Down syndrome trisomy 21, Turner syndrome monosomy X, "
    "Klinefelter syndrome XXY). CEE questions often ask about the causes and karyotype "
    "outcomes of specific chromosomal abnormalities. Practise drawing the karyotypes "
    "for different disorders and understanding how non-disjunction during meiosis leads "
    "to aneuploidy. Know the phenotypic features of each disorder and how polyploidy "
    "contributes to speciation in plants through reproductive isolation from parents."
)

TEXTS["Water relations"] = (
    "Water relations covers water potential and its components (solute potential and "
    "pressure potential), osmosis and its types (endosmosis and exosmosis), plasmolysis "
    "and deplasmolysis in plant cells, the mechanism of ascent of sap (cohesion-tension "
    "theory and root pressure theory), transpiration and its regulation through stomatal "
    "opening and closing, and water absorption by roots through active and passive "
    "mechanisms. The CEE tests the cohesion-tension theory and the role of transpiration "
    "pull in water transport through xylem. Practise water potential calculations and "
    "understand how adding solute lowers water potential. Know the factors affecting "
    "transpiration rate (light, humidity, temperature, wind speed) and how guard cells "
    "regulate stomatal aperture."
)

TEXTS["Photosynthesis"] = (
    "Photosynthesis covers the light-dependent reactions occurring in thylakoid "
    "membranes (photolysis of water, electron transport chain through Photosystem II "
    "and Photosystem I, ATP synthesis by chemiosmosis, NADPH formation), the Calvin "
    "cycle or C3 pathway in the stroma (carbon fixation by RuBisCO, reduction, "
    "regeneration of RuBP), the C4 pathway in mesophyll and bundle sheath cells "
    "(spatial separation of initial carbon fixation), the CAM pathway for xerophytes "
    "(temporal separation), and factors affecting photosynthetic rate. The CEE tests "
    "the differences between C3 and C4 pathways and the significance of photorespiration "
    "which reduces efficiency in C3 plants. Practise tracing the electron flow from "
    "water through both photosystems to NADPH."
)

TEXTS["Respiration"] = (
    "Respiration covers aerobic and anaerobic respiration, glycolysis (the common "
    "pathway in cytoplasm converting glucose to pyruvate with net 2 ATP and 2 NADH), "
    "the link reaction (pyruvate to acetyl CoA), the Krebs cycle in mitochondrial "
    "matrix (producing NADH, FADH2, and GTP), the electron transport chain on the "
    "inner mitochondrial membrane, and oxidative phosphorylation by chemiosmosis. The "
    "CEE frequently tests the total ATP yield from complete oxidation of one glucose "
    "molecule (36 or 38 ATP). Practise tracing carbon atoms through glycolysis and "
    "the Krebs cycle. Know the differences between aerobic respiration and anaerobic "
    "respiration in plants (ethanol pathway) versus animals (lactic acid pathway), as "
    "these comparisons appear regularly."
)

TEXTS["Plant growth and seed germination"] = (
    "Plant growth and seed germination covers the three phases of plant growth (cell "
    "division in meristems, cell elongation, cell maturation and differentiation), "
    "plant hormones and their functions (auxins for apical dominance and cell elongation, "
    "gibberellins for stem elongation and seed germination, cytokinins for cell division "
    "and delay of senescence, abscisic acid for dormancy and stomatal closure, ethylene "
    "for fruit ripening and abscission), photoperiodism (short-day and long-day plants), "
    "vernalisation, and seed dormancy mechanisms. The CEE tests the roles of specific "
    "hormones and how their ratios interact to regulate plant growth. Practise matching "
    "hormones to their effects and understanding how auxin-to-cytokinin ratios determine "
    "whether roots or shoots develop in tissue culture."
)

TEXTS["Reproduction and sporogenesis in angiosperms"] = (
    "Reproduction and sporogenesis covers flower structure (sepals, petals, stamens "
    "with anthers, carpels with ovary), microsporogenesis (development of pollen grains "
    "from microspore mother cells through meiosis), megasporogenesis (development of "
    "embryo sac from megaspore mother cell producing 7-celled 8-nucleate structure), "
    "pollination mechanisms (self-pollination and cross-pollination by wind, water, "
    "insects, birds), and double fertilisation (one sperm fuses with egg forming zygote "
    "2n, the other fuses with polar nuclei forming primary endosperm nucleus 3n). The "
    "CEE tests the steps of double fertilisation and the structure of the embryo sac. "
    "Practise understanding the difference between pollination and fertilisation and "
    "the sequential developmental stages. Know how agents of pollination influence flower "
    "structure and why wind-pollinated flowers lack bright petals and fragrance."
)

TEXTS["Embryo and endosperm"] = (
    "Embryo and endosperm covers the types of endosperm development (nuclear with "
    "free-nuclear divisions, cellular with cell wall formation, and helobial "
    "intermediate), embryo development in dicots (proembryo, globular, heart-shaped, "
    "torpedo, mature cotyledonary stages) and monocots, seed structure (seed coat, "
    "embryo with cotyledons, endosperm in endospermic seeds), and the differences "
    "between endospermic (monocots like maize) and non-endospermic (dicots like pea) "
    "seeds. The CEE tests the role of the suspensor in embryo nutrition, the fate of "
    "endosperm as a food reserve, and structural differences between monocot and dicot "
    "seeds. Practise identifying seed parts from descriptions or diagrams. Understand "
    "how double fertilisation simultaneously produces both embryo and triploid endosperm."
)

TEXTS["Ecosystem ecology"] = (
    "Ecosystem ecology covers the structure of ecosystems (abiotic components like "
    "temperature, water, soil and biotic components including producers, consumers, "
    "and decomposers), food chains and food webs showing feeding relationships, "
    "ecological pyramids (energy pyramids always upright, biomass pyramids usually "
    "upright but inverted in aquatic systems, number pyramids), energy flow through "
    "trophic levels with the 10 percent transfer rule, and nutrient cycling. The CEE "
    "tests the construction and interpretation of ecological pyramids and why only "
    "about 10 percent of energy transfers between trophic levels. Practise identifying "
    "trophic levels in a given food web and understanding why this energy loss limits "
    "the number of trophic levels. The distinction between grazing and detritus food "
    "chains is also tested."
)

TEXTS["Biogeochemical cycles and ecological imbalances"] = (
    "Biogeochemical cycles covers the carbon cycle (photosynthesis, respiration, "
    "decomposition, combustion, fossil fuel burning), nitrogen cycle (nitrogen fixation "
    "by Rhizobium and Azotobacter, nitrification by Nitrosomonas and Nitrobacter, "
    "denitrification by Pseudomonas, ammonification), phosphorus cycle (no gaseous "
    "phase, mainly through rocks and water), and water cycle (evaporation, "
    "transpiration, precipitation, runoff). Human activities that disrupt these cycles "
    "and their ecological consequences are also covered. The CEE tests the key "
    "processes and organisms in each cycle. Practise matching bacteria to their roles "
    "in the nitrogen cycle and understanding how excess nitrogen fertiliser causes "
    "eutrophication in water bodies leading to oxygen depletion, algal blooms, and "
    "massive fish kills that devastate aquatic ecosystems."
)

TEXTS["Vegetation and adaptation"] = (
    "Vegetation and adaptation covers the vegetation zones of Nepal along altitudinal "
    "gradients (tropical sal and chir pine forests below 1000m, subtropical forests "
    "1000-2000m, temperate oak and rhododendron forests 2000-3000m, subalpine birch "
    "and juniper 3000-4000m, alpine meadows above 4000m) and plant adaptations to "
    "different environments: xerophytes (reduced leaves, thick cuticle, sunken "
    "stomata, deep roots), hydrophytes (air-filled aerenchyma, thin cuticle, flexible "
    "stems), and halophytes (salt-excreting glands, succulent tissues). The CEE tests "
    "your knowledge of Nepal's vegetation zones and specific adaptations. Practise "
    "matching adaptation types to plant examples and understanding why each adaptation "
    "is beneficial. Know the difference between morphological and physiological "
    "adaptations, as classification questions appear regularly."
)

TEXTS["Plant tissue culture"] = (
    "Plant tissue culture covers the principle of totipotency (the ability of a "
    "single differentiated cell to develop into a complete plant), micropropagation "
    "for rapid and disease-free plant multiplication through four stages "
    "(establishment, multiplication, rooting, acclimatisation), callus culture "
    "(undifferentiated cell mass), suspension culture, somatic embryogenesis, and "
    "applications in agriculture, horticulture, conservation of endangered species, "
    "and secondary metabolite production. The CEE tests the stages of micropropagation "
    "and the advantages of tissue culture over conventional propagation (speed, "
    "disease-free plants, year-round production). Focus on understanding totipotency "
    "and how the ratio of auxins to cytokinins in the culture medium determines "
    "whether shoots or roots develop."
)

TEXTS["Genetic engineering"] = (
    "Genetic engineering covers recombinant DNA technology, restriction enzymes "
    "(molecular scissors that cut DNA at specific palindromic sequences), vectors "
    "(plasmids, bacteriophages, cosmids) for gene transfer, gene cloning in host "
    "organisms, the polymerase chain reaction (PCR) for amplifying specific DNA "
    "sequences, gel electrophoresis for separating DNA fragments by size, and "
    "applications including transgenic organisms (Bt cotton, golden rice) and gene "
    "therapy. The CEE tests the steps involved in creating transgenic organisms and "
    "the tools used at each step. Practise understanding the role of restriction "
    "enzymes in cutting DNA and DNA ligase in joining fragments. Know the difference "
    "between cloning vectors and expression vectors."
)

TEXTS["Biofertilizers and food security"] = (
    "Biofertilizers covers Rhizobium for symbiotic nitrogen fixation in legume root "
    "nodules, Azotobacter and Clostridium for free-living nitrogen fixation, "
    "cyanobacteria (Anabaena, Nostoc) for nitrogen fixation in paddy fields and their "
    "association with Azolla fern, and mycorrhizae (fungus-root associations) for "
    "enhancing phosphorus and water absorption. The role of biological nitrogen "
    "fixation in sustainable agriculture and food security is a central theme. The CEE "
    "tests the specific benefits of each biofertilizer type and the distinction between "
    "symbiotic and free-living nitrogen fixers. Practise understanding why legumes need "
    "less nitrogen fertiliser, how mycorrhizal associations extend effective root surface "
    "area, and the advantages of biofertilizers over chemical fertilisers for long-term "
    "soil health."
)

TEXTS["Animal diversity from Protozoa to Chordata"] = (
    "Animal diversity covers the classification, body plans, and key characteristics "
    "of major animal phyla: Protozoa (unicellular), Porifera (porous body, no true "
    "tissues), Cnidaria (radial symmetry, cnidocytes), Platyhelminthes (flatworms, "
    "acoelomate), Nematoda (roundworms, pseudocoelomate), Annelida (segmented worms, "
    "true coelom), Arthropoda (jointed legs, chitinous exoskeleton, largest phylum), "
    "Mollusca (soft body, muscular foot, mantle), Echinodermata (spiny skin, water "
    "vascular system, pentaradial symmetry in adults), and Chordata (notochord, dorsal "
    "hollow nerve cord, pharyngeal slits, post-anal tail). The CEE tests distinguishing "
    "features of each phylum and evolutionary trends from simple to complex body plans. "
    "Practise comparing phyla based on coelom type, germ layers, and symmetry. Focus on "
    "why Arthropoda is the largest phylum due to jointed appendages and exoskeleton that "
    "allow adaptation to diverse habitats, and why Chordata is the most evolutionarily "
    "advanced group with vertebral column development."
)

TEXTS["Types of animal tissues"] = (
    "Types of animal tissues covers the four primary tissue types: epithelial tissue "
    "(simple squamous for diffusion, cuboidal for secretion, columnar for absorption, "
    "pseudostratified ciliated for protection; stratified squamous for protection of "
    "surfaces; glandular for secretion), connective tissue (areolar for padding, "
    "adipose for insulation and energy storage, dense regular for tendons, cartilage "
    "for flexible support, bone for rigid support, blood as fluid connective tissue), "
    "muscular tissue (smooth involuntary in organs, skeletal voluntary attached to "
    "bones, cardiac involuntary in heart with intercalated discs), and nervous tissue "
    "(neurons for impulse transmission, neuroglia for support). The CEE asks you to "
    "identify tissue types from structural descriptions and match them to functions. "
    "Practise the classification system and unique features of each subtype."
)

TEXTS["Digestive System"] = (
    "The digestive system covers the anatomy of the alimentary canal from mouth "
    "through oesophagus, stomach, small intestine (duodenum, jejunum, ileum), and "
    "large intestine to the anus. It covers digestive glands (salivary glands "
    "producing amylase, liver producing bile, pancreas producing trypsin and lipase) "
    "and the physiology of mechanical and chemical digestion at each stage. The CEE "
    "tests enzyme-substrate specificity at each digestive stage and the mechanisms of "
    "nutrient absorption through villi and microvilli. Practise matching enzymes to "
    "substrates and products. Understand the role of bile in fat emulsification (not "
    "chemical digestion) and the structural adaptations of the small intestine for "
    "maximum absorption efficiency."
)

TEXTS["Respiratory System"] = (
    "The respiratory system covers the anatomy of the respiratory tract (nasal cavity "
    "warming and filtering air, pharynx, larynx with vocal cords, trachea with C-shaped "
    "cartilage rings, branching bronchi and bronchioles, alveoli with thin squamous "
    "epithelium), the mechanics of breathing (inspiration by diaphragm contraction "
    "and external intercostal contraction, expiration by relaxation), gas exchange at "
    "alveoli through partial pressure gradients, and transport of oxygen by haemoglobin "
    "as oxyhemoglobin and carbon dioxide as bicarbonate ions. The CEE tests the oxygen-"
    "haemoglobin dissociation curve and the Bohr effect. Practise understanding how "
    "decreased pH and increased CO2 shift the curve right to facilitate oxygen release "
    "in active tissues."
)

TEXTS["Circulatory System"] = (
    "The circulatory system covers the structure of the human heart (four chambers, "
    "atrioventricular and semilunar valves, septum preventing mixing), the cardiac "
    "cycle (atrial systole, ventricular systole, joint diastole with the lub-dub "
    "sounds), blood vessels (arteries with thick elastic walls, veins with valves, "
    "capillaries with single-cell thickness for exchange), blood composition (plasma, "
    "RBCs with haemoglobin, WBCs for immunity, platelets for clotting), blood groups "
    "(ABO system with antigens and antibodies, Rh factor), and blood pressure "
    "regulation. The CEE tests the cardiac cycle phases and how valves prevent backflow. "
    "Practise tracing blood flow through the pulmonary and systemic circuits and "
    "understanding blood group inheritance and transfusion compatibility."
)

TEXTS["Excretory System"] = (
    "The excretory system covers the structure of the human kidney (cortex, medulla, "
    "pelvis, ureter, bladder, urethra), the nephron as the functional unit (renal "
    "corpusule with Bowman's capsule and glomerulus, proximal convoluted tubule, Loop "
    "of Henle with descending and ascending limbs, distal convoluted tubule, collecting "
    "duct), the three steps of urine formation (glomerular filtration, tubular "
    "reabsorption of glucose and ions, tubular secretion of wastes), and hormonal "
    "regulation by ADH (water reabsorption) and aldosterone (sodium reabsorption). "
    "The CEE tests the countercurrent mechanism in the Loop of Henle that creates "
    "the osmotic gradient. Practise understanding how dehydration triggers ADH release "
    "and how the kidney adjusts urine concentration."
)

TEXTS["Nervous System"] = (
    "The nervous system covers the structure of neurons (cell body with nucleus, "
    "dendrites receiving signals, axon conducting impulses, myelin sheath for "
    "insulation, synapse for communication), the generation and propagation of nerve "
    "impulses (resting potential at -70mV, action potential depolarisation and "
    "repolarisation through Na+ and K+ channel opening and closing), synaptic "
    "transmission (neurotransmitter release from presynaptic vesicles, binding to "
    "postsynaptic receptors), and the organisation of the central nervous system "
    "(brain regions and spinal cord) and peripheral nervous system (somatic voluntary "
    "and autonomic involuntary with sympathetic and parasympathetic divisions). The "
    "CEE tests the role of ion channels and the difference between excitatory and "
    "inhibitory synapses."
)

TEXTS["Sense Organs"] = (
    "Sense organs covers the structure and function of the human eye (cornea "
    "refracting light, iris controlling pupil size, lens focusing through accommodation, "
    "retina with rods for dim light and cones for colour vision, optic nerve), "
    "defects of vision (myopia corrected by concave lens, hypermetropia corrected by "
    "convex lens, astigmatism, presbyopia), the ear (outer pinna collecting sound, "
    "middle ear ossicles amplifying vibrations, inner ear cochlea with organ of Corti "
    "for hearing and semicircular canals for balance). The CEE tests common eye defects "
    "and corrective lens calculations using the lens formula. Practise understanding "
    "the mechanism of hearing from sound wave entry to nerve impulse generation, and "
    "how the semicircular canals detect angular acceleration for balance."
)

TEXTS["Endocrinology"] = (
    "Endocrinology covers the major endocrine glands: pituitary (master gland "
    "producing GH, TSH, ACTH, FSH, LH, prolactin), thyroid (T3 and T4 for "
    "metabolism, calcitonin lowering blood calcium), parathyroid (PTH raising blood "
    "calcium), adrenal cortex (cortisol for stress, aldosterone for salt balance) "
    "and medulla (adrenaline for fight-or-flight), pancreas (insulin lowering and "
    "glucagon raising blood sugar), and gonads (testosterone, estrogen, progesterone). "
    "The CEE tests hormone deficiencies and excesses and the disorders they cause "
    "(dwarfism from GH deficiency, goitre from iodine deficiency, diabetes mellitus "
    "from insulin deficiency, Cushing's syndrome from cortisol excess). Practise "
    "matching hormones to target organs and understanding negative feedback loops "
    "that regulate hormone secretion levels."
)

TEXTS["Reproductive System"] = (
    "The reproductive system covers male reproductive anatomy (testes producing "
    "sperm and testosterone, epididymis for sperm maturation, vas deferens, seminal "
    "vesicles and prostate contributing to semen, penis) and female reproductive "
    "anatomy (ovaries producing ova and hormones, fallopian tubes for fertilisation "
    "site, uterus for implantation, vagina), gametogenesis (spermatogenesis from "
    "puberty continuously, oogenesis from birth with periodic arrest), the hormonal "
    "control of the menstrual cycle (FSH stimulating follicle, LH triggering ovulation, "
    "estrogen and progesterone maintaining uterine lining), fertilisation, and "
    "contraception methods. The CEE tests hormonal interplay during the menstrual "
    "cycle and the stages of gamete development. Know the difference between "
    "spermatogenesis and oogenesis in terms of timing and number of functional gametes."
)

TEXTS["Origin of life"] = (
    "Origin of life covers the hypotheses on the origin of life including the "
    "Oparin-Haldane theory proposing chemical evolution in a reducing atmosphere, "
    "the Miller-Urey experiment that simulated early Earth conditions with methane, "
    "ammonia, hydrogen, and water vapour and produced amino acids and simple organic "
    "molecules, the stages of chemical evolution from simple inorganic molecules to "
    "complex organic molecules to protocells, and the RNA world hypothesis suggesting "
    "RNA preceded DNA as genetic material. The CEE asks about the products of the "
    "Miller-Urey experiment, the reducing atmosphere of early Earth, and the sequence "
    "of events leading to the first living cell. Practise understanding each stage of "
    "chemical evolution and why the absence of free oxygen facilitated organic synthesis."
)

TEXTS["Evidences of evolution"] = (
    "Evidences of evolution covers the fossil record showing progressive changes over "
    "geological time with transitional forms, homologous organs (same basic structure "
    "like the pentadactyl limb in different vertebrates indicating common ancestry), "
    "analogous organs (similar function but different origin like wings of insects and "
    "birds indicating convergent evolution), vestigial organs (reduced function remnants "
    "like human appendix, whale pelvic bones), comparative embryology (similar early "
    "development stages), and molecular evidence (DNA hybridisation, cytochrome c "
    "amino acid comparison, protein sequence analysis). The CEE tests your ability to "
    "classify specific organs and explain evolutionary significance. Practise providing "
    "examples for each evidence type and understanding why molecular evidence provides "
    "the strongest support."
)

TEXTS["Theories of evolution"] = (
    "Theories of evolution covers Lamarckism (inheritance of acquired characters "
    "through use and disuse of organs, rejected because acquired traits are not "
    "inherited), Darwinism or natural selection (variation exists, struggle for "
    "existence, survival of the fittest, differential reproduction), and Neo-Darwinism "
    "or the synthetic theory integrating Mendelian genetics with natural selection "
    "through concepts of mutation, genetic drift, gene flow, and speciation. The CEE "
    "compares predictions and limitations of different theories. Understand why "
    "Lamarckism was rejected and how the synthetic theory explains evolution at the "
    "population level through changes in allele frequency. Practise distinguishing "
    "natural selection (directional change) from genetic drift (random change, "
    "especially significant in small populations). Know the three types of natural "
    "selection: directional, stabilising, and disruptive."
)

TEXTS["Human evolution"] = (
    "Human evolution traces the ancestry of modern humans from early primates through "
    "key transitional forms: Dryopithecus and Ramapithecus (ancestral apes with "
    "semi-erect posture), Australopithecus (bipedal, small brain around 400-500cc), "
    "Homo habilis (first tool maker, brain around 650cc), Homo erectus (used fire, "
    "brain around 900cc, migrated out of Africa), Homo neanderthalensis (large brain "
    "comparable to modern humans, buried dead, robust build), to Homo sapiens sapiens "
    "(modern humans with brain around 1400cc, complex language and culture). The CEE "
    "tests the chronological order of ancestors and their distinguishing features "
    "including brain size, tool use, posture, and cultural practices. Practise placing "
    "ancestors in the correct evolutionary sequence and understanding the key transitions."
)

TEXTS["Animal Behavior"] = (
    "Animal behavior covers innate behaviour (instinctive, genetically programmed "
    "responses like web building in spiders and nest building in birds), learned "
    "behaviour (conditioning, imprinting by Konrad Lorenz, insight learning in "
    "primates), migration (seasonal movement for food, breeding, or climate), "
    "hibernation and aestivation (dormancy during extreme cold or heat to conserve "
    "energy), courtship displays and mating rituals, and social behaviour "
    "(eusociality in ants and bees with castes, dominance hierarchies in wolf packs). "
    "The CEE asks about the distinction between innate and learned behaviours and their "
    "adaptive significance. Practise classifying specific behaviours and understand "
    "the differences between habituation, classical conditioning, and operant "
    "conditioning as these learning types appear regularly."
)

TEXTS["Environmental pollution"] = (
    "Environmental pollution covers air pollution (vehicle emissions and industrial "
    "discharge producing smog, acid rain from SO2 and NOx, ozone depletion by CFCs), "
    "water pollution (eutrophication from nutrient runoff causing algal blooms, "
    "biomagnification of persistent toxins like DDT through food chains, industrial "
    "and sewage waste), soil pollution (pesticides, heavy metals, plastic waste), and "
    "noise pollution. Causes, biological effects, and control measures are covered for "
    "each type. The CEE tests causes and effects of major pollutants and control "
    "strategies. Practise matching pollutants to their effects and understanding "
    "biomagnification. Know biological indicators of water pollution (BOD levels, "
    "coliform bacteria) and air pollution (lichen absence)."
)

TEXTS["Adaptations"] = (
    "Adaptations covers structural adaptations (physical features like thick fur in "
    "polar bears, long necks in giraffes, streamlined bodies in fish and dolphins, "
    "camouflage colouring in chameleons), physiological adaptations (internal "
    "processes like counter-current heat exchange in penguin flippers, water "
    "conservation through concentrated urine in desert kangaroo rats, antifreeze "
    "proteins in polar fish), and behavioural adaptations (actions like nocturnal "
    "activity to avoid heat, migration for food and breeding, hibernation to survive "
    "winter). The CEE asks you to identify the type of adaptation and explain its "
    "advantage. Practise distinguishing between structural (visible morphological "
    "features), physiological (metabolic or chemical processes), and behavioural "
    "(actions or responses) using specific animal examples for each type."
)

TEXTS["Conservation Biology"] = (
    "Conservation biology covers biodiversity hotspots including the Western Ghats "
    "and Eastern Himalayas, endangered species and the IUCN Red List categories "
    "(extinct in wild, endangered, vulnerable, near threatened, least concern), "
    "protected areas in Nepal (Chitwan National Park for one-horned rhino and Bengal "
    "tiger, Sagarmatha National Park for snow leopard, Langtang National Park, "
    "Annapurna Conservation Area), and conservation strategies including in situ "
    "(national parks, wildlife sanctuaries, biosphere reserves) and ex situ (zoos, "
    "botanical gardens, seed banks, captive breeding programmes). The CEE tests "
    "knowledge of Nepal's protected areas and their flagship species. Practise matching "
    "species to their IUCN status and understanding the causes of biodiversity loss "
    "(habitat destruction, overexploitation, invasive species, pollution, climate change)."
)

TEXTS["Microbial diseases"] = (
    "Microbial diseases covers bacterial diseases (tuberculosis caused by Mycobacterium "
    "tuberculosis through airborne transmission, cholera by Vibrio cholerae through "
    "contaminated water, typhoid by Salmonella typhi, plague by Yersinia pestis), "
    "viral diseases (COVID-19 by SARS-CoV-2, AIDS by HIV through blood and "
    "sexual contact, dengue by Dengue virus through Aedes mosquito, rabies by "
    "Rhabdovirus through animal bites), protozoan diseases (malaria by Plasmodium "
    "through Anopheles mosquito, amoebic dysentery by Entamoeba histolytica), and "
    "fungal diseases (ringworm by Trichophyton). For each, causative agent, "
    "transmission, symptoms, and prevention are covered. The CEE often asks you to "
    "match diseases to their causative organisms and classify by pathogen type."
)

TEXTS["Immunity"] = (
    "Immunity covers innate immunity (first line physical barriers like skin and "
    "mucous membranes, second line phagocytes, natural killer cells, inflammation, "
    "complement system) and adaptive immunity (third line with B-cells producing "
    "antibodies for humoral immunity and T-cells for cell-mediated immunity). It "
    "covers antigens as immune-stimulating molecules, antibodies with their five "
    "classes (IgG, IgM, IgA, IgE, IgD), antigen-antibody reactions, and immune "
    "response including primary and secondary responses. The CEE tests the difference "
    "between humoral and cell-mediated immunity, the types of antibodies, and how "
    "memory cells provide long-lasting immunity. Understand the role of each immune "
    "cell type and the complement system in enhancing antibody effectiveness."
)

TEXTS["Vaccines"] = (
    "Vaccines covers the principles of vaccination (stimulating immune response "
    "without causing disease), types of vaccines (live attenuated like MMR and BCG, "
    "killed/inactivated like polio IPV, toxoid like tetanus, subunit like hepatitis B, "
    "and newer mRNA vaccines), the national immunisation schedule in Nepal, herd "
    "immunity thresholds, and booster doses. The CEE tests the differences between "
    "vaccine types in terms of immunity duration, number of doses needed, and "
    "suitability for immunocompromised individuals. Practise matching vaccine types "
    "to their examples and understanding why multiple doses are needed (primary and "
    "secondary immune response). Know the principle behind live attenuated vaccines "
    "providing stronger and longer-lasting immunity versus killed vaccines requiring "
    "booster doses."
)

TEXTS["Medical technology"] = (
    "Medical technology covers diagnostic imaging techniques including X-rays "
    "(using electromagnetic radiation for bone and dense tissue imaging), CT scans "
    "(computed tomography using multiple X-ray slices for 3D reconstruction), MRI "
    "(magnetic resonance imaging using magnetic fields and radio waves for soft tissue "
    "detail), ultrasound (using high-frequency sound waves for foetal imaging and organ "
    "examination), and ECG (electrocardiogram recording electrical activity of the "
    "heart). Therapeutic technologies like laser surgery and dialysis are also covered. "
    "The CEE tests the physical principle behind each technique and the clinical "
    "situations where each is most appropriate. Practise matching each technique to "
    "its underlying principle and understanding when MRI is preferred over CT scan."
)

TEXTS["Applied microbiology"] = (
    "Applied microbiology covers industrial uses of microorganisms for producing "
    "antibiotics (Penicillium producing penicillin), vaccines, enzymes (amylase, "
    "protease for detergent industry), organic acids (citric acid by Aspergillus), "
    "biofuels (ethanol by yeast fermentation), and biotechnological products "
    "(recombinant insulin by engineered E. coli). Fermentation technology and its "
    "applications in food production (bread, yogurt, cheese, beer) are also covered. "
    "The CEE tests the specific microorganism used in each industrial process. "
    "Practise matching microorganisms to their industrial products: Aspergillus "
    "niger for citric acid, Saccharomyces cerevisiae for ethanol and bread, "
    "Lactobacillus for yogurt, and Acetobacter for vinegar. These direct recall "
    "questions appear frequently and are quick to answer."
)

TEXTS["Plasmodium"] = (
    "Plasmodium covers the life cycle of the malarial parasite including both the "
    "human host phase (sporozoites entering liver, schizogony in liver cells, "
    "merozoites infecting red blood cells, erythrocytic cycle causing fever, "
    "gametocyte formation) and the mosquito vector phase (Anopheles female mosquito "
    "ingesting gametocytes, fertilisation in mosquito gut, sporozoite development in "
    "salivary glands). Species include P. vivax (benign tertian malaria) and P. "
    "falciparum (malignant tertian malaria, most dangerous). Symptoms include "
    "periodic fever, chills, sweating, anaemia, and splenomegaly. The CEE tests "
    "the complete life cycle including both phases and the reason for periodic fever "
    "patterns. Know the role of the Anopheles mosquito as vector and the liver and "
    "blood stages of the parasite."
)

TEXTS["Earthworm (Pheretima)"] = (
    "Earthworm (Pheretima) covers external morphology (segmented body with clitellum "
    "for reproduction, setae for locomotion, mouth with prostomium), and internal "
    "anatomy including the digestive system (pharynx, oesophagus, crop for storage, "
    "gizzard for grinding, intestine with typhlosole for absorption), closed "
    "circulatory system (five pairs of aortic arches, dorsal and ventral blood "
    "vessels), excretory system (segmental nephridia in each segment), nervous "
    "system (ventral nerve cord with segmental ganglia, cerebral ganglia as brain), "
    "and reproductive system (hermaphroditic with male and female organs, cross-"
    "fertilisation). The CEE tests the structure and function of each organ system. "
    "Understand why earthworms are called farmer's friends (soil aeration and "
    "enrichment) and practise the anatomy from anterior to posterior segments."
)

TEXTS["Frog (Rana)"] = (
    "Frog (Rana) covers external features (moist permeable skin for cutaneous "
    "respiration, tympanum for hearing, nictitating membrane for eye protection), "
    "skeletal system, digestive system (short intestine with villi, liver and "
    "pancreas), respiratory system (both gills in tadpoles and lungs plus cutaneous "
    "respiration in adults), three-chambered heart (two atria and one ventricle with "
    "partial separation of oxygenated and deoxygenated blood), excretory system "
    "(mesonephric kidneys, uric acid as nitrogenous waste), nervous system (brain "
    "with well-developed optic lobes), and reproductive system (males with vocal "
    "sacs and nuptial pads, females with large ovaries). The CEE tests unique "
    "features like the hepatic portal system and the differences between male and "
    "female frogs. Practise comparing frog organ systems with human systems."
)


def apply():
    updated = 0
    for s in SubChapter.objects.all():
        new_text = TEXTS.get(s.name)
        if not new_text:
            for key, val in TEXTS.items():
                if s.name.replace('\ufffd', '-').replace('\u2013', '-') == key.replace('\u2013', '-'):
                    new_text = val
                    break
        if new_text and new_text != s.intro_text:
            s.intro_text = new_text
            s.save(update_fields=["intro_text"])
            updated += 1
    print(f"Updated {updated} subchapter intro texts")
    
    # Verify word counts
    for s in SubChapter.objects.all():
        wc = len(s.intro_text.split())
        if wc < 100:
            print(f"  LOW: {s.name} = {wc} words")


if __name__ == "__main__":
    apply()
