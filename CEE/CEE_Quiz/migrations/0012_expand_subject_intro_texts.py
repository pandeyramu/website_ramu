from django.db import migrations

SUBJECT_INTRO_EXTRAS = {
    'physics': (
        "\n\nPhysics in the CEE is known for its numerical and application-based questions. "
        "Unlike pure recall, most Physics problems require you to identify the right formula, "
        "substitute values correctly, and interpret the result in the context of the question. "
        "Topics like projectile motion, electrical circuits, and wave interference appear repeatedly "
        "because they combine multiple concepts in a single problem. Working through a large variety "
        "of numerical problems is the most effective way to prepare, because the same underlying "
        "principle can appear in many different disguises on exam day.\n\n "
        "A useful strategy is to divide your Physics preparation into three phases. First, build a "
        "strong conceptual foundation by studying each chapter's theory and key formulas. Second, "
        "solve chapter-wise MCQs under timed conditions to build speed and accuracy. Third, mix "
        "questions from different chapters in a single practice session to simulate the real exam, "
        "where you must switch between Mechanics, Optics, Electricity, and Modern Physics without "
        "warning. Pay special attention to units, sign conventions, and dimensional analysis — "
        "these small details account for a significant number of incorrect answers in the actual exam."
    ),
    'chemistry': (
        "\n\nThe CEE Chemistry section demands two very different study approaches depending on the "
        "branch. Physical Chemistry problems are numerical and formula-driven, requiring you to work "
        "through calculations involving molarity, enthalpy, equilibrium constants, and electrochemical "
        "cells. Organic Chemistry, on the other hand, tests your understanding of reaction mechanisms, "
        "functional group transformations, and the ability to predict products of unfamiliar reactions "
        "using pattern recognition. Inorganic Chemistry relies more on factual recall of periodic "
        "trends, coordination compounds, and qualitative analysis.\n\n "
        "An effective preparation strategy is to keep a reaction map for Organic Chemistry that links "
        "functional groups through common transformations. For Physical Chemistry, maintain a formula "
        "sheet organised by topic and practise applying each formula to at least three different "
        "problem types. Inorganic Chemistry benefits from repeated revision rather than long study "
        "sessions — short, frequent review sessions help transfer factual details into long-term "
        "memory. Practising chapter-wise MCQs on this platform reinforces these habits, and the "
        "detailed solutions explain not just the correct answer but why the other options are wrong, "
        "which is often where the real learning happens."
    ),
    'zoology': (
        "\n\nZoology carries the heaviest single-chapter weightage in the entire CEE syllabus: "
        "Human Biology and Physiology alone accounts for 15 out of 40 Zoology questions. This "
        "chapter covers the digestive, respiratory, circulatory, excretory, nervous, and reproductive "
        "systems, along with endocrinology and sense organs. Questions in this area often test your "
        "ability to trace physiological pathways — for example, following the route of blood through "
        "the heart, or explaining how a nerve impulse travels from stimulus to response. Diagram-based "
        "questions and sequence-based questions are common here.\n\n "
        "For the remaining Zoology chapters, a factual recall approach works best. Animal Diversity "
        "and Classification require you to memorise key characteristics of major phyla, while Animal "
        "Tissues and Histology demand familiarity with tissue types and their functions. Microbial "
        "Diseases and Immunology frequently appears in CEE as applied questions linking a pathogen "
        "to its disease, transmission method, and prevention. The most efficient preparation method "
        "is to work through chapter-wise MCQs after studying each topic, focusing on the solutions "
        "to questions you get wrong. This targeted revision approach helps you identify and fix "
        "knowledge gaps before the exam rather than passively rereading textbook notes."
    ),
    'botany': (
        "\n\nBotany accounts for 40 questions in the CEE and rewards both conceptual understanding "
        "and precise factual knowledge. Biodiversity is the highest-weightage chapter with 9 questions, "
        "covering the classification of organisms from Monera through Angiosperms. Plant Physiology "
        "and Genetics each contribute 6 questions and require you to understand processes like "
        "photosynthesis, transpiration, Mendelian inheritance, and gene expression at a level that "
        "goes beyond simple memorisation.\n\n "
        "A key challenge in Botany is the breadth of factual detail you need to remember — from the "
        "classification hierarchy of plant kingdoms to the specific steps of the Calvin cycle. "
        "Concept maps and comparison tables are particularly useful here because Botany questions "
        "often test your ability to distinguish between similar processes or structures. For example, "
        "you may need to compare C3 and C4 photosynthesis, or differentiate between mitosis and "
        "meiosis at specific stages. The Medicinal Plants of Nepal topic is unique to the Nepali CEE "
        "syllabus and frequently appears in the exam, so do not skip it. Practising the chapter-wise "
        "MCQs on this platform after studying each topic helps transfer facts from short-term to "
        "long-term memory, and reviewing the detailed solutions reveals common traps that catch "
        "students in the actual exam."
    ),
}


def forwards(apps, schema_editor):
    Subject = apps.get_model('CEE_Quiz', 'Subject')
    for slug, extra in SUBJECT_INTRO_EXTRAS.items():
        try:
            subject = Subject.objects.get(slug=slug)
        except Subject.DoesNotExist:
            continue
        base = (subject.intro_text or '').rstrip()
        if extra.strip() in base:
            continue
        subject.intro_text = base + extra
        subject.save(update_fields=['intro_text'])


def reverse(apps, schema_editor):
    Subject = apps.get_model('CEE_Quiz', 'Subject')
    for slug, extra in SUBJECT_INTRO_EXTRAS.items():
        try:
            subject = Subject.objects.get(slug=slug)
        except Subject.DoesNotExist:
            continue
        if subject.intro_text and extra.strip() in subject.intro_text:
            subject.intro_text = subject.intro_text.replace(extra, '').rstrip()
            subject.save(update_fields=['intro_text'])


class Migration(migrations.Migration):

    dependencies = [
        ('CEE_Quiz', '0011_expand_intro_texts'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse),
    ]
