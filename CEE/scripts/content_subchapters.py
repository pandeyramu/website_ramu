"""Authored core content for all 172 subchapters (unique per topic)."""

# helper to build a dict slug -> {slug, core: [paragraphs]}
from content_data import SUBJECTS  # noqa: F401  (not used directly; kept for doc)

# Each entry: slug -> list of unique paragraphs (the expansion engine pads to 1000+ words)
SUBCHAPTERS = [
    {'slug': 'physical-quantities-vectors-and-scalars', 'core': [
        "This topic opens the physics section by fixing the vocabulary of measurement: physical quantities, their dimensions, and the two families, vectors and scalars, into which they fall. Scalars carry magnitude only, while vectors carry magnitude and direction, and the distinction drives nearly every later topic because the exam will test which class a quantity belongs to and how the two are treated differently.",
        "The practice that pays here is dimensional analysis: writing length, mass and time exponents for each quantity, and using them to check formulas and to derive units. The CEE rewards this eye because a single dimensional slip is enough to make an answer misalign with the options, and a candidate who checks dimensions catches it before committing.",
    ]},
    {'slug': 'kinematics', 'core': [
        "Kinematics describes motion without asking what causes it: displacement, velocity and acceleration, and the equations that connect them under constant acceleration. The chapter's classic question shapes are the rise and fall of a body under gravity, where velocity vanishes at the top but acceleration does not, and the two-direction projectile motion, which the exam splits into independent horizontal and vertical problems.",
        "The single habit that protects marks is fixing a sign convention for the vertical axis at the start and writing it on the page before substituting. Projectile questions also reward separating the horizontal constant-velocity motion from the vertical constant-acceleration motion, because every projectile formula follows from those two independent statements.",
    ]},
    {'slug': 'dynamics', 'core': [
        "Dynamics explains why motion changes: Newton's three laws, the concept of force, and the practical cases of friction and connected bodies. The exam concentrates on the boundary between rest and motion, because static and kinetic friction obey different laws, and on the acceleration-sharing behaviour of connected bodies, which a free-body diagram resolves more reliably than algebra done in the head.",
        "A labelled diagram of the forces acting on each body is the discipline that prevents signed errors. Writing which quantity is the same on both sides of a string, and which quantity differs, converts most dynamics questions into a short system of two equations.",
    ]},
    {'slug': 'rotational-dynamics', 'core': [
        "Rotational dynamics recasts the linear ideas of force and motion in angular form: torque, moment of inertia, angular momentum and the kinetic energy of rotation. The exam tests the dependence of moment of inertia on the axis chosen, the conservation of angular momentum when a system changes shape, and the relations that parallel the linear equations.",
        "The recurring comparison is between linear and rotational quantities, and a small parallel table of v to omega, m to I, and F to torque is the fastest revision device. Problems about a skater drawing in arms, or a wheel gaining angular speed, follow from knowing which quantity is conserved in each situation.",
    ]},
    {'slug': 'fluid-statics-and-dynamics', 'core': [
        "Fluid statics and dynamics studies liquids and gases at rest and in motion: pressure, buoyancy, surface tension and viscosity, together with the flows described by continuity and Bernoulli's principle. The exam asks what a floating or submerged body experiences, why a liquid rises in a narrow tube, and what happens to pressure and speed along a streamline.",
        "The buoyancy questions are answered by Archimedes' principle, the capillary ones by surface tension, and the viscosity ones by the opposing force between layers at different speeds. Bernoulli's principle explains the common applications the paper favours, from the aerofoil to the venturi, and each is settled by comparing pressure where speed is high with pressure where it is low.",
    ]},
    {'slug': 'circular-and-periodic-motion', 'core': [
        "Circular and periodic motion covers motion that repeats: uniform circular motion, centripetal force, and the simple harmonic motion that underlies pendulums and oscillations. The exam distinguishes the force a body feels from the force that turns it, and it tests the relation between period, frequency and angular speed, together with the energy changes in simple harmonic motion.",
        "The recurring model is the particle moving at constant speed around a circle, whose acceleration points inward and is supplied by a real force such as tension, gravity or friction. Simple harmonic motion then appears whenever a restoring force is proportional to displacement, and its displacement-time graph answers many questions faster than its equations.",
    ]},
    {'slug': 'gravity', 'core': [
        "Gravity is the chapter of universal attraction: Newton's law of gravitation, the acceleration due to gravity and its variation with height and depth, and the motion of satellites. The exam rewards knowing how g changes as you move away from the surface or into the earth, and how orbital speed depends on the distance of the orbit rather than on the satellite's mass.",
        "The satellite questions reduce to the single statement that the gravitational force provides the centripetal force, which fixes orbital speed and period. Escape velocity and the energy of an orbit close the topic, and a compact table of height dependence and depth dependence keeps the variation of g systematic.",
    ]},
    {'slug': 'elasticity', 'core': [
        "Elasticity describes how materials deform under stress and return when the stress is removed: stress, strain and the elastic moduli, notably Young's modulus, bulk modulus and rigidity modulus. The exam tests the meaning of each modulus, the graphical behaviour of a loaded wire, and the dependence of deformation on the wire's length, area and material.",
        "The central relation is stress proportional to strain within the elastic limit, with the modulus as the constant of proportionality. Questions about extending a wire, compressing a rod or altering dimensions are answered by identifying which quantity stays fixed and which changes.",
    ]},
    {'slug': 'thermal-energy-heat-temperature-and-thermometers', 'core': [
        "This topic defines the vocabulary of the heat chapter: thermal energy, heat, temperature and thermal equilibrium, together with the instruments that measure temperature. The exam tests the distinction between heat and temperature, the meaning of equilibrium between two touching bodies, and the construction and calibration of thermometers across different scales.",
        "The comparisons the paper favours are conceptual: why a thermometer changes reading, how scales are standardised between fixed points, and what the zeroth law contributes to the idea of temperature. Precision in these definitions carries most of the marks in this first topic.",
    ]},
    {'slug': 'thermal-expansion', 'core': [
        "Thermal expansion covers the growth of solids, liquids and gases with rising temperature: linear, superficial and cubical expansion for solids, and the behaviour of liquids in vessels and of gases at constant pressure. The exam tests the three coefficients and their mutual relation, and the practical cases of gaps in rails and bridges.",
        "The questions reduce to proportionality: expansion grows with original size, temperature change and the material's coefficient. Picking the correct coefficient for the dimension involved, and remembering that a liquid's apparent expansion hides its container's expansion, prevents the standard slips.",
    ]},
    {'slug': 'quantity-of-heat', 'core': [
        "Quantity of heat deals with the energy absorbed or released as bodies heat up and change state: specific heat capacity, latent heat and the calorimetric method. The exam's central idea is that heat lost equals heat gained when bodies exchange thermal energy in an insulated container, and this single equation answers most of the topic's numeric questions.",
        "Latent heat questions add the energy absorbed in a change of state without a temperature change, and the paper regularly mixes a warm sample with a cold one, or drops a hot object into water. Keeping the energy account organised, with each term labelled by which body it belongs to, is the guarded habit.",
    ]},
    {'slug': 'ideal-gas', 'core': [
        "The ideal gas chapter connects pressure, volume, temperature and amount through the gas laws and the ideal gas equation. The exam tests Boyle's law, Charles's law and Avogadro's law, and their combination into a single equation, together with the molecular picture in which pressure arises from molecular collisions.",
        "The disciplined approach is to decide which quantities stay fixed before applying any law: constant temperature for Boyle, constant pressure for Charles, and constant volume for the pressure-temperature law. The ideal gas equation then unifies the cases, provided the temperature is in kelvin and the units are consistent.",
    ]},
    {'slug': 'first-law-of-thermodynamics', 'core': [
        "The first law of thermodynamics states that the change in a system's internal energy equals the heat added minus the work done, and it provides the accounting framework for every thermodynamic process. The exam tests the sign conventions, the special cases of isothermal, adiabatic, isobaric and isochoric processes, and the calculation of work from a pressure-volume diagram.",
        "The most dependable habits are fixing the sign of each term before writing the equation and recognising each named process from its defining condition: no temperature change, no heat flow, constant pressure or constant volume. Those identifications decide the majority of the topic's questions.",
    ]},
    {'slug': 'second-law-of-thermodynamics', 'core': [
        "The second law of thermodynamics sets the direction of natural processes: heat flows spontaneously from hot to cold, and every real process increases total entropy. The exam asks why some processes never run backwards on their own, what entropy change implies about a process, and how heat engines and refrigerators respect the law's limits.",
        "The core of the topic is the engine efficiency question: the maximum efficiency of a heat engine between two temperatures is set by the Carnot limit, and no cyclic device can convert heat wholly into work. Keeping the direction of entropy and the language of engines and refrigerators straight answers most items.",
    ]},
    {'slug': 'wave-motion', 'core': [
        "Wave motion describes energy travelling without the permanent transport of matter: wavelength, frequency, amplitude, phase and speed, and the distinction between transverse and longitudinal waves. The exam tests the wave equation relating speed to frequency and wavelength, the behaviour of waves at a boundary, and the meaning of a progressive wave travelling through a medium.",
        "The habits that pay are converting between period and frequency without error and picturing the difference between the motion of the wave and the motion of the medium's particles. The exam also favours the statement that waves transfer energy and momentum but not matter.",
    ]},
    {'slug': 'stationary-waves', 'core': [
        "Stationary waves arise when two waves of equal frequency travel in opposite directions and superpose, producing nodes and antinodes that do not move. The exam tests the formation of standing waves on strings and in pipes, the harmonics that each geometry supports, and the difference between open and closed pipes.",
        "The classic questions locate nodes and antinodes, count the modes of a stretched string or an organ pipe, and relate the fundamental frequency to length and tension. Remembering that a closed pipe holds an odd set of harmonics while an open one holds all multiples is the single most useful distinction.",
    ]},
    {'slug': 'acoustic-phenomena', 'core': [
        "Acoustic phenomena applies the ideas of waves to sound: intensity, loudness, the Doppler effect and the behaviour of sound in air. The exam tests the factors that change intensity and loudness, the reflection and absorption of sound, and the frequency shift that a moving source or observer produces.",
        "The Doppler questions reduce to one decision: whether the distance between source and observer is shrinking or growing. A shrinking gap raises the frequency and a growing one lowers it, and that direction judgement, made before any formula, answers most of the numeric items.",
    ]},
    {'slug': 'reflection-refraction-and-dispersion', 'core': [
        "This topic covers the geometric behaviour of light: reflection from mirrors, refraction across boundaries, total internal reflection and the dispersion of white light into its colours. The exam tests the laws of reflection and refraction, the conditions for total internal reflection, and the role of the prism in bending and separating light.",
        "Snell's law and the critical angle are the numeric heart, and ray diagrams drawn to scale are the fastest route to the qualitative questions. Remembering that dispersion reveals the wavelength-dependence of refractive index ties the chapter together.",
    ]},
    {'slug': 'interference', 'core': [
        "Interference describes the reinforcement and cancellation of waves that overlap coherently, and the exam pairs it with Young's double-slit experiment, which produced bright and dark fringes from two coherent sources. The topic tests the condition for constructive and destructive interference, the fringe width, and the requirement that the sources maintain a constant phase relation.",
        "The numeric questions use the path or phase difference to predict a bright or dark fringe, and the vocabulary of coherent sources and path difference is the anchor. Candidates who can state why a single source split into two gives stable fringes have understood the topic's heart.",
    ]},
    {'slug': 'diffraction-and-polarization', 'core': [
        "Diffraction and polarization describe the wave nature of light beyond straight-line travel: light bending around edges and slits, and light vibrating in a single plane after passing a polariser. The exam tests the condition for observable diffraction, the relation of the diffraction pattern to slit width, and the ways to produce and detect polarised light.",
        "The core distinctions are the conditions: sustained interference needs coherent sources and comparable slit width needs narrow apertures, while polarization requires a transverse wave. The exam rewards knowing that sound, being longitudinal, never polarises, which explains several celebrated questions.",
    ]},
    {'slug': 'electrical-quantities', 'core': [
        "This topic stabilises the vocabulary of electric circuits: current, potential difference, resistance, resistivity and their units and relations. The exam tests Ohm's law, the dependence of resistance on a wire's length, area and material, and the temperature dependence of resistance in conductors.",
        "The questions settle around the proportionality of resistance to length and its inverse relation to cross-sectional area, together with the resistivity constant that identifies the material. Combining the relations correctly, rather than recalling ten formulas, is what the exam actually checks.",
    ]},
    {'slug': 'electrical-circuits', 'core': [
        "Electrical circuits applies the electrical quantities to connected networks: series and parallel combinations, Kirchhoff's laws, and the measuring instruments of the voltmeter and ammeter. The exam tests the equivalent resistance of combined networks, the current through each branch, and the internal resistance of a cell.",
        "The disciplined method is to reduce the network one pair at a time, marking which combination is simplified before moving on. The potentiometer and the balanced wheatstone bridge reward understanding of why each is used, and the exam regularly checks that a voltmeter has high resistance and an ammeter low resistance.",
    ]},
    {'slug': 'thermoelectric-effect', 'core': [
        "The thermoelectric effect covers the conversion between heat and electricity at the junction of two different metals: the Seebeck effect, the Peltier effect and thermocouples as thermometers. The exam tests which effect produces which outcome, the dependence of thermoelectric emf on temperature difference, and the practical use of a thermocouple for measuring temperature.",
        "The distinctions between the three effects, and the direction of the current and heat flow in each, form the chapter's recall core. Associating each effect with its instrument-purpose pair makes the questions mechanical.",
    ]},
    {'slug': 'alternating-currents', 'core': [
        "Alternating currents describes current and voltage that reverse direction periodically: peak and rms values, phase, and the behaviour of resistors, capacitors and inductors in AC circuits. The exam tests why rms values are defined, the phase relations each component introduces, and where the real power in an AC circuit is dissipated.",
        "The central facts are the root-mean-square relation, the capacitor that leads the current and the inductor that lags it, and the power formula that uses the power factor. Those three anchors answer nearly every question in the topic.",
    ]},
    {'slug': 'magnetic-properties-of-materials', 'core': [
        "Magnetic properties of materials classifies substances by their response to a magnetic field: diamagnetic, paramagnetic and ferromagnetic behaviour, together with the concepts of permeability, susceptibility and domains. The exam tests which materials are attracted, weakly repelled or strongly magnetised, and explains the behaviour through electron structure and domain alignment.",
        "The topic answers are differences: ferromagnetic materials retain magnetisation and align domains, paramagnetic ones align weakly, and diamagnetic ones oppose the field. Matching each class to its susceptibility sign and its classic example resolves most items.",
    ]},
    {'slug': 'magnetic-field', 'core': [
        "The magnetic field describes the region around magnets and currents where forces act: field lines, the force on a moving charge and on a current-carrying wire, and the fields created by straight wires, loops and solenoids. The exam tests the direction of the force, the right-hand rules that assign it, and the dependence of the field magnitude on current and distance.",
        "The habit that protects marks is drawing the field lines and the current direction before applying a rule. The exam also rewards knowing that the force on a charge moving parallel to the field is zero, which quietly resolves curved-path questions.",
    ]},
    {'slug': 'electromagnetic-induction', 'core': [
        "Electromagnetic induction describes the generation of emf by changing magnetic flux: Faraday's law, Lenz's law and the practical devices that depend on them. The exam tests the factors that increase the induced emf, the direction of the induced current, and the role of flux change in generators and transformers.",
        "The core statements are that emf equals the rate of change of flux and that the induced current opposes the change that created it. Applying Lenz's law before any calculation fixes the direction, and the topic rewards describing each device as an emf induced by a flux change.",
    ]},
    {'slug': 'electric-charge-and-electric-field', 'core': [
        "This topic introduces the language of electrostatics: charge, its conservation and quantization, the force between charges, and the electric field as force per unit charge. The exam tests Coulomb's law, the direction and strength of fields from single and multiple charges, and the drawing of field lines.",
        "The numeric questions combine forces vectorially, so sketching the directions is the habit that pays. The exam also rewards the vocabulary: like charges repel, field lines leave positive and enter negative charges, and the field is the same everywhere between parallel plates.",
    ]},
    {'slug': 'electric-field-strength-potential-and-potential-energy', 'core': [
        "This topic connects force and potential in electrostatics: electric field strength as the gradient of potential, the potential at a point, and the potential energy of a charge in a field. The exam tests the relation between field and potential, the work done in moving a charge, and the behaviour of charges at equipotential surfaces.",
        "The anchor ideas are that potential is work per unit charge and that no work is done moving along an equipotential surface. Questions about the field between plates and the energy of an accelerated charge follow directly from these two statements.",
    ]},
    {'slug': 'capacitors', 'core': [
        "Capacitors store charge and energy: capacitance, the parallel-plate capacitor, series and parallel combinations, and the effect of a dielectric between the plates. The exam tests what changes when a dielectric is inserted, separately for a battery-connected capacitor and an isolated one, and how combinations are reduced.",
        "The decisive distinction is between constant voltage and constant charge. With the battery connected the voltage stays fixed and the stored energy changes; when isolated the charge stays fixed. Keeping those two cases separate answers the majority of the topic's questions.",
    ]},
    {'slug': 'nuclear-physics', 'core': [
        "Nuclear physics studies the nucleus: protons and neutrons, the forces that bind them, and the energy represented by the mass defect. The exam tests the binding energy curve, the most stable nuclei, and the meaning of nuclear fission and fusion, with the mass-energy relation as the quantitative core.",
        "The binding energy per nucleon curve is the chapter's map: nuclei near iron are most stable, fission releases energy for the heavy end, and fusion releases it for the light end. Reading that graph, rather than reciting facts, answers the conceptual questions.",
    ]},
    {'slug': 'electron', 'core': [
        "The electron topic covers the discovery and behaviour of the electron across atomic and solid-state contexts: its charge and mass, its role in the atom, and its behaviour in conductors, semiconductors and the effect known as thermionic emission. The exam tests how the electron was identified and how its behaviour explains electrical and electronic phenomena.",
        "The questions reward linking every macroscopic electrical effect to the movement of electrons, and distinguishing conductors, insulators and semiconductors by their electron behaviour. The historical experiments and their conclusions are favourite recall items.",
    ]},
    {'slug': 'photon-and-photoelectric-effect', 'core': [
        "The photon and the photoelectric effect introduce the quantum view of light: energy delivered in discrete packets, the work function, threshold frequency and the emission of electrons from a metal surface. The exam tests the dependence of electron emission on frequency rather than intensity, the stopping potential, and the energy balance of the emitted electrons.",
        "The idea that a photon below the threshold frequency fails to eject an electron whatever the intensity is the topic's signature fact. The exam usually graphs kinetic energy of emitted electrons against photon frequency, and the slope and intercept of that line carry both the answers and the physics.",
    ]},
    {'slug': 'wave-particle-duality-and-x-rays', 'core': [
        "Wave-particle duality and X-rays together show the two natures of matter and energy: waves behaving as particles and particles behaving as waves, and the production of X-rays by fast electrons striking a target. The exam tests the de Broglie relation, the conditions for turning particle motion into wave language, and the continuous and characteristic X-ray spectra.",
        "The de Broglie wavelength connects momentum to wavelength, and the exam rewards knowing that the wave nature becomes detectable only for tiny masses. X-ray questions reduce to the minimum wavelength set by the accelerating voltage and the origin of the characteristic lines.",
    ]},
    {'slug': 'radioactivity', 'core': [
        "Radioactivity describes unstable nuclei emitting radiation: the alpha, beta and gamma forms, their penetrating powers, and the exponential decay governed by half-life. The exam tests the properties that distinguish the three radiations, the calculation of remaining quantities after a number of half-lives, and the safety and application of radioactive materials.",
        "The solving habit is to count half-lives rather than to use the exponent formula directly in most cases, which avoids arithmetic slips. Distinguishing the three radiations by charge, mass and penetration is the topic's recall backbone.",
    ]},
    {'slug': 'solid-and-semiconductor-devices', 'core': [
        "Solid and semiconductor devices applies the physics of electrons in solids to practical components: intrinsic and doped semiconductors, p-n junctions, and the diodes and rectifiers built from them. The exam tests the difference between n-type and p-type materials, forward and reverse bias, and the half and full wave rectification performed by diodes.",
        "The anchor facts are the majority carriers in each doped material and the behaviour of the junction under bias. The exam rewards the vocabulary of depletion region, and knowing that a diode conducts in forward bias and blocks in reverse bias.",
    ]},
    {'slug': 'particle-physics-and-recent-trends', 'core': [
        "Particle physics and recent trends surveys the fundamental constituents of matter, the four fundamental forces, and the discoveries that extended physics in recent decades. The exam tests the classification of particles into leptons, hadrons, baryons and mesons, the mediators of the forces, and the narrative of accelerators and discoveries.",
        "The questions reward a clean table of particles and the force each family of particles feels. Recent-trends items test the vocabulary of the discoveries themselves, so revision should name each discovery, its year and its significance.",
    ]},
    {'slug': 'basic-concepts-in-chemistry', 'core': [
        "This topic defines the counting language of chemistry: the mole, atomic and molecular mass, and the composition of compounds expressed in mass and percentage. The exam tests the mole as a counting unit, the conversion between mass, moles and particles, and the meaning of empirical and molecular formulas.",
        "The guard that protects marks is writing the unit with every value and converting between gram and mole through the molar mass without skipping a line. Percentage composition and the route from percentages to an empirical formula are the recurring numeric patterns.",
    ]},
    {'slug': 'stoichiometry', 'core': [
        "Stoichiometry carries the arithmetic of reacting quantities: balanced equations, mole ratios and the calculation of products or reactants, including the limiting reagent. The exam tests the ability to balance an equation, read its ratios, and scale the quantities, with the moles-of-each reacting substance traced through the reaction.",
        "The methodical habit is to convert to moles first, apply the equation's ratio, and convert back to the requested unit, and to check which substance runs out first in a two-reactant problem. Every stoichiometry question reduces to that sequence regardless of how it is worded.",
    ]},
    {'slug': 'atomic-structure', 'core': [
        "Atomic structure describes the arrangement of electrons around the nucleus: energy levels, orbitals, quantum numbers, and the rules by which electrons fill them. The exam tests each quantum number's meaning, the shape and order of orbitals, and the electron configurations that follow the aufbau principle.",
        "The exam rewards writing the configuration for an element systematically and knowing which configuration characterises which block of the periodic table. The vocabulary that matters is the pair of quantum numbers that fix an orbital's energy and shape.",
    ]},
    {'slug': 'classification-of-elements-and-periodicity', 'core': [
        "Classification of elements and periodicity organises the periodic table and the trends that repeat across it: atomic radius, ionisation energy, electronegativity and the metallic character of the elements. The exam compares elements across periods and groups and asks for the reason behind each trend.",
        "The periodic table is the topic's complete tool, and the exam rewards explaining each trend through effective nuclear charge and shell number. Committing the direction of each trend, and the cause, converts recall questions into reasoning questions.",
    ]},
    {'slug': 'chemical-bonding-and-shape-of-molecules', 'core': [
        "Chemical bonding and the shape of molecules explains how atoms join: ionic, covalent, coordinate and metallic bonds, and the molecular shapes predicted by VSEPR theory. The exam tests the conditions that favour each bond type, the hybridisation around a central atom, and the reasoning that assigns a molecule its shape.",
        "The exam repeatedly asks why a molecule is bent, trigonal planar or tetrahedral, which is answered by counting bonding pairs and lone pairs around the central atom. Matching hybridisation to geometry, and geometry to the lone-pair count, is the chapter's central skill.",
    ]},
    {'slug': 'redox-reaction', 'core': [
        "Redox reaction treats the transfer of electrons between species: oxidation and reduction, the balancing of half reactions, and the changes in oxidation numbers that identify what is oxidised or reduced. The exam tests assigning oxidation numbers, identifying the oxidising and reducing agents, and balancing equations in acidic and basic media.",
        "The habit that anchors the topic is tracking oxidation numbers first, because the definitions of oxidised, reduced, oxidant and reductant all follow from them. Balancing proceeds most reliably by separating the two half reactions and combining them.",
    ]},
    {'slug': 'states-of-matter', 'core': [
        "States of matter covers the solid, liquid and gaseous states and the transitions between them: the gas laws, intermolecular forces, and the properties that distinguish real from ideal behaviour. The exam tests the kinetic interpretation of gases, the factors affecting the state, and where real gases deviate from ideal ones.",
        "The anchor ideas are the constant molecular motion in gases, the stronger attractions in liquids, and the regular arrangement in solids. Questions about pressure, temperature and volume reduce to the gas equation when the conditions are stated clearly.",
    ]},
    {'slug': 'chemical-equilibrium', 'core': [
        "Chemical equilibrium describes the state in which the forward and reverse reactions occur at equal rates: the equilibrium constant, its dependence on temperature, and the shifts caused by changing concentration, pressure or temperature. The exam tests Le Chatelier's principle and the calculation of equilibrium quantities from starting amounts.",
        "The exam rewards explaining each response through the principle: a stress on the system is answered by a shift that reduces it. Equilibrium constant questions reward keeping the expression in the correct form, with concentrations of solids and pure liquids omitted.",
    ]},
    {'slug': 'volumetric-analysis', 'core': [
        "Volumetric analysis is the laboratory skill of measuring concentration through titration: standard solutions, burettes and pipettes, and the calculations of molarity and normality at the equivalence point. The exam tests the preparation of standard solutions, the choice and use of indicators, and the arithmetic of titration data.",
        "The core formula connects the volume and concentration of one reactant to the other through the reaction ratio, and the exam rewards writing the balanced reaction before calculating. The distinction between molarity and normality, and when each is used, is the topic's guard.",
    ]},
    {'slug': 'ionic-equilibrium', 'core': [
        "Ionic equilibrium covers the behaviour of weak and strong electrolytes in water: dissociation, the ionic product of water, pH, buffers and the hydrolysis of salts. The exam tests the calculation of pH from hydrogen ion concentration, the action of a buffer, and the strength of acids and bases expressed through their constants.",
        "The topic's numeric heart is the logarithmic definition of pH and the distinction between strong and weak electrolytes through their degree of dissociation. Buffer questions reward one statement: a buffer resists pH change by absorbing added acid or base.",
    ]},
    {'slug': 'chemical-kinetics', 'core': [
        "Chemical kinetics studies the rates of reactions and the factors that control them: concentration, temperature, catalyst and surface area, together with the rate law and the order of a reaction. The exam tests the relation between concentration and rate, the effect of temperature through activation energy, and the vocabulary of rate constant and order.",
        "The exam rewards reading a rate law from described behaviour and explaining why a temperature rise accelerates a reaction through more molecules crossing the activation barrier. The graph of progress of the reaction, and where activation energy appears, is the topic's visual core.",
    ]},
    {'slug': 'electrochemistry', 'core': [
        "Electrochemistry connects chemistry to electricity: electrolytic cells, galvanic cells, standard electrode potentials and the electrochemical series. The exam tests what happens at each electrode, the direction of electron flow, and the prediction of spontaneous reaction from electrode potentials.",
        "The electrochemical series is the topic's map: a higher metal displaces a lower one from its salt, and the cell potential is the difference of the two electrode potentials. Predicting which reaction is spontaneous, and which electrode is the anode, are the questions that recur.",
    ]},
    {'slug': 'chemical-thermodynamics', 'core': [
        "Chemical thermodynamics applies the laws of energy to chemical change: enthalpy, entropy and free energy, and the direction of reactions dictated by them. The exam tests the enthalpy change of reactions, the meaning of entropy, and the free-energy criterion for spontaneous change.",
        "The anchor is the free-energy equation: a reaction is spontaneous when the free energy change is negative, balancing the enthalpy and entropy contributions. Hess's law, which allows the addition of reaction enthalpies, answers a family of numeric questions.",
    ]},
    {'slug': 'nuclear-chemistry', 'core': [
        "Nuclear chemistry studies reactions of the nucleus: radioactivity, artificial transmutation, nuclear fission and fusion, and their energy changes. The exam tests balancing nuclear equations, the characteristics of the emitted radiations, and the release of energy represented by the mass defect.",
        "The tasks reduce to conserving mass number and atomic number in every nuclear equation and to attributing the energy release to the mass-energy equivalence. The distinction between fission in heavy nuclei and fusion in light nuclei explains where nuclear energy originates.",
    ]},
    {'slug': 'chemistry-of-non-metals', 'core': [
        "The chemistry of non-metals treats the elements that sit to the right and top of the periodic table: hydrogen, carbon, nitrogen, oxygen, the halogens and sulphur, together with their important compounds. The exam tests the preparation, properties and uses of ammonia, acids, bleaches and the hydrides of the elements.",
        "Organising revision by element, then by its key compounds and the reaction that produces each, keeps the recall manageable. The exam rewards knowing the conditions of the familiar processes and the distinctive test for each common gas.",
    ]},
    {'slug': 'chemistry-of-metals', 'core': [
        "The chemistry of metals covers the metallic elements, their extraction from ores and their characteristic reactions: the reactivity series, the extraction of important metals, and the properties they share with and without their unique reactions. The exam tests the route from ore to metal, the reasons for using given methods, and the distinctive behaviour of reactive metals.",
        "The reactivity series is the chapter's skeleton: a more reactive metal displaces a less reactive one from its salt, and the method of extraction follows from reactivity. Describing each extraction as a choice of method justified by reactivity is the answering style the exam rewards.",
    ]},
    {'slug': 'bio-inorganic-chemistry', 'core': [
        "Bio-inorganic chemistry connects metal ions to life: the elements that living systems require, the role of iron in oxygen transport, and the metals that enzymes and other biomolecules depend on. The exam tests which metal performs which biological function and what happens when the supply is deficient.",
        "A source-function-defect table, one row per essential metal, contains the whole topic. The exam rewards knowing that haemoglobin depends on iron, and that enzymes and hormones rely on a handful of metals for activity.",
    ]},
    {'slug': 'general-organic-chemistry', 'core': [
        "General organic chemistry establishes the thinking tools of the subject: functional groups, hybridisation, the electronic effects that influence reactivity, and the stability of reaction intermediates. The exam tests identifying functional groups, explaining why one position is more reactive than another, and comparing the stability of carbocations.",
        "The electronic effects, induction and resonance, are the topic's reasoning engine, because they explain reactivity across every later chapter. The exam rewards stating the effect, the atom involved, and the consequence for electron density in one sentence.",
    ]},
    {'slug': 'hydrocarbons', 'core': [
        "Hydrocarbons covers alkanes, alkenes and alkynes: their structure, preparation and the reactions that characterise saturated and unsaturated carbon chains. The exam tests addition reactions across the multiple bond, the conditions that select a product, and the structural difference between the families.",
        "The distinction that organises the chapter is addition for unsaturated compounds and substitution for saturated ones. The exam rewards associating each reagent and condition with the reaction it performs on a double or triple bond.",
    ]},
    {'slug': 'aromatic-hydrocarbons', 'core': [
        "Aromatic hydrocarbons centre on benzene and its derivatives: the delocalised structure that gives the ring its stability, and the electrophilic substitution reactions that characterise it. The exam tests the resonance picture of benzene, the conditions of substitution, and why aromatic rings resist addition.",
        "The exam rewards knowing that benzene undergoes substitution rather than addition because addition would destroy its delocalisation. Naming the reagents and conditions of each substitution, and the directing effects of substituents, covers most of the topic's questions.",
    ]},
    {'slug': 'haloalkanes-and-haloarenes', 'core': [
        "Haloalkanes and haloarenes treat compounds containing carbon-halogen bonds: their preparation, the nucleophilic substitution reactions of the alkyl halides, and the relative reactivity of the aryl halides. The exam tests the mechanism of substitution, the factors that affect its rate, and why the aryl halide is far less reactive.",
        "The central comparison is the reactivity gap between the two families, explained by the strength of the carbon-halogen bond and the absence of a suitable site in the aryl case. Questions on the preparation and the products of substitution follow from that single explanation.",
    ]},
    {'slug': 'alcohols-and-phenols', 'core': [
        "Alcohols and phenols cover the hydroxyl compounds: the preparation and reactions of the alcohols, the acidity of the phenols, and the differences in behaviour between the aliphatic and aromatic hydroxyl groups. The exam tests the oxidation of alcohols, the distinction between primary, secondary and tertiary members, and the acidity of phenol.",
        "The organising contrast is the difference between the alkyl and aryl hydroxyl group: phenol is acidic where the alcohols are not, and oxidation products depend on the class of the alcohol. Those two comparisons answer a large fraction of the topic.",
    ]},
    {'slug': 'ethers', 'core': [
        "Ethers are the compounds with an oxygen link between two carbon chains, here treated through their preparation and their characteristic reactions, notably the cleavage by acids. The exam tests the formation of ethers, the bonding and structure of the oxygen bridge, and the products of cleavage.",
        "The anchor fact is the acid-catalysed cleavage that splits the ether into two parts at the oxygen. Knowing which reagent forms an ether from an alcohol, and what the cleavage produces, covers most of the topic.",
    ]},
    {'slug': 'aldehydes-and-ketones', 'core': [
        "Aldehydes and ketones are the carbonyl compounds, tested through their preparation, the nucleophilic addition reactions of the carbonyl group, and the oxidation that distinguishes the two families. The exam rewards distinguishing the aldehyde, which is readily oxidised, from the ketone, which is not, and predicting the products of addition.",
        "The carbonyl group's polarised bond is the reasoning centre: nucleophiles attack the carbon and the products include alcohols, hydrazones and cyanohydrins. The exam's favourite differentiators, Tollens' and Fehling's tests, hinge entirely on the aldehyde's easy oxidation.",
    ]},
    {'slug': 'carboxylic-acid-and-its-derivatives', 'core': [
        "The carboxylic acids and their derivatives close the oxygen series: the acidity of the carboxyl group, the preparation of the acids, and the conversion to esters, acid chlorides and amides. The exam tests the acidity compared with alcohols and phenols, the reactions that interconvert the family, and the naming of the derivatives.",
        "The carboxyl group unifies the topic: it is the source of acidity, the site of esterification, and the point from which every derivative is prepared. The exam rewards one reaction network of the family drawn as a wheel, with the acid at the centre.",
    ]},
    {'slug': 'nitro-compounds', 'core': [
        "Nitro compounds carry the nitrogen-oxygen group and are tested through their preparation, their reduction to amines and their characteristic reactions. The exam tests the nitration of hydrocarbons, the reduction of the nitro group as the route to a primary amine, and the stability and uses of the compounds.",
        "The single chain that ties the topic is reduction: the nitro group becomes an amine, and that conversion is the route that matters. Questions about preparation reduce to knowing which substrate is nitrated and which reagent performs the reduction.",
    ]},
    {'slug': 'amines', 'core': [
        "Amines are the nitrogen-containing organic bases: their classification, preparation and basicity, and the reactions that distinguish primary, secondary and tertiary members. The exam tests the basic strength of the amines, their formation from halides or nitro compounds, and their reactions with acids and reagents.",
        "Basicity is the topic's spine: amines are bases because the nitrogen carries a lone pair, and the order of basic strength among the classes is the recurring question. The exam rewards explaining the basicity trend through electron density on nitrogen.",
    ]},
    {'slug': 'organometallic-compounds', 'core': [
        "Organometallic compounds pair a metal with carbon, in reagents such as the Grignard reagents that carry a carbon-metal bond. The exam tests their preparation, their reactivity as sources of carbon nucleophiles, and their use in building carbon-carbon bonds and converting to alcohols and other products.",
        "The reagent's character is the key: the carbon-metal bond is polarised so that carbon behaves as a nucleophile. Understanding that reactivity explains why the reagent attacks carbonyl compounds and why it must be protected from water.",
    ]},
    {'slug': 'manufacturing-processes', 'core': [
        "Manufacturing processes covers the industrial chemistry behind everyday materials: the Haber process for ammonia, the contact process for sulphuric acid, and the electrolytic production of caustic soda, each tested through its feedstocks, conditions and steps. The exam asks for the conditions, the catalyst and the reason each is chosen.",
        "The structured habit is to learn every process as a fixed sequence of raw material, reaction conditions, catalyst, and product, and to explain why each condition is chosen. Rebuilding that sequence from memory is the reliable preparation for the topic.",
    ]},
    {'slug': 'applications-of-non-metals-metals-and-compounds', 'core': [
        "This topic applies chemistry to materials: the uses of non-metals such as carbon, nitrogen and silicon, the roles of metals in alloys and construction, and the compounds that serve industry. The exam asks why a particular material is chosen for a purpose, answered by matching a property to a need.",
        "The answering method is to pair each material with one decisive property and one use that follows from it. The exam rewards organised recall of uses, and a use-material-property table is the topic's compact revision unit.",
    ]},
    {'slug': 'chemistry-in-service-to-mankind', 'core': [
        "Chemistry in service to mankind brings the discipline to medicine, agriculture, food and the home: drugs, fertilisers, pesticides, plastics, soaps and detergents, disinfectants and the substances of daily life. The exam tests the composition, purpose and safe handling of these familiar chemicals.",
        "The topic rewards structured association: each product paired with its composition and its function. A compact table of product-composition-use, rebuilt from memory, answers the majority of the items.",
    ]},
    {'slug': 'chemical-tests', 'core': [
        "Chemical tests are the diagnostic reactions by which chemist identify substances: the confirmatory tests for cations, anions and gases through characteristic colours, precipitates and odours. The exam asks for the reagent, the observation and the ion or gas thereby identified.",
        "The topic is a table by nature: reagent, observation and conclusion belong together for every test. Assembling that table, and rehearsing it until the triples are automatic, is the only preparation that transfers to the examined questions.",
    ]},
    {'slug': 'separation-techniques', 'core': [
        "Separation techniques organise mixtures into their pure components: filtration, crystallisation, distillation, solvent extraction, chromatography and sublimation, each chosen according to a physical property. The exam asks which technique separates a given mixture and why it works.",
        "The deciding question is which property, boiling point, solubility or volatility, differs between the components. Matching each technique to its property and its application keeps the topic completely organised.",
    ]},
    {'slug': 'types-of-titration', 'core': [
        "Types of titration distinguish the analytical methods built on measuring reaction endpoints: acid-base, redox and precipitation titrations, each with its own indicator and endpoint conditions. The exam tests the choice of titration, the indicator that matches the endpoint, and the calculations that follow from the data.",
        "The anchor is the equivalence-point idea shared by every type, with the indicator chosen so its colour change coincides with that point. The exam rewards knowing the classic indicator for each titration family and what the endpoint indicates.",
    ]},
    {'slug': 'origin-of-life', 'core': [
        "The origin of life asks how non-living matter gave rise to living systems, and the exam tests the conditions of the early earth, the classic experiments that synthesised organic molecules, and the theories that account for the transition. The questions reward a narrative of chemistry becoming biology.",
        "The timeline of the experiments, each with its question, method and conclusion, is the topic's spine. The exam rewards knowing what the early atmosphere contained, what the experiments synthesised, and what step the experiments could not reproduce.",
    ]},
    {'slug': 'evidences-of-evolution', 'core': [
        "Evidences of evolution assemble the observations that species change: comparative anatomy, embryology, palaeontology and molecular biology, with homologous and analogous organs, vestigial structures and the fossil record. The exam asks which type of evidence a given example represents and what it demonstrates.",
        "The exam rewards classifying each piece of evidence, and the logic is simple once fixed: a shared structure from a common ancestor is homologous, while a similar function from separate origins is analogous. The organising table of evidence types keeps the answers mechanical.",
    ]},
    {'slug': 'theories-of-evolution', 'core': [
        "Theories of evolution explain the mechanism of change: Lamarck's use and disuse, Darwin's natural selection through variation and struggle, and the modern synthesis that joins genetics to selection. The exam compares the theories, states the conditions of selection, and tests which observation each theory explains.",
        "Natural selection in one precise sentence, variation arises, the environment selects, and the selected traits spread, answers most conceptual items. The exam also rewards knowing the flaw in Lamarck's argument and the contributions that completed Darwin's.",
    ]},
    {'slug': 'human-evolution', 'core': [
        "Human evolution traces the lineage of modern humans from early hominids: the fossil stages, the features that changed, and the timeline of brain size, posture and tool use. The exam tests naming the stages and attaching to each stage its defining feature and approximate era.",
        "A compact date-feature-trait table, one row per stage, organises the whole topic. The exam rewards locating each stage on the line and stating what change distinguishes it from its predecessor.",
    ]},
    {'slug': 'animal-diversity-from-protozoa-to-chordata', 'core': [
        "Animal diversity from protozoa to chordata surveys the animal kingdom in its ascending order: the level of organisation, symmetry, germ layers and body cavity of each phylum, with the characteristic examples of every group. The exam asks which animal belongs to which phylum and which feature places it there.",
        "The master comparison table, with a row per phylum listing symmetry, germ layers, body cavity and examples, is the topic's complete revision unit. The exam rewards reasoning from a stated feature to its phylum.",
    ]},
    {'slug': 'types-of-animal-tissues', 'core': [
        "Types of animal tissues classifies the four basic tissue groups, epithelial, connective, muscular and nervous, each with its subtypes, locations and functions. The exam tests which tissue performs which role and where each subtype is found.",
        "The topic is inherently tabular: for each tissue, associate one location and one function. The exam rewards precision in the classification, since the options differ by a single word.",
    ]},
    {'slug': 'plasmodium', 'core': [
        "Plasmodium is the protozoan that causes malaria, and its study covers its life cycle across the mosquito vector and the human host, its symptoms and its control. The exam tests the stages of the cycle, the vector, and the stage responsible for the fever.",
        "The two-host cycle diagram, drawn once and remembered, answers the majority of the topic's questions. The exam rewards knowing where the parasite multiplies and what the characteristic symptom indicates.",
    ]},
    {'slug': 'earthworm-pheretima', 'core': [
        "The earthworm, Pheretima, is the classic representative of the annelids, and its study covers its external segmentation, its setae, and its digestive, circulatory, excretory and nervous systems. The exam tests the organs of the worm and the adaptations of its burrowing life.",
        "The topic rewards a body-plan tour: describe the worm's segments, its closed circulation, its olygochaete features and its ganglionic nervous system in order. The exam asks which system performs which function, and the tour answers every such item.",
    ]},
    {'slug': 'frog-rana', 'core': [
        "The frog, Rana, is the classic amphibian, and its study covers its moist skin, its two-chambered-plus-partial heart, its modes of respiration and its life cycle with a tadpole stage. The exam tests the frog's anatomy, its adaptations to land and water, and its development.",
        "The topic rewards a systematic body-plan account: skin, skeleton, circulation, respiration and reproduction in order. The exam likes the contrasts between the frog's life stages and between the frog and the worm.",
    ]},
    {'slug': 'digestive-system', 'core': [
        "The digestive system carries food from mouth to large intestine, with each region contributing a defined step of breakdown and absorption and each enzyme acting at a specific site. The exam tests where each enzyme acts, what it digests, and the consequence of damage to a section.",
        "A flow chart of the tract, with the enzymes and secretions placed at each station, is the topic's one-page summary. The exam rewards knowing what happens in each segment and which nutrient is absorbed where.",
    ]},
    {'slug': 'respiratory-system', 'core': [
        "The respiratory system handles the exchange of gases: the passages, the alveoli where exchange occurs, the mechanics of breathing and the transport of oxygen and carbon dioxide in the blood. The exam tests the site of exchange, the direction of gas movement and the carriage of each gas.",
        "The topic is a pathway: air enters, reaches the alveoli, and gases move along pressure gradients into and out of the blood. The exam rewards knowing the factors that favour oxygen release and the difference between external and internal respiration.",
    ]},
    {'slug': 'circulatory-system', 'core': [
        "The circulatory system moves blood around the body: the heart's chambers and valves, the vessels, the double circulation, and the composition and role of blood. The exam tests the path of blood, the direction set by the valves, and what each component of blood carries.",
        "A heart-and-vessels diagram with the flow arrows is the topic's central device. The exam rewards knowing the route from atrium to ventricle to artery, the distinction between oxygenated and deoxygenated flow, and the functions of the blood cells.",
    ]},
    {'slug': 'excretory-system', 'core': [
        "The excretory system removes metabolic waste: the kidneys, the nephron as the functional unit, the formation of urine, and the composition and volume of the waste products. The exam tests the steps of filtration, reabsorption and secretion along the nephron.",
        "The nephron as a pathway, with what is filtered, reabsorbed and secreted at each site, is the topic's spine. The exam rewards knowing where each substance is reclaimed and what the final urine contains.",
    ]},
    {'slug': 'nervous-system', 'core': [
        "The nervous system coordinates the body through neurons and their circuits: the structure of the neuron, the reflex arc, the regions of the brain and the spinal cord, and the transmission of the impulse. The exam tests the direction of an impulse, the parts of the reflex arc and the function of each brain region.",
        "The topic rewards tracing a signal from stimulus to response, naming each relay, and locating each function in the brain. A labelled diagram of the reflex arc and of the brain sections answers most of the items.",
    ]},
    {'slug': 'sense-organs', 'core': [
        "The sense organs collect information from the environment: the eye for vision, the ear for hearing and balance, together with the organs of taste, smell and touch. The exam tests the structure and function of each receptor and the path of each sensation to the brain.",
        "The topic is suited to labelled diagrams: the eye's layers and lens, the ear's three compartments, and the receptor cells of each organ. The exam rewards knowing which structure performs which transformation of the stimulus.",
    ]},
    {'slug': 'endocrinology', 'core': [
        "Endocrinology covers the endocrine glands and their hormones: which gland secretes which hormone, the target organ of each, and the effect of each on the body. The exam tests the source-target-effect triple and the consequences of over or under secretion.",
        "A source-target-effect table, one row per hormone, is the whole topic in one page. The exam returns to the pituitary as the master gland and to the interplay between the glands in maintaining balance.",
    ]},
    {'slug': 'reproductive-system', 'core': [
        "The reproductive system covers the organs that produce gametes, the menstrual cycle, fertilisation and the development of the embryo: the male and female tracts, the hormonal control of the cycle, and the stages from zygote to birth. The exam tests the site of each stage and the hormones that control the cycle.",
        "The topic is a sequence: gametes form, meet, the zygote implants, and the embryo grows under hormonal control. The exam rewards knowing which stage occurs where and which hormone governs each phase of the cycle.",
    ]},
    {'slug': 'microbial-diseases', 'core': [
        "Microbial diseases surveys the infections caused by bacteria, viruses, protozoa and fungi: the pathogen, the mode of transmission and the characteristic symptoms of each disease. The exam tests the pathogen-disease pairing and the route by which each infection spreads.",
        "A pathogen-disease-vector-symptom table is the topic's complete revision unit. The exam rewards the ability to name the organism behind a familiar disease and the route it takes from reservoir to host.",
    ]},
    {'slug': 'immunity', 'core': [
        "Immunity covers the body's defensive systems: the innate barriers and cells, the adaptive response with its antibodies and memory, and the difference between the first and second lines of defence. The exam tests which cell performs which role and which response is specific and remembered.",
        "The topic's core is the difference between the immediate, non-specific defences and the delayed, specific response. The exam rewards the vocabulary of antigens, antibodies, B cells and T cells, and the memory that a later infection does not re-fight.",
    ]},
    {'slug': 'vaccines', 'core': [
        "Vaccines prepare the immune system before infection: what a vaccine contains, how it triggers antibody production and memory, and how active immunity differs from passive immunity. The exam tests the immune principle behind vaccination and the consequences of the choices between live and killed agents.",
        "The topic's anchor is that a vaccine presents the immune system with a harmless form of the pathogen so that memory develops without the disease. The exam rewards the distinction between a vaccine protecting actively and a serum transferring passive immunity.",
    ]},
    {'slug': 'medical-technology', 'core': [
        "Medical technology applies biology and laboratory science to diagnosis and treatment: blood testing, imaging, microscopy and the tests that measure the body's state. The exam tests what each test measures, why it is ordered and what the result indicates.",
        "The topic reduces to a test-measurement-condition table. The exam rewards knowing which test monitors which function and what an abnormal result points to.",
    ]},
    {'slug': 'applied-microbiology', 'core': [
        "Applied microbiology uses microorganisms for useful ends: fermentation for food and drink, the production of antibiotics and other products, and the industrial processes built on microbial action. The exam tests which organism produces which product under which conditions.",
        "A product-organism-process table is the topic's compact device. The exam rewards knowing the role of each microorganism and the conditions its process requires.",
    ]},
    {'slug': 'animal-behavior', 'core': [
        "Animal behaviour studies what animals do and why: instinctive and learned behaviour, and the patterns of feeding, mating and social living. The exam tests classifying behaviour from a description and explaining the survival value of each pattern.",
        "The topic rewards a behaviour-type-definition-example table, rebuilt from memory. The exam asks whether a described action is inborn or acquired and what purpose it serves.",
    ]},
    {'slug': 'environmental-pollution', 'core': [
        "Environmental pollution identifies the contamination of air, water and soil: the pollutants, their sources and their effects, and the control measures available. The exam tests which pollutant comes from which source and which effect follows which pollutant.",
        "A pollutant-source-effect table, with the associated problems of acid rain and global warming, is the topic's spine. The exam rewards connecting a pollutant to its origin and to its consequence.",
    ]},
    {'slug': 'adaptations', 'core': [
        "Adaptations describes how organisms cope with their environments: the features of desert, aquatic, cold and disturbed habitats, and the structural and behavioural responses that survival demands. The exam tests which feature suits which environment and why.",
        "The reasoning skill is matching every feature to the need that selects it. The exam rewards explaining, for each adaptation, the pressure it answers, rather than listing features alone.",
    ]},
    {'slug': 'conservation-biology', 'core': [
        "Conservation biology is the protection and management of biodiversity: the threats to species, the protected areas and the strategies that preserve genetic variety. The exam tests the value of biodiversity, the tools of conservation and the reasons a species may decline.",
        "The topic rewards arguing from the value of diversity, since every conservation question follows from the cost of its loss. The exam asks which step protects which resource and why biodiversity matters.",
    ]},
    {'slug': 'carbohydrates-lipids-and-minerals', 'core': [
        "Carbohydrates, lipids and minerals are the energy and building materials of the cell: the sugars from monosaccharides to polysaccharides, the fats and oils, and the inorganic ions that physiology needs. The exam tests the structure, members and functions of each group.",
        "A component-monomers-function table for the three groups is the topic's one page of revision. The exam rewards knowing where each is stored, what each provides and which deficiency follows from a missing mineral.",
    ]},
    {'slug': 'proteins-and-enzymes', 'core': [
        "Proteins and enzymes describe the workhorses of the cell: proteins as polymers of amino acids whose sequence sets their structure, and enzymes as the proteins that catalyse the cell's reactions. The exam tests the levels of protein structure, the active site and the factors that alter enzyme activity.",
        "The topic's core is the structure-function link of a protein and the specificity of an enzyme's active site. The exam rewards knowing which changes of temperature and pH disable the enzyme and why.",
    ]},
    {'slug': 'introduction-and-classification-systems', 'core': [
        "Introduction and classification systems establishes how living things are named and grouped: the hierarchy from kingdom to species, the criteria on which classification rests, and the binomial system of naming. The exam tests the ranks, the rules and the reasoning behind the groupings.",
        "The topic rewards a classification ladder and the rules of two-part naming. The exam asks which rank holds which group and why classification changes as evidence grows.",
    ]},
    {'slug': 'monera-and-virus', 'core': [
        "Monera and viruses treat the simplest organisms: the prokaryotic bacteria with their forms, nutrition and roles, and the viruses that blur the living-nonliving boundary. The exam tests the structure of bacteria, their classification and reproduction, and the nature of viruses.",
        "The distinction between the prokaryotic cell and the virus is the topic's spine. The exam rewards knowing what a bacterium possesses that a virus lacks, and what each causes in industry and disease.",
    ]},
    {'slug': 'fungi-and-lichens', 'core': [
        "Fungi and lichens cover the heterotrophic and symbiotic groups: the fungal body of hyphae, their modes of nutrition and reproduction, and the lichen as a partnership of fungus and alga. The exam tests the structure of fungi, their role and the nature of the lichen association.",
        "The topic's anchor is the arrangement of the fungal body and the mutual dependence that makes a lichen. The exam rewards comparing the fungal mode of nutrition with that of plants and animals.",
    ]},
    {'slug': 'algae', 'core': [
        "Algae are the photosynthetic aquatic organisms, from the single-celled forms to the large seaweeds: their pigments, their classification and their economic importance. The exam tests the characteristic pigments of the major groups and the ways algae serve food, fuel and industry.",
        "The topic rewards a group-pigment-habitat-use table. The exam asks which alga carries which pigments and how each group contributes economically.",
    ]},
    {'slug': 'bryophytes', 'core': [
        "Bryophytes are the simplest land plants: the mosses and liverworts, with a dominant gametophyte, no true roots and a dependence on water for fertilisation. The exam tests the alternation of generations, the structure of the plant body and the amphibious nature of the group.",
        "The topic's core is the dominance of the gametophyte and the lack of woody conduction. The exam rewards knowing which generation reproduces sexually and why the group stays low and damp.",
    ]},
    {'slug': 'pteridophytes', 'core': [
        "Pteridophytes are the first vascular plants without seeds: ferns with true roots, stems and leaves, and a sporophyte-dominant life cycle. The exam tests the plant body, the alternation of generations and the significance of the group as seedless vascular plants.",
        "The topic is organised by the transition from gametophyte to sporophyte dominance. The exam rewards the difference between the dominant generation in bryophytes and in pteridophytes.",
    ]},
    {'slug': 'gymnosperms', 'core': [
        "Gymnosperms are the seed plants whose seeds lie uncovered: the conifers and their allies, with naked seeds, needle leaves and wind-pollinated reproduction. The exam tests the structure of the plant, the position of the seed and the gymnosperms' place in evolution.",
        "The topic's defining fact is the naked seed, which sets the group apart from the flowering plants. The exam rewards knowing the features that adapt gymnosperms to cold, dry climates.",
    ]},
    {'slug': 'angiosperms', 'core': [
        "Angiosperms are the flowering plants, the most advanced and widespread group: the flower, the covered seed and the double fertilisation that produces the endosperm. The exam tests the plant body, the floral structure and the features that give the group its dominance.",
        "The topic's anchor is the flower and the covered seed of the group. The exam rewards knowing what the double fertilisation produces and how the group's vascular and reproductive features outdo the earlier plants.",
    ]},
    {'slug': 'economic-importance-of-plant-groups', 'core': [
        "The economic importance of plant groups links each major group to its uses: the food, fuel, fibre, medicine and industry drawn from algae, fungi, bryophytes and higher plants. The exam asks which product comes from which group and what purpose it serves.",
        "The topic is a use-group-product table, assembled and rebuilt from memory. The exam rewards the pairing of a plant group with its principal contribution to human needs.",
    ]},
    {'slug': 'medicinal-plants-of-nepal', 'core': [
        "Medicinal plants of Nepal connects the country's plant life to health: the native species used in traditional and modern medicine, the part used and the ailment treated. The exam tests the plant-use-parts associations and the conservation of the resource.",
        "The topic rewards a plant-part-use table built around the well-known Nepali species. The exam asks which plant relieves which condition and which part carries the active material.",
    ]},
    {'slug': 'ecosystem-ecology', 'core': [
        "Ecosystem ecology describes the living and non-living parts of a community and the flow of energy between them: producers, consumers and decomposers, food chains and webs, and the pyramids of numbers, biomass and energy. The exam tests the roles of the trophic levels and the direction of energy flow.",
        "The topic's spine is the transfer of energy from producers upward and the losses at each level. The exam rewards reading the direction of a chain, naming the producer and noting where energy is lost.",
    ]},
    {'slug': 'biogeochemical-cycles-and-ecological-imbalances', 'core': [
        "Biogeochemical cycles and ecological imbalances trace the movement of matter through life and environment: the carbon, nitrogen, oxygen, water and phosphorus cycles, and the disruptions such as pollution and nutrient overload that unbalance them. The exam asks which process moves which substance and which imbalance follows which disruption.",
        "The topic rewards a loop diagram per cycle, with the reservoirs and the human disruptions marked. The exam asks how a substance returns to its source and what happens when the loop breaks.",
    ]},
    {'slug': 'vegetation-and-adaptation', 'core': [
        "Vegetation and adaptation describes plant life across climates and altitudes: the great vegetation belts and the structural features with which plants meet drought, cold, salinity and flooding. The exam tests which zone supports which vegetation and which feature suits which stress.",
        "The topic rewards a climate-zone-vegetation-feature table, from tropical forest to alpine. The exam asks how a plant's leaves, roots and cuticle answer the demands of its habitat.",
    ]},
    {'slug': 'prokaryotic-and-eukaryotic-cells', 'core': [
        "Prokaryotic and eukaryotic cells establish the grand division of life: the differences in nucleus, organelles, ribosomes and cell wall, and the representatives of each type. The exam tests which feature is present in which cell and the practical consequences of the differences.",
        "The topic is a comparison by nature: one column per cell type listing nucleus, membrane-bound organelles, ribosome size and wall composition. The exam rewards the accurate placement of each feature.",
    ]},
    {'slug': 'cell-organelles', 'core': [
        "Cell organelles are the functional compartments of the cell: the nucleus, mitochondria, chloroplast, endoplasmic reticulum, Golgi apparatus, lysosome, ribosome and cytoskeleton, each with a defined role. The exam tests which organelle performs which function and where each is found.",
        "A structure-function table, with one row per organelle, is the whole topic compactly. The exam rewards the association of each organelle with the process it carries out.",
    ]},
    {'slug': 'cell-cycle-and-cell-division', 'core': [
        "The cell cycle and cell division describe how cells grow and reproduce: interphase, mitosis and meiosis, their phases and their products, and the difference in the number of divisions. The exam tests chromosome behaviour, the outcome of each process and the vocabulary of the phases.",
        "The topic's spine is the contrast between mitosis and meiosis: one division preserving the chromosome number versus two divisions halving it. The exam rewards knowing which cells divide by which process and what each produces.",
    ]},
    {'slug': 'genetic-material-dna-and-rna', 'core': [
        "The genetic material, DNA and RNA, carries hereditary information: the double-stranded structure of DNA with its base pairing, its replication, and the flow of information to protein through transcription and translation. The exam tests the structure, the pairing rules and the machinery of information transfer.",
        "The topic's anchor is the complementary base-pairing and the antiparallel double strand. The exam rewards tracing information from DNA to RNA to protein and knowing the roles of the three RNA types.",
    ]},
    {'slug': 'mendelian-genetics-and-linkage', 'core': [
        "Mendelian genetics and linkage apply the laws of inheritance: dominance, segregation and independent assortment, and the departure from them in linkage and crossing over. The exam tests setting up a cross, predicting a ratio and explaining why linked genes do not assort independently.",
        "The topic rewards cleanly writing the parental genotypes and the gametes before any ratio. The exam asks for the outcome of a cross and the reason that linked genes stay together.",
    ]},
    {'slug': 'sex-linked-inheritance', 'core': [
        "Sex-linked inheritance describes traits carried on the sex chromosomes: the transmission of X-linked conditions, the carrier state and the pattern of affected offspring. The exam tests the pedigree of a sex-linked trait and which parent passes it to which child.",
        "The topic's spine is the dosage of the X chromosome: a single mutated copy affects the male while the female carries or escapes. The exam rewards tracing the allele through a pedigree line by line.",
    ]},
    {'slug': 'mutation-polyploidy-and-genetic-disorders', 'core': [
        "Mutation, polyploidy and genetic disorders cover the changes that alter genetic material and their consequences: gene and chromosomal mutations, the multiplication of whole chromosome sets, and the syndromes that follow. The exam tests the type of change, its cause and the disorder it produces.",
        "The topic rewards a change-type-disorder table, connecting each alteration to its condition. The exam asks which change underlies which syndrome and what factor increases the change.",
    ]},
    {'slug': 'plant-tissues-and-vascular-bundles', 'core': [
        "Plant tissues and vascular bundles classify the tissues of the plant body: meristematic and permanent, protective and conducting, and the arrangement of xylem and phloem into bundles. The exam tests which tissue performs which role and how the bundles are arranged in each organ.",
        "The topic is a classification table: tissue, location and function in one row each. The exam rewards knowing which tissue divides, which conducts water and which conducts food.",
    ]},
    {'slug': 'anatomy-of-monocot-and-dicot-root-stem-and-leaf', 'core': [
        "The anatomy of monocot and dicot organs compares the internal arrangement of the root, stem and leaf in the two plant classes: the number of vascular bundles, the presence of a pith, and the structure of the leaf's mesophyll. The exam tests which arrangement belongs to which class and organ.",
        "The topic is best revised as three paired diagrams: the monocot and dicot section of each organ side by side. The exam rewards confident placement of the bundles and the pith.",
    ]},
    {'slug': 'water-relations', 'core': [
        "Water relations describes the journey of water through the plant: its entry at the root, its rise through the xylem and its loss by transpiration, with the forces that drive each step. The exam tests the mechanism of each movement and the instruments used to study them.",
        "The topic is a pathway with a driving force at each station: osmosis at the root, cohesion-tension in the xylem and evaporation at the leaf. The exam rewards naming the force and its stage.",
    ]},
    {'slug': 'photosynthesis', 'core': [
        "Photosynthesis converts light energy into the chemical energy of food: the light and dark reactions, the pigments, and the factors that limit the rate. The exam tests where each reaction occurs, what each requires and produces, and how temperature, light and carbon dioxide set the limit.",
        "A stage-location-input-output table for the light and dark reactions is the topic's compact spine. The exam rewards locating each product in its reaction and knowing which factor limits the process at a given moment.",
    ]},
    {'slug': 'respiration', 'core': [
        "Respiration releases energy from food: glycolysis, the Krebs cycle and the electron transport chain, together with the anaerobic pathways of fermentation. The exam tests where each stage occurs, what each produces and the fate of pyruvate under different oxygen conditions.",
        "The topic is a pathway with defined energy yields at each stage. The exam rewards tracing glucose to final products and knowing which yield accompanies which pathway.",
    ]},
    {'slug': 'plant-growth-and-seed-germination', 'core': [
        "Plant growth and seed germination describe how a seed becomes a seedling and how the plant grows: imbibition, the mobilisation of stored food, the emergence of the radicle and plumule, and the hormonal control of growth. The exam tests the sequence of germination and the conditions it requires.",
        "The topic is a timeline from imbibition to establishment, with the hormones and conditions at each stage. The exam rewards the order of events and the requirement of water, air and warmth.",
    ]},
    {'slug': 'reproduction-and-sporogenesis-in-angiosperms', 'core': [
        "Reproduction and sporogenesis in angiosperms traces the origin of the gametes: microsporogenesis in the anther and megasporogenesis in the ovule, and the gametophytes they produce, together with pollination and the events of fertilisation. The exam tests where each process occurs and what each produces.",
        "The topic is a flower-to-fruit flow chart with the sexual events at each station. The exam rewards the location of microsporogenesis and megasporogenesis and the outcome of the double fertilisation.",
    ]},
    {'slug': 'embryo-and-endosperm', 'core': [
        "The embryo and endosperm follow fertilisation: the endosperm that nourishes the developing embryo, and the embryo's differentiation into radicle, plumule and cotyledons. The exam tests what the endosperm is, how it forms and what each part of the embryo becomes.",
        "The topic's anchor is the double fertilisation that produces the endosperm, the distinctive feature of flowering plants. The exam rewards knowing the origin of each part of the mature seed.",
    ]},
    {'slug': 'plant-tissue-culture', 'core': [
        "Plant tissue culture grows cells, tissues and organs on artificial media: its methods, its advantages over conventional propagation and the concept of totipotency on which it rests. The exam tests the conditions required and the applications of the technique.",
        "The topic's spine is regeneration from a small explant under controlled conditions. The exam rewards knowing what the culture requires and what advantages the technique offers.",
    ]},
    {'slug': 'genetic-engineering', 'core': [
        "Genetic engineering manipulates DNA to change the characteristics of an organism: the tools of restriction enzymes and vectors, the transfer and expression of genes, and the applications in medicine and agriculture. The exam tests what each tool does and the steps of the process.",
        "The topic is a step sequence: cut the gene, insert it, introduce it and express it. The exam rewards the order of the steps and the role of each tool.",
    ]},
    {'slug': 'biofertilizers-and-food-security', 'core': [
        "Biofertilizers and food security bring biology to the field: the organisms that enrich the soil with nitrogen and phosphorous, and the technologies that raise yields. The exam tests which organism performs which service and how these inputs help feed a growing population.",
        "The topic rewards a microorganism-service table, connecting each organism to its agricultural function. The exam asks how biofertilizers reduce dependence on synthetic inputs while raising production.",
    ]},
    {'slug': 'time-and-work', 'core': [
        "Time and work problems ask how long a person or a machine takes to complete a task, alone or together. The method is to treat the total work as one unit and convert each rate into work done per day or per hour, then combine rates where workers cooperate.",
        "The exam favours the classic shapes: two workers together, one replacing another, and the efficiency gap between people or machines. The disciplined habit is to write each rate as a fraction of the work per unit time before any arithmetic.",
    ]},
    {'slug': 'percentage', 'core': [
        "Percentage is the arithmetic of parts per hundred, and the CEE tests it through the classic applications: percentage increase and decrease, successive changes, and the comparison of quantities expressed as percentages. The skill is choosing the right base for every computation.",
        "The exam rewards mastering successive percentage changes, where the second change applies to the first result, and the shortcut of treating an increase-and-decrease pair as a combined effect. Writing each base explicitly prevents the standard errors.",
    ]},
    {'slug': 'profit-and-loss', 'core': [
        "Profit and loss trades in cost price, selling price, and the percentages of gain and loss, including the cases of marked price and discount. The exam tests the classic setups: gaining per cent, loss per cent and the combined effect of a discount on a marked price.",
        "The method is to name the base of every percentage, cost price for profit, and marked price for discount, before solving. Keeping the two bases separate answers the majority of the questions.",
    ]},
    {'slug': 'ratio-and-proportion', 'core': [
        "Ratio and proportion describe relative size and the constancy of a relation: dividing a quantity in a given ratio, comparing parts, and applying a proportion to a changing whole. The exam mixes ratios with ages, mixtures and shares.",
        "The technique is to keep the ratio in its given order and to introduce a common multiplier when a quantity is divided. The exam rewards translating the words of the problem into a ratio equation first.",
    ]},
    {'slug': 'problem-on-ages', 'core': [
        "Problems on ages relate the ages of two or more people now, in the past or in the future, through ratios and differences. The method is to pitch the ages as multiples of the common ratio and write the difference as one equation, since the gap between the ages is constant.",
        "The exam tests the classic shapes: an age ratio now combined with a stated ratio after a number of years. Constancy of the age gap is the anchor that keeps the algebra short and safe.",
    ]},
    {'slug': 'averages', 'core': [
        "Averages fold a group of numbers into a single value: finding the mean of a set, working back to a missing value, and comparing the averages of merged groups. The exam tests both the direct computation and the reversal of the formula.",
        "The method is to think in totals: the total of a group is its average times its size, and totals add while averages do not. Working from totals answers the merged-group questions before they look hard.",
    ]},
    {'slug': 'time-speed-and-distance', 'core': [
        "Time, speed and distance links the three quantities of motion: the basic relation, the conversions between units, and the classic cases of trains, boats and moving points meeting or overtaking. The exam tests relative speed whenever two objects move at once.",
        "The disciplined approach is to convert units at the start and to add or subtract speeds to form the relative speed. The exam rewards knowing the direction of the relative motion before applying the formula.",
    ]},
    {'slug': 'permutation-and-combination', 'core': [
        "Permutation and combination count the ways of arranging and selecting: arrangements where order matters and selections where it does not, with the formulas for each. The exam keeps the numbers small and tests the judgement of when order matters.",
        "The single decision, order matters or not, chooses the formula and prevents most errors. The exam rewards reading a question and naming it a permutation or a combination before touching the computation.",
    ]},
    {'slug': 'partnership', 'core': [
        "Partnership divides profit or loss among investors in proportion to their capital and the time it was invested. The exam tests two-partner cases where capitals and durations differ, and the ratio that follows.",
        "The method is to weight each capital by its time and reduce the product to the ratio of the partners. The exam rewards that single computation, which carries the whole question.",
    ]},
    {'slug': 'simple-interest-and-compound-interest', 'core': [
        "Simple and compound interest frame the growth of money: simple interest growing by a fixed sum yearly and compound interest growing by a multiplier. The exam tests rate, time, principal and amount, and the distinction between the two growths.",
        "The exam rewards knowing the two formulas and the habit of noting the compounding period before applying the compound formula. Keeping the bases and the periods explicit answers the questions cleanly.",
    ]},
    {'slug': 'distance-and-direction', 'core': [
        "Distance and direction trace a path on a plane: a sequence of moves between the cardinal directions, the net displacement and the final bearing. The method is to sketch the path as you read and to track the net east-west and north-south movement.",
        "The exam rewards the drawing discipline over algebra, since the answer falls out of a correct diagram. The habit of updating the net position after every move prevents the tangled-ending confusions.",
    ]},
    {'slug': 'coding-and-decoding', 'core': [
        "Coding and decoding converts letters, numbers or symbols into a hidden message under a stated or inferred rule: a shift, a reversal, a position swap or a substitution. The exam gives example pairs and asks to decode a fresh target.",
        "The method is to infer the rule from the given examples before touching the target. The exam rewards naming the rule explicitly, because the identified rule then decides the code mechanically.",
    ]},
    {'slug': 'ranking-order', 'core': [
        "Ranking order places people or items in a line and asks about positions: the rank from one end, the number of people and the count between two named individuals. The method is to fix one end as the anchor.",
        "The exam rewards turning every from-the-left or from-the-right into a position relative to the anchor. A clear picture of the line, updated as ranks are stated, answers most of the questions.",
    ]},
    {'slug': 'verbal-classification', 'core': [
        "Verbal classification offers a group of words and asks which one does not belong: the odd one out by category, function or property. The exam looks for the cleanest rule that separates the majority from the outlier.",
        "The method is to name the shared property of the majority before judging the outlier. The exam rewards choosing the item that breaks the strongest rule, not a superficial similarity.",
    ]},
    {'slug': 'verbal-analogy', 'core': [
        "Verbal analogy compares word pairs: A is to B as C is to D, where the relationship of the first pair must be transferred. The exam tests synonym, antonym, class, part-whole and other standard relationships.",
        "The method is to name the relationship of the given pair in one phrase before testing the options. The exam rewards that step, since the correct option must match the same relationship at the same level.",
    ]},
    {'slug': 'synonym-and-antonym', 'core': [
        "Synonym and antonym test precise vocabulary: the word closest in meaning and the word opposite in meaning. The exam asks the candidate to read carefully, because near-synonyms differ in shade.",
        "The method is to neutralise the options by meaning rather than by sound. The exam rewards knowing the exact shade each option carries and picking the closest, not a loosely related, word.",
    ]},
    {'slug': 'verbal-puzzle', 'core': [
        "Verbal puzzles dress logic in a story: neighbours in houses, friends in ranks, or students in seats, with a set of linked clues. The method is to convert the sentences into constraints and combine the strongest ones.",
        "The exam rewards writing the clues as notes or a table rather than holding them in the head. Constraint by constraint, the puzzle narrows until a single arrangement remains possible.",
    ]},
    {'slug': 'blood-relations', 'core': [
        "Blood relations map family links from sentences about fathers, mothers, sons, daughters and spouses, and ask for a stated relationship often at two or three removes. The method is to draw the family tree as you read.",
        "The exam rewards the diagram discipline: every person placed, every generation labelled. The answer follows from the tree, so the tree is what the candidate must build regardless of the wording.",
    ]},
    {'slug': 'statement-and-reasons', 'core': [
        "Statement and reasons gives a set of statements and proposed conclusions and asks which conclusion necessarily follows. The exam rewards reasoning strictly from the given statements without outside knowledge.",
        "The method is to judge each conclusion against the statements alone and to prefer the conclusion that follows necessarily rather than merely possibly. The exam rewards that distinction above vocabulary.",
    ]},
    {'slug': 'arithmetical-operation', 'core': [
        "Arithmetical operation redefines ordinary symbols with unusual meanings, such as a defined operation between two numbers, and asks the candidate to compute under the new rule. The method is to substitute the definition at every occurrence.",
        "The exam rewards applying the definition mechanically and in the given order, without letting conventional operator rules interfere. Reading the definition once and obeying its words answers the question.",
    ]},
    {'slug': 'number-series', 'core': [
        "Number series present a sequence with a hidden pattern in the differences, products or alternating rules, and ask for the next term. The method is to examine the gaps between consecutive terms first.",
        "The exam rewards writing the difference row before predicting. Most series yield to differences, and the pattern usually lives in that row, whether arithmetic, geometric or alternating.",
    ]},
    {'slug': 'alphabet-series', 'core': [
        "Alphabet series treat letters as positions on a circular wheel and hide the pattern in the gaps between successive positions. The method is to convert every letter to its number and read the sequence as a number series.",
        "The exam rewards the conversion and the circular awareness that the alphabet wraps after Z. The difference row, as with numbers, is where the answer lives.",
    ]},
    {'slug': 'continuous-patterns-and-positional-series', 'core': [
        "Continuous patterns repeat a block of letters, numbers or symbols with a twist after each cycle, and ask for the element at a given position. The method is to identify the repeating block and its cycle length.",
        "The exam rewards finding the block before counting positions: the position in the sequence locates the element inside the cycle. Working one block at a time keeps the pattern simple.",
    ]},
    {'slug': 'matrix-and-missing-characters', 'core': [
        "Matrix and missing characters present a grid where each row and column follows a rule, with one blank cell holding the missing entry. The method is to solve two complete lines to infer the rule before the blank.",
        "The exam rewards confirming the rule on a third line before applying it to the blank. Distinguishing row rules from column rules keeps the inference honest.",
    ]},
    {'slug': 'analogy', 'core': [
        "Analogy in the abstract context transforms a first pair into a second: the relationship between the first two items is repeated between the third and the missing one. The method is to name the transformation applied to the first pair.",
        "The exam rewards applying the same transformation exactly to the third item, in the same order. Naming the rule in a phrase before choosing answers the majority of the questions.",
    ]},
    {'slug': 'classification', 'core': [
        "Classification asks which item breaks the shared property of a group: the odd figure, number or word in a set with a common feature. The method is to identify the property that most of the items share.",
        "The exam rewards testing every option against the named property rather than a vague sense of similarity. The exception that breaks the strongest rule is the intended answer.",
    ]},
    {'slug': 'logical-sequence-of-words', 'core': [
        "Logical sequence of words arranges a set of words into a sensible order by size, stages, hierarchy or chronology, and asks for the sequence or the middle term. The method is to decide the dimension of the ordering first.",
        "The exam rewards fixing the ordering principle before comparing options. A sequence that makes sense at every adjacent step is the correct one, and the options rarely trap a candidate who has chosen the right dimension.",
    ]},
    {'slug': 'logical-venn-diagram', 'core': [
        "The logical Venn diagram matches sets of things, such as men, musicians and teachers, to the circle or region diagram that represents their overlap. The method is to decide which categories can include one another or overlap.",
        "The exam rewards reasoning about inclusion before comparing pictures: the diagram must show exactly which set contains which. Selecting by reasoned overlap rather than by shape answers the questions.",
        "A three-circle diagram can express eight distinct regions, one for every combination of membership in three sets, and most items in this topic ask which of those regions a described group belongs to.",
        "The steady habit of labelling each circle and each overlap before reading the options keeps the picture ordered when the sets grow to four or five, which is where careless solvers misplace a region.",
        "Concrete anchor sets, such as men, doctors and athletes, make inclusion obvious: some doctors are men, some athletes are men, and a few are both, so their regions must intersect accordingly.",
        "Turning the wording into the question 'which objects belong to which circle?' exposes the reasoning, and the diagram that matches that ownership is the answer.",
        "A common presentation gives a statement such as 'some students are artists and all artists are studious' and asks which diagram fits; drawing the two forced relationships first resolves it.",
        "The same logic transfers to numbers: the set of even numbers and the set of primes overlap at two, and a diagram that marks that single shared point is correct even if the circles look thinner than expected.",
        "Reading every option before settling matters here, because two diagrams can differ by a single region, and the difference is usually the clue that distinguishes the intended reading of the words.",
        "Reviewing the route once chosen - naming the one category that was included in another - replaces the guess with a defensible line, which is precisely the habit the solved sets demonstrate.",
    ]},
    {'slug': 'common-properties', 'core': [
        "Common properties looks for the trait shared by several given items and applies it to a missing choice, whether words, numbers or figures. The method is to state the property in one phrase and test every option against it.",
        "The exam rewards the same discipline as classification: a precise property named first prevents the drift toward vague similarity. The option sharing the strongest property is the answer.",
    ]},
    {'slug': 'series', 'core': [
        "The series topic generalises the pattern question across numbers, letters and mixed items, asking for the next term of a sequence whose rule is not announced. The method is to scan for the ordering principle before predicting.",
        "The exam rewards trying differences, ratios and alternations in order. Reading the full sequence and naming the pattern before computing keeps the answer grounded in the evidence.",
    ]},
    {'slug': 'classification-test', 'core': [
        "The classification test asks which figure or item does not belong in a given set, under time pressure and across varied representations. The method is to name the shared feature of the majority and identify the breaker.",
        "The exam rewards disciplined testing of each option against an explicit property. A clear, confirmable rule separates the correct choice from the plausible distractors.",
    ]},
    {'slug': 'analogy-2', 'core': [
        "The advanced analogy set extends the transform-a-pair skill to more demanding pairs, where the transformation may combine rotation, shading, position or number changes at once. The method is to decompose the transformation into its parts.",
        "The exam rewards tracking every independent change before applying it to the target. Applying the changes in the same order completes the analogy reliably.",
    ]},
    {'slug': 'matrix', 'core': [
        "The extended matrix set widens the grid-reasoning skill to figures across several rows, each governed by its own rule, with one blank cell to fill. The method is to solve row by row, confirming each rule.",
        "The exam rewards checking a candidate rule against a complete row before committing. The option that satisfies every confirmed rule is the answer.",
    ]},
    {'slug': 'figure-formation', 'core': [
        "Figure formation asks how two or more shapes combine into a definite whole: which option is the assembled figure made from the given pieces. The method is to trace the pieces mentally and match distinctive corners and proportions.",
        "The exam rewards exact matching over resemblance. Rejecting options that distort proportions or drop a piece keeps the selection disciplined.",
    ]},
    {'slug': 'construction-of-figure', 'core': [
        "Construction of figure identifies the single figure that can be built from a set of pieces, where every piece appears exactly once. The method is to verify each piece by its shape and orientation.",
        "The exam rewards checking that every given piece is present and none overlaps. The precise fit of the pieces, not their resemblance, decides the option.",
    ]},
    {'slug': 'analytic-reasoning-test', 'core': [
        "The analytic reasoning test bundles the serial logic of seating, ranking and scheduling, in which several linked clues fix one arrangement. The method is to write each clue as a constraint and combine the strongest first.",
        "The exam rewards disciplined note-taking and the elimination of arrangements that violate a single clue. The arrangement that survives every constraint is the answer.",
    ]},
    {'slug': 'grouping-figure', 'core': [
        "Grouping figure sorts a set of small figures into classes by shared features such as sides, symmetry or shading, and asks which option reproduces the correct grouping. The method is to pick a defining property and test the classes.",
        "The exam rewards grouping by one confirmable feature at a time. The option whose classes match the stated property is the answer.",
    ]},
    {'slug': 'paper-folding', 'core': [
        "Paper folding shows a sheet being folded, and often punched, and asks for the appearance when it is opened. The method is to unfold the paper step by step in the mind, or to use the fold symmetry.",
        "The exam rewards tracking the holes through each fold and applying the fold's symmetry. Matching hole positions after the complete unfolding chooses the option.",
    ]},
    {'slug': 'cube-and-dice', 'core': [
        "Cube and dice work out which faces are opposite when a net is folded, or which face appears after a roll. The method is to build the face map from the net and use the rule that adjacent faces are never opposite.",
        "The exam rewards the opposite-face map above visual guessing. Once opposite pairs are known, the visible faces in any orientation determine the hidden one.",
    ]},
    {'slug': 'embedded-figure', 'core': [
        "The embedded figure hides a target shape somewhere inside a larger drawing, and the exam asks where it lies. The method is to scan systematically, seeking the exact outline of the target.",
        "The exam rewards matching at least two distinctive corners of the target within the larger figure. Precision of outline, not general resemblance, completes the answer.",
    ]},
    {'slug': 'dot-situation', 'core': [
        "Dot situation places one or more dots that must fall inside a stated combination of overlapping regions of several figures. The method is to label every region before placing a dot.",
        "The exam rewards naming each region, inside A only, inside B only, or in the overlap, before matching the dots. The labelled map decides the correct place for each dot.",
    ]},
    {'slug': 'water-image-and-mirror-image', 'core': [
        "Water images and mirror images invert a figure: a mirror flips left and right, and water flips top and bottom. The method is to fix the axis of the flip before comparing options.",
        "The exam rewards testing a single asymmetric element of the figure, such as a notch, to verify the flip. The option matching the correct inversion is the answer.",
    ]},
]