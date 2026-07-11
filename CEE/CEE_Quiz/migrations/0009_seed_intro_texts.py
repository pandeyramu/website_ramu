from django.db import migrations

# ---------------------------------------------------------------------------
# Subject intro_texts
# ---------------------------------------------------------------------------
SUBJECT_INTROS = {
    'physics': (
        "Physics in the CEE exam carries 50 questions, making it one of the most important subjects in the entrance examination. "
        "The syllabus is divided into six major chapters: Mechanics (10 questions), Heat and Thermodynamics (7 questions), "
        "Waves and Optics (8 questions), Current Electricity and Magnetism (9 questions), Electrostatics and Capacitors "
        "(4 questions), and Modern Physics (12 questions). Mechanics and Modern Physics together account for nearly half "
        "of all Physics questions, so they deserve special attention during preparation.\n\n"
        "All questions are multiple-choice with a single correct answer, and there is a negative marking of 0.25 marks "
        "for every incorrect response. The Physics section tests both conceptual understanding and numerical problem-solving "
        "ability. Many questions require applying formulas to real-world scenarios, so practising a wide variety of numerical "
        "problems is essential.\n\n"
        "Below you will find all Physics chapters organised for focused practice. Each chapter has its own subtopics, "
        "chapter-wise MCQ tests with timers, and detailed solutions that explain the reasoning behind each correct answer. "
        "Regular practice with these resources will help you build both speed and accuracy for the actual CEE exam."
    ),
    'chemistry': (
        "Chemistry in the CEE exam carries 50 questions divided across five distinct areas: Physical Chemistry (17 questions), "
        "Inorganic Chemistry (10 questions), Organic Chemistry (17 questions), Applied Chemistry (3 questions), and "
        "Analytical Chemistry (3 questions). Physical Chemistry and Organic Chemistry together contribute 34 questions, "
        "more than two-thirds of the entire Chemistry section, making them the highest priority for revision.\n\n"
        "Physical Chemistry requires strong numerical skills in stoichiometry, thermodynamics, equilibrium, and "
        "electrochemistry. Organic Chemistry demands understanding of reaction mechanisms, functional group interconversions, "
        "and named reactions. Inorganic Chemistry covers periodic trends and chemical reactions of elements. Applied and "
        "Analytical Chemistry cover industrial processes and laboratory techniques.\n\n"
        "The negative marking of 0.25 marks per wrong answer applies across all Chemistry questions. Since Chemistry covers "
        "both numerical and theoretical content, a balanced study approach is the most effective strategy. Each chapter below "
        "links to targeted MCQ tests and detailed solution sets to help you prepare systematically."
    ),
    'zoology': (
        "Zoology in the CEE exam carries 40 questions, forming one half of the Biology section. "
        "The syllabus spans eight chapters: Evolutionary Biology (3 questions), Animal Diversity and Classification (4 questions), "
        "Animal Tissues and Histology (4 questions), Study of Selected Animals (6 questions), Human Biology and Physiology "
        "(15 questions), Microbial Diseases and Immunology (4 questions), Medical Technology and Applied Biology (2 questions), "
        "and Biota, Environment and Conservation (2 questions).\n\n"
        "Human Biology and Physiology is by far the most heavily weighted chapter, contributing 15 out of 40 Zoology questions. "
        "It covers the digestive, respiratory, circulatory, excretory, nervous, and reproductive systems, along with "
        "endocrinology and sense organs. Evolutionary Biology, Animal Diversity, and Animal Tissues each contribute "
        "3-4 questions and require mainly factual recall.\n\n"
        "Zoology questions in CEE range from straightforward factual recall to applied understanding of physiological "
        "processes and disease mechanisms. The chapter-wise MCQ tests below include detailed solutions to help you identify "
        "weak areas and strengthen your understanding before the exam."
    ),
    'botany': (
        "Botany in the CEE exam carries 40 questions, forming the second half of the Biology section alongside Zoology. "
        "The syllabus covers nine chapters: Basic Components of Life (2 questions), Biodiversity (9 questions), "
        "Ecology and Vegetation (4 questions), Cell Biology (5 questions), Genetics (6 questions), Plant Anatomy "
        "(3 questions), Plant Physiology (6 questions), Developmental Botany (2 questions), and Applied Botany (3 questions).\n\n"
        "Biodiversity is the highest-weightage chapter in Botany with 9 questions, covering the classification of "
        "living organisms from Monera through Angiosperms. Plant Physiology and Genetics contribute 6 questions each. "
        "Cell Biology, with 5 questions, also requires focused preparation.\n\n"
        "Botany questions test a combination of factual knowledge and conceptual understanding. The Medicinal Plants of "
        "Nepal topic is unique to the Nepali CEE syllabus and frequently appears in the exam. Use the chapter-wise MCQ "
        "tests below to practise each topic and review the detailed solutions provided."
    ),
}

# ---------------------------------------------------------------------------
# Chapter intro_texts
# ---------------------------------------------------------------------------
CHAPTER_INTROS = {
    'mechanics': "Mechanics contributes 10 questions to the CEE Physics section, making it the second most important chapter after Modern Physics. This chapter covers a wide range of topics from basic physical quantities and vectors to advanced rotational dynamics and elasticity. The subtopics include Physical Quantities, Vectors and Scalars; Kinematics; Dynamics; Rotational Dynamics; Fluid Statics and Dynamics; Circular and Periodic Motion; Gravity; and Elasticity. Mechanics questions in the CEE exam typically test your ability to apply Newton's laws, solve kinematics equations, understand rotational motion, and work with gravitational forces.",
    'heat-and-thermodynamics': "Heat and Thermodynamics contributes 7 questions to the CEE Physics section. This chapter covers six subtopics: Thermal Energy, Heat, Temperature and Thermometers; Thermal Expansion; Quantity of Heat; Ideal Gas; First Law of Thermodynamics; and Second Law of Thermodynamics. The questions range from conceptual understanding of temperature scales and thermal expansion to numerical problems involving specific heat capacity, latent heat, and the ideal gas equation.",
    'waves-and-optics': "Waves and Optics contributes 8 questions to the CEE Physics section. The chapter is divided into six subtopics: Wave Motion; Stationary Waves; Acoustic Phenomena; Reflection, Refraction and Dispersion; Interference; and Diffraction and Polarization. Wave Motion and Stationary Waves cover the basics of wave types, the wave equation, and standing wave patterns in strings and pipes.",
    'current-electricity-and-magnetism': "Current Electricity and Magnetism contributes 9 questions to the CEE Physics section. This chapter is divided into seven subtopics: Electrical Quantities; Electrical Circuits; Thermoelectric Effect; Alternating Currents; Magnetic Properties of Materials; Magnetic Field; and Electromagnetic Induction. Electrical circuits and electromagnetic induction are the most heavily tested areas.",
    'electrostatics-and-capacitors': "Electrostatics and Capacitors contributes 4 questions to the CEE Physics section. The chapter covers three subtopics: Electric Charge and Electric Field; Electric Field Strength, Potential and Potential Energy; and Capacitors. Though it is a smaller chapter, the concepts are foundational for understanding current electricity and magnetism.",
    'modern-physics': "Modern Physics contributes 12 questions to the CEE Physics section, the highest among all Physics chapters. It covers seven subtopics: Nuclear Physics; Electron; Photon and Photoelectric Effect; Wave Particle Duality and X-rays; Radioactivity; Solid and Semiconductor Devices; and Particle Physics and Recent Trends. Modern Physics is often considered scoring because many questions are based on standard formulas.",
    'physical-chemistry': "Physical Chemistry contributes 17 questions to the CEE Chemistry section, the highest among all Chemistry chapters. It covers 14 subtopics: Basic Concepts in Chemistry; Stoichiometry; Atomic Structure; Classification of Elements and Periodicity; Chemical Bonding and Shape of Molecules; Redox Reaction; States of Matter; Chemical Equilibrium; Volumetric Analysis; Ionic Equilibrium; Chemical Kinetics; Electrochemistry; Chemical Thermodynamics; and Nuclear Chemistry.",
    'inorganic-chemistry': "Inorganic Chemistry contributes 10 questions to the CEE Chemistry section. It covers three subtopics: Chemistry of Non-metals; Chemistry of Metals; and Bio-inorganic Chemistry. Inorganic Chemistry questions are primarily factual, requiring good memorisation of reactions, trends, and properties.",
    'organic-chemistry': "Organic Chemistry contributes 17 questions to the CEE Chemistry section, equal in weightage to Physical Chemistry. It covers 11 subtopics: General Organic Chemistry; Hydrocarbons; Aromatic Hydrocarbons; Haloalkanes and Haloarenes; Alcohols and Phenols; Ethers; Aldehydes and Ketones; Carboxylic Acid and its Derivatives; Nitro-compounds; Amines; and Organometallic Compounds.",
    'applied-chemistry': "Applied Chemistry contributes 3 questions to the CEE Chemistry section. It covers three subtopics: Manufacturing Processes; Applications of Non-metals, Metals and Compounds; and Chemistry in Service to Mankind. Though it contributes only 3 questions, these are often straightforward recall-based questions.",
    'analytical-chemistry': "Analytical Chemistry contributes 3 questions to the CEE Chemistry section. It covers three subtopics: Chemical Tests; Separation Techniques; and Types of Titration. The questions are typically based on standard laboratory procedures and observations.",
    'evolutionary-biology': "Evolutionary Biology contributes 3 questions to the CEE Zoology section. The chapter covers four subtopics: Origin of Life; Evidences of Evolution; Theories of Evolution; and Human Evolution. The questions are primarily factual, testing your knowledge of evolutionary concepts.",
    'animal-diversity-and-classification': "Animal Diversity and Classification contributes 4 questions to the CEE Zoology section. It covers the classification of the animal kingdom from Protozoa through Chordata, including the key characteristics of each phylum and class.",
    'animal-tissues-and-histology': "Animal Tissues and Histology contributes 4 questions to the CEE Zoology section. The chapter covers the four primary tissue types: epithelial, connective, muscular, and nervous tissues.",
    'study-of-selected-animals': "Study of Selected Animals contributes 6 questions to the CEE Zoology section. The chapter covers the detailed study of three organisms: Plasmodium, Earthworm (Pheretima), and Frog (Rana).",
    'human-biology-and-physiology': "Human Biology and Physiology contributes 15 questions to the CEE Zoology section, the highest weightage chapter in Zoology. It covers eight subtopics: Digestive System; Respiratory System; Circulatory System; Excretory System; Nervous System; Sense Organs; Endocrinology; and Reproductive System.",
    'microbial-diseases-and-immunology': "Microbial Diseases and Immunology contributes 4 questions to the CEE Zoology section. The chapter covers Microbial Diseases; Immunity; and Vaccines.",
    'medical-technology-and-applied-biology': "Medical Technology and Applied Biology contributes 2 questions to the CEE Zoology section. It covers Medical Technology and Applied Microbiology.",
    'biota-environment-and-conservation': "Biota, Environment and Conservation contributes 2 questions to the CEE Zoology section. It covers Animal Behavior; Environmental Pollution; Adaptations; and Conservation Biology.",
    'basic-components-of-life': "Basic Components of Life contributes 2 questions to the CEE Botany section. It covers Carbohydrates, Lipids and Minerals; and Proteins and Enzymes.",
    'biodiversity': "Biodiversity contributes 9 questions to the CEE Botany section, the highest weightage chapter in Botany. It covers 10 subtopics from Monera and Virus through Angiosperms, plus Economic Importance and Medicinal Plants of Nepal.",
    'ecology-and-vegetation': "Ecology and Vegetation contributes 4 questions to the CEE Botany section. It covers Ecosystem Ecology; Biogeochemical Cycles; and Vegetation and Adaptation.",
    'cell-biology': "Cell Biology contributes 5 questions to the CEE Botany section. It covers Prokaryotic and Eukaryotic Cells; Cell Organelles; and Cell Cycle and Cell Division.",
    'genetics': "Genetics contributes 6 questions to the CEE Botany section. It covers Genetic Material DNA and RNA; Mendelian Genetics and Linkage; Sex-linked Inheritance; and Mutation, Polyploidy and Genetic Disorders.",
    'plant-anatomy': "Plant Anatomy contributes 3 questions to the CEE Botany section. It covers Plant Tissues and Vascular Bundles; and Anatomy of Monocot and Dicot Root, Stem and Leaf.",
    'plant-physiology': "Plant Physiology contributes 6 questions to the CEE Botany section. It covers Water Relations; Photosynthesis; Respiration; and Plant Growth and Seed Germination.",
    'developmental-botany': "Developmental Botany contributes 2 questions to the CEE Botany section. It covers Reproduction and Sporogenesis in Angiosperms; and Embryo and Endosperm.",
    'applied-botany': "Applied Botany contributes 3 questions to the CEE Botany section. It covers Plant Tissue Culture; Genetic Engineering; and Biofertilizers and Food Security.",
}

# ---------------------------------------------------------------------------
# SubChapter intro_texts
# ---------------------------------------------------------------------------
SUBCHAPTER_INTROS = {
    'physical-quantities-vectors-and-scalars': "Physical quantities, vectors and scalars covers the fundamental concepts of physical quantities, measurement, SI units, dimensions, significant figures, and vector operations. Understanding these basics is essential for solving problems across all areas of mechanics and physics.",
    'kinematics': "Kinematics deals with the mathematical description of motion. The subtopic covers equations of motion, projectile motion, relative velocity, and graphical analysis of displacement, velocity, and acceleration.",
    'dynamics': "Dynamics explains the causes of motion through Newton's laws. This subtopic covers Newton's three laws, momentum, impulse, conservation of momentum, friction, and their applications.",
    'rotational-dynamics': "Rotational dynamics extends Newton's laws to rotational motion. Topics include torque, moment of inertia, angular momentum, conservation of angular momentum, and rolling motion.",
    'fluid-statics-and-dynamics': "Fluid statics and dynamics covers the mechanics of fluids at rest and in motion, including pressure, Pascal's law, Archimedes' principle, Bernoulli's principle, viscosity, and surface tension.",
    'circular-and-periodic-motion': "Circular motion covers centripetal acceleration and force, and banked curves. Periodic motion covers simple harmonic motion, energy relationships, and oscillatory systems.",
    'gravity': "Gravity covers Newton's law of gravitation, gravitational field and potential, Kepler's laws, and satellite motion including orbital and escape velocity.",
    'elasticity': "Elasticity covers stress, strain, Hooke's law, Young's modulus, bulk modulus, shear modulus, and the energy stored in a deformed body.",
    'thermal-energy-heat-temperature-and-thermometers': "Thermal energy, heat, temperature and thermometers covers the fundamental concepts of temperature scales, thermometric properties, and different types of thermometers.",
    'thermal-expansion': "Thermal expansion covers linear, superficial, and volumetric expansion of solids, expansion of liquids and gases, and the anomalous expansion of water.",
    'quantity-of-heat': "Quantity of heat covers specific heat capacity, heat capacity, latent heat, and the principle of heat exchange in calorimetry.",
    'ideal-gas': "Ideal gas covers the gas laws, the ideal gas equation, and the kinetic theory of gases including root mean square speed.",
    'first-law-of-thermodynamics': "First law of thermodynamics covers conservation of energy in thermodynamic systems, internal energy, work done by gases, and heat transfer in various thermodynamic processes.",
    'second-law-of-thermodynamics': "Second law of thermodynamics covers entropy, heat engines, refrigerators, heat pumps, and the Carnot cycle.",
    'wave-motion': "Wave motion covers the classification of waves, wave equation, wave speed, and energy transport by waves.",
    'stationary-waves': "Stationary waves covers standing waves in strings and air columns, nodes and antinodes, and resonant frequencies.",
    'acoustic-phenomena': "Acoustic phenomena covers the Doppler effect, beats, musical instruments, and characteristics of sound.",
    'reflection-refraction-and-dispersion': "Reflection, refraction and dispersion covers Snell's law, total internal reflection, lens formula, magnification, and dispersion through a prism.",
    'interference': "Interference covers Young's double-slit experiment, conditions for constructive and destructive interference, and fringe width calculation.",
    'diffraction-and-polarization': "Diffraction and polarization covers single-slit diffraction, diffraction grating, and polarized light including Brewster's law.",
    'electrical-quantities': "Electrical quantities covers electric current, potential difference, resistance, Ohm's law, resistivity, and factors affecting resistance.",
    'electrical-circuits': "Electrical circuits covers series and parallel combinations, Kirchhoff's laws, Wheatstone bridge, potentiometer, and meter bridge.",
    'thermoelectric-effect': "Thermoelectric effect covers Seebeck effect, Peltier effect, and thermocouples.",
    'alternating-currents': "Alternating currents covers RMS and peak values, AC circuits containing R, L, and C components, impedance, and power in AC circuits.",
    'magnetic-properties-of-materials': "Magnetic properties of materials covers diamagnetic, paramagnetic, and ferromagnetic materials, Curie temperature, and hysteresis.",
    'magnetic-field': "Magnetic field covers Biot-Savart law, Ampere's law, Lorentz force, and force between current-carrying conductors.",
    'electromagnetic-induction': "Electromagnetic induction covers Faraday's laws, Lenz's law, motional EMF, self and mutual induction, and transformers.",
    'electric-charge-and-electric-field': "Electric charge and electric field covers Coulomb's law, electric field, Gauss's law, and its applications.",
    'electric-field-strength-potential-and-potential-energy': "Electric field strength, potential and potential energy covers electric potential, equipotential surfaces, and potential energy of charge configurations.",
    'capacitors': "Capacitors covers capacitance, parallel plate capacitors, series and parallel combinations, energy stored, and dielectrics.",
    'nuclear-physics': "Nuclear physics covers atomic nucleus, nuclear forces, binding energy, nuclear reactions, and fission and fusion.",
    'electron': "The electron subtopic covers the discovery of the electron, Thomson's experiment, and Millikan's oil drop experiment.",
    'photon-and-photoelectric-effect': "Photon and photoelectric effect covers Einstein's photon theory, the photoelectric effect, threshold frequency, work function, and stopping potential.",
    'wave-particle-duality-and-x-rays': "Wave particle duality and X-rays covers de Broglie's hypothesis, Davisson-Germer experiment, X-ray production, and Bragg's law.",
    'radioactivity': "Radioactivity covers types of radioactive decay, law of radioactive decay, half-life, and radioactive series.",
    'solid-and-semiconductor-devices': "Solid and semiconductor devices covers energy bands, intrinsic and extrinsic semiconductors, p-n junction diodes, rectifiers, and transistors.",
    'particle-physics-and-recent-trends': "Particle physics and recent trends covers elementary particles, quarks, leptons, and fundamental forces.",
    'basic-concepts-in-chemistry': "Basic Concepts in Chemistry covers laws of chemical combination, atomic and molecular mass, mole concept, and percentage composition.",
    'stoichiometry': "Stoichiometry covers quantitative relationships in chemical reactions, limiting reagents, reaction yield, and concentration units.",
    'atomic-structure': "Atomic structure covers Bohr model, quantum mechanical model, quantum numbers, orbitals, and electronic configuration.",
    'classification-of-elements-and-periodicity': "Classification of elements and periodicity covers the periodic table, periodic trends in atomic radius, ionisation energy, and electronegativity.",
    'chemical-bonding-and-shape-of-molecules': "Chemical bonding and shape of molecules covers ionic, covalent, and metallic bonding, VSEPR theory, and hybridisation.",
    'redox-reaction': "Redox reaction covers oxidation and reduction, oxidation number, and balancing redox equations.",
    'states-of-matter': "States of matter covers the properties of solids, liquids, and gases, gas laws, kinetic molecular theory, and van der Waals equation.",
    'chemical-equilibrium': "Chemical equilibrium covers equilibrium constant, Le Chatelier's principle, and factors affecting equilibrium.",
    'volumetric-analysis': "Volumetric analysis covers titration principles, concentration units, indicators, and acid-base titration curves.",
    'ionic-equilibrium': "Ionic equilibrium covers dissociation of acids and bases, pH, buffers, hydrolysis, and solubility product.",
    'chemical-kinetics': "Chemical kinetics covers rate of reaction, rate laws, integrated rate equations, half-life, and Arrhenius equation.",
    'electrochemistry': "Electrochemistry covers electrolytic cells, Faraday's laws, electrochemical cells, Nernst equation, and electrochemical series.",
    'chemical-thermodynamics': "Chemical thermodynamics covers internal energy, enthalpy, Hess's law, entropy, Gibbs free energy, and spontaneity.",
    'nuclear-chemistry': "Nuclear chemistry covers radioactive decay, nuclear reactions, artificial transmutation, and radioisotopes.",
    'chemistry-of-non-metals': "Chemistry of non-metals covers the properties, preparation, and reactions of hydrogen, oxygen, nitrogen, halogens, and their compounds.",
    'chemistry-of-metals': "Chemistry of metals covers metallurgy, properties of s-block, p-block, d-block and f-block elements, and alloys.",
    'bio-inorganic-chemistry': "Bio-inorganic chemistry covers the role of metal ions in biological systems, including hemoglobin, chlorophyll, and essential trace elements.",
    'general-organic-chemistry': "General organic chemistry covers IUPAC nomenclature, isomerism, reaction intermediates, and electronic effects.",
    'hydrocarbons': "Hydrocarbons covers alkanes, alkenes, and alkynes, including preparation, properties, addition reactions, and polymerisation.",
    'aromatic-hydrocarbons': "Aromatic hydrocarbons covers benzene and its derivatives, aromaticity, and electrophilic aromatic substitution reactions.",
    'haloalkanes-and-haloarenes': "Haloalkanes and haloarenes covers alkyl and aryl halides, nucleophilic substitution, and elimination reactions.",
    'alcohols-and-phenols': "Alcohols and phenols covers preparation and reactions of alcohols and phenols, oxidation, dehydration, and acidic character.",
    'ethers': "Ethers covers the preparation of ethers, physical properties, and chemical reactions including cleavage by acids.",
    'aldehydes-and-ketones': "Aldehydes and ketones covers preparation, nucleophilic addition, oxidation and reduction, and the distinction between aldehydes and ketones.",
    'carboxylic-acid-and-its-derivatives': "Carboxylic acids and derivatives covers preparation, reactions, esterification, and derivative interconversions.",
    'nitro-compounds': "Nitro-compounds covers the preparation and reactions of nitroalkanes and nitroarenes, and reduction to amines.",
    'amines': "Amines covers classification, preparation, reactions, basicity, diazotisation, and coupling reactions.",
    'organometallic-compounds': "Organometallic compounds covers Grignard reagents, their preparation, and reactions with functional groups.",
    'manufacturing-processes': "Manufacturing processes covers industrial production of ammonia, sulfuric acid, sodium hydroxide, and cement.",
    'applications-of-non-metals-metals-and-compounds': "Applications of non-metals, metals and compounds covers practical applications of elements and compounds in industry and daily life.",
    'chemistry-in-service-to-mankind': "Chemistry in service to mankind covers the role of chemistry in health, agriculture, and environmental protection.",
    'chemical-tests': "Chemical tests covers identification of cations, anions, and gases through characteristic reactions.",
    'separation-techniques': "Separation techniques covers filtration, distillation, crystallization, chromatography, and solvent extraction.",
    'types-of-titration': "Types of titration covers acid-base, redox, complexometric, and precipitation titrations.",
    'origin-of-life': "Origin of life covers the theories on the origin of life, the Miller-Urey experiment, and the chemical evolution theory.",
    'evidences-of-evolution': "Evidences of evolution covers fossil records, homologous and analogous organs, vestigial organs, embryological evidence, and molecular evidence.",
    'theories-of-evolution': "Theories of evolution covers Lamarckism, Darwinism, and Neo-Darwinism including genetic drift and speciation.",
    'human-evolution': "Human evolution traces the ancestry of modern humans from primates through Australopithecus, Homo habilis, Homo erectus to Homo sapiens.",
    'animal-diversity-from-protozoa-to-chordata': "Animal diversity covers the classification and characteristics of the animal kingdom from Protozoa through Chordata.",
    'types-of-animal-tissues': "Types of animal tissues covers the four primary tissue types: epithelial, connective, muscular, and nervous tissues.",
    'plasmodium': "Plasmodium covers the life cycle of the malarial parasite, transmission by Anopheles mosquitoes, and symptoms of malaria.",
    'earthworm-pheretima': "Earthworm (Pheretima) covers morphology, digestive, circulatory, excretory, nervous, and reproductive systems.",
    'frog-rana': "Frog (Rana) covers external features, skeletal, digestive, respiratory, circulatory, excretory, nervous, and reproductive systems.",
    'digestive-system': "The digestive system covers the anatomy of the alimentary canal, digestive glands, and the physiology of digestion and absorption.",
    'respiratory-system': "The respiratory system covers the anatomy of the respiratory tract, mechanism of breathing, gas exchange, and transport of gases.",
    'circulatory-system': "The circulatory system covers the structure of the heart, cardiac cycle, blood vessels, blood composition, and blood pressure.",
    'excretory-system': "The excretory system covers the structure of the kidney, nephron, urine formation, and regulation of kidney function.",
    'nervous-system': "The nervous system covers the structure of neurons, nerve impulse propagation, central and peripheral nervous systems.",
    'sense-organs': "Sense organs covers the structure and function of the eye, ear, nose, tongue, and skin.",
    'endocrinology': "Endocrinology covers the endocrine glands, their hormones, and the mechanisms of hormone action and feedback regulation.",
    'reproductive-system': "The reproductive system covers male and female reproductive anatomy, gametogenesis, menstrual cycle, fertilisation, and contraception.",
    'microbial-diseases': "Microbial diseases covers bacterial, viral, protozoan, and fungal diseases, their causative agents, transmission, symptoms, and prevention.",
    'immunity': "Immunity covers innate and adaptive immunity, antigens, antibodies, and immune response mechanisms.",
    'vaccines': "Vaccines covers the principles of vaccination, types of vaccines, and the immunisation schedule.",
    'medical-technology': "Medical technology covers diagnostic techniques including X-rays, CT scans, MRI, ultrasound, ECG, and therapeutic technologies.",
    'applied-microbiology': "Applied microbiology covers industrial uses of microorganisms for producing antibiotics, vaccines, enzymes, and biotechnological products.",
    'animal-behavior': "Animal behavior covers innate and learned behaviour, migration, hibernation, and social behaviour in animals.",
    'environmental-pollution': "Environmental pollution covers air, water, soil, and noise pollution, their causes, effects, and control measures.",
    'adaptations': "Adaptations covers structural, physiological, and behavioural adaptations of animals to different environments.",
    'conservation-biology': "Conservation biology covers biodiversity hotspots, endangered species, protected areas, and conservation strategies.",
    'carbohydrates-lipids-and-minerals': "Carbohydrates, lipids and minerals covers the classification, structure, and functions of carbohydrates, lipids, and essential minerals.",
    'proteins-and-enzymes': "Proteins and enzymes covers amino acids, protein structure, enzyme classification, mechanism of action, and factors affecting activity.",
    'introduction-and-classification-systems': "Introduction and classification systems covers the need for classification, the five-kingdom and three-domain systems, and taxonomy.",
    'monera-and-virus': "Monera and virus covers the characteristics of bacteria, their economic importance, and the structure and replication of viruses.",
    'fungi-and-lichens': "Fungi and lichens covers the characteristics of fungi, their classification, reproduction, economic importance, and lichens as symbiotic associations.",
    'algae': "Algae covers the general characteristics, classification, life cycles of Spirogyra and Chlamydomonas, and economic importance.",
    'bryophytes': "Bryophytes covers the characteristics, classification, and life cycle of Marchantia and Funaria.",
    'pteridophytes': "Pteridophytes covers the characteristics, classification, and life cycle of ferns as the first vascular plants.",
    'gymnosperms': "Gymnosperms covers the characteristics, classification, and life cycle of Pinus and Cycas.",
    'angiosperms': "Angiosperms covers the characteristics, classification into monocots and dicots, and life cycle of flowering plants.",
    'economic-importance-of-plant-groups': "Economic importance covers useful and harmful aspects of different plant groups including food, medicine, and timber.",
    'medicinal-plants-of-nepal': "Medicinal plants of Nepal covers identification, active compounds, and uses of important medicinal plants found in Nepal.",
    'ecosystem-ecology': "Ecosystem ecology covers the structure and function of ecosystems, food chains, food webs, ecological pyramids, and energy flow.",
    'biogeochemical-cycles-and-ecological-imbalances': "Biogeochemical cycles covers carbon, nitrogen, phosphorus, and water cycles. Ecological imbalances covers eutrophication and global warming.",
    'vegetation-and-adaptation': "Vegetation and adaptation covers the vegetation types of Nepal and plant adaptations to different environments.",
    'prokaryotic-and-eukaryotic-cells': "Prokaryotic and eukaryotic cells covers the differences between both cell types and the structure of the plant cell.",
    'cell-organelles': "Cell organelles covers the structure and functions of the nucleus, mitochondria, chloroplasts, endoplasmic reticulum, Golgi apparatus, and ribosomes.",
    'cell-cycle-and-cell-division': "Cell cycle and cell division covers the stages of interphase, mitosis, and meiosis.",
    'genetic-material-dna-and-rna': "Genetic material covers the structure of DNA, RNA, DNA replication, transcription, translation, and the genetic code.",
    'mendelian-genetics-and-linkage': "Mendelian genetics covers Mendel's laws, monohybrid and dihybrid crosses, test cross, linkage, and crossing over.",
    'sex-linked-inheritance': "Sex-linked inheritance covers X-linked and Y-linked inheritance patterns and common sex-linked disorders.",
    'mutation-polyploidy-and-genetic-disorders': "Mutation, polyploidy and genetic disorders covers types of mutations, polyploidy in plants, and human genetic disorders.",
    'plant-tissues-and-vascular-bundles': "Plant tissues covers meristematic and permanent tissues, simple and complex tissues, and types of vascular bundles.",
    'anatomy-of-monocot-and-dicot-root-stem-and-leaf': "Anatomy of monocot and dicot root, stem and leaf covers the internal structures and differences between monocots and dicots.",
    'water-relations': "Water relations covers water potential, osmosis, plasmolysis, ascent of sap, transpiration, and water absorption.",
    'photosynthesis': "Photosynthesis covers light and dark reactions, C3 and C4 pathways, CAM pathway, and factors affecting photosynthesis.",
    'respiration': "Respiration covers aerobic and anaerobic respiration, glycolysis, Krebs cycle, electron transport chain, and oxidative phosphorylation.",
    'plant-growth-and-seed-germination': "Plant growth and seed germination covers growth phases, plant hormones, photoperiodism, and seed dormancy.",
    'reproduction-and-sporogenesis-in-angiosperms': "Reproduction and sporogenesis covers flower structure, microsporogenesis, megasporogenesis, pollination, and double fertilisation.",
    'embryo-and-endosperm': "Embryo and endosperm covers endosperm types, embryo development in dicots and monocots, and seed structure.",
    'plant-tissue-culture': "Plant tissue culture covers totipotency, micropropagation, callus culture, and applications in agriculture and horticulture.",
    'genetic-engineering': "Genetic engineering covers recombinant DNA technology, restriction enzymes, vectors, gene cloning, and PCR.",
    'biofertilizers-and-food-security': "Biofertilizers covers Rhizobium, Azotobacter, cyanobacteria, and mycorrhizae. Food security covers sustainable agriculture and biotechnology.",
}

# ---------------------------------------------------------------------------
# Migration functions
# ---------------------------------------------------------------------------


def seed_intro_texts(apps, schema_editor):
    Subject = apps.get_model('CEE_Quiz', 'Subject')
    Chapter = apps.get_model('CEE_Quiz', 'Chapter')
    SubChapter = apps.get_model('CEE_Quiz', 'SubChapter')

    for slug, text in SUBJECT_INTROS.items():
        Subject.objects.filter(slug=slug).update(intro_text=text)

    for slug, text in CHAPTER_INTROS.items():
        Chapter.objects.filter(slug=slug).update(intro_text=text)

    for slug, text in SUBCHAPTER_INTROS.items():
        SubChapter.objects.filter(slug=slug).update(intro_text=text)


def delete_intro_texts(apps, schema_editor):
    Subject = apps.get_model('CEE_Quiz', 'Subject')
    Chapter = apps.get_model('CEE_Quiz', 'Chapter')
    SubChapter = apps.get_model('CEE_Quiz', 'SubChapter')

    Subject.objects.all().update(intro_text='')
    Chapter.objects.all().update(intro_text='')
    SubChapter.objects.all().update(intro_text='')


class Migration(migrations.Migration):

    dependencies = [
        ('CEE_Quiz', '0008_seed_solution_sets'),
    ]

    operations = [
        migrations.RunPython(seed_intro_texts, delete_intro_texts),
    ]
