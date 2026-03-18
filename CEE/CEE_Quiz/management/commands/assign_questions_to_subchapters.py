import json
import re
from collections import defaultdict
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from CEE_Quiz.models import Chapter, Question, SubChapter


STOP_WORDS = {
    "and", "or", "the", "of", "in", "to", "for", "with", "on", "at", "from", "by",
    "its", "their", "his", "her", "a", "an", "is", "are", "as", "into", "through",
    "group", "family", "state", "states", "compound", "compounds", "chemistry", "biology",
    "physics", "chapter", "part", "section", "i", "ii", "iii", "iv",
}


MANUAL_HINTS = {
    "newton's laws of motion": ["newton", "inertia", "momentum", "action reaction", "f=ma"],
    "work, energy, power and collision": ["work", "energy", "power", "collision", "kinetic energy", "potential energy"],
    "gravitation": ["gravitation", "gravity", "g", "escape velocity", "orbital"],
    "simple harmonic motion": ["shm", "simple harmonic", "oscillation", "time period", "amplitude"],
    "thermodynamics": ["thermodynamics", "enthalpy", "entropy", "first law", "second law"],
    "electrochemistry": ["electrode", "electrolysis", "electrochemical", "galvanic", "emf", "cell potential"],
    "chemical kinetics": ["rate constant", "order of reaction", "arrhenius", "half life", "activation energy"],
    "chemical equilibrium": ["equilibrium constant", "le chatelier", "kc", "kp"],
    "ionic equilibrium": ["ph", "poh", "buffer", "hydrolysis", "solubility product", "ka", "kb"],
    "hydrocarbons": ["alkane", "alkene", "alkyne", "benzene", "hydrocarbon"],
    "halogen derivatives": ["alkyl halide", "haloalkane", "halogen"],
    "alcohol": ["alcohol", "ethanol", "methanol"],
    "phenols": ["phenol"],
    "ether": ["ether", "williamson synthesis"],
    "carbonyl compounds": ["aldehyde", "ketone", "carbonyl"],
    "carboxylic compounds and their derivatives": ["carboxylic", "ester", "amide", "acyl", "anhydride"],
    "compounds containing nitrogen": ["amine", "diazonium", "nitro"],
    "genetics: inheritance and variation": ["mendel", "allele", "genotype", "phenotype", "monohybrid", "dihybrid"],
    "cell biology": ["cell organelle", "mitochondria", "ribosome", "membrane"],
    "photosynthesis": ["chlorophyll", "light reaction", "calvin cycle", "photosynthesis"],
    "respiration": ["glycolysis", "krebs", "atp", "respiration"],
    "nervous system": ["neuron", "synapse", "cns", "brain", "spinal cord"],
    "cardiovascular system": ["heart", "blood pressure", "artery", "vein", "cardiac"],
    "respiratory system": ["alveoli", "lungs", "respiration", "trachea"],
    "digestive system": ["digestion", "enzyme", "stomach", "intestine", "liver"],
    "reproductive system": ["spermatogenesis", "oogenesis", "menstrual", "fertilization"],
}


def normalize_text(value):
    cleaned = re.sub(r"[^a-z0-9\s]", " ", value.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def tokenize(value):
    return [
        token for token in normalize_text(value).split()
        if len(token) >= 3 and token not in STOP_WORDS
    ]


class Command(BaseCommand):
    help = (
        "Auto-assign existing questions to subchapters using keyword scoring. "
        "Default is dry-run; pass --apply to save updates."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply changes to database. Without this flag, command runs in dry-run mode.",
        )
        parser.add_argument(
            "--chapter-id",
            action="append",
            type=int,
            help="Restrict processing to one or more chapter IDs (repeatable).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit number of questions processed per chapter (0 = no limit).",
        )
        parser.add_argument(
            "--mapping-file",
            type=str,
            default="",
            help=(
                "Optional JSON file to add custom hints. Format: "
                "{\"<chapter_id>\": {\"<subchapter name>\": [\"keyword1\", ...]}}"
            ),
        )
        parser.add_argument(
            "--sample-unmatched",
            type=int,
            default=5,
            help="How many unmatched/ambiguous question IDs to print per chapter.",
        )

    def _load_custom_hints(self, mapping_file):
        if not mapping_file:
            return {}

        path = Path(mapping_file).resolve()
        if not path.exists():
            raise CommandError(f"Mapping file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON in mapping file: {exc}") from exc

        if not isinstance(data, dict):
            raise CommandError("Mapping file root must be an object.")

        parsed = {}
        for chapter_id_raw, chapter_map in data.items():
            try:
                chapter_id = int(chapter_id_raw)
            except (TypeError, ValueError) as exc:
                raise CommandError(f"Invalid chapter id in mapping file: {chapter_id_raw}") from exc

            if not isinstance(chapter_map, dict):
                raise CommandError(f"Chapter mapping for {chapter_id} must be an object.")

            parsed[chapter_id] = {}
            for sub_name, hints in chapter_map.items():
                if not isinstance(hints, list):
                    raise CommandError(f"Hints for subchapter '{sub_name}' must be a list.")
                parsed[chapter_id][normalize_text(str(sub_name))] = [normalize_text(str(item)) for item in hints]

        return parsed

    def _build_subchapter_profile(self, chapter, custom_hints):
        profiles = []
        chapter_custom = custom_hints.get(chapter.id, {})

        for sub in SubChapter.objects.filter(chapter=chapter).order_by("order", "id"):
            sub_name_norm = normalize_text(sub.name)
            keywords = set(tokenize(sub.name))
            for hint in MANUAL_HINTS.get(sub_name_norm, []):
                keywords.update(tokenize(hint))
            for hint in chapter_custom.get(sub_name_norm, []):
                keywords.update(tokenize(hint))

            phrase_hints = [sub_name_norm]
            phrase_hints.extend([normalize_text(h) for h in MANUAL_HINTS.get(sub_name_norm, [])])
            phrase_hints.extend(chapter_custom.get(sub_name_norm, []))

            profiles.append({
                "sub": sub,
                "keywords": keywords,
                "phrases": [p for p in phrase_hints if p],
            })

        return profiles

    def _score_question(self, question_text_norm, question_tokens, profile):
        score = 0
        token_set = set(question_tokens)

        for phrase in profile["phrases"]:
            if phrase and phrase in question_text_norm:
                score += 5

        score += len(token_set.intersection(profile["keywords"]))
        return score

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        chapter_ids = options.get("chapter_id") or []
        limit = options["limit"]
        sample_unmatched = options["sample_unmatched"]
        custom_hints = self._load_custom_hints(options["mapping_file"])

        chapters_qs = Chapter.objects.filter(has_subchapters=True).order_by("id")
        if chapter_ids:
            chapters_qs = chapters_qs.filter(id__in=chapter_ids)

        chapters = list(chapters_qs)
        if not chapters:
            self.stdout.write(self.style.WARNING("No chapters found to process."))
            return

        self.stdout.write(
            self.style.WARNING("RUN MODE: APPLY") if apply_changes else self.style.WARNING("RUN MODE: DRY-RUN")
        )

        total_processed = 0
        total_assigned = 0
        total_ambiguous = 0
        total_unmatched = 0

        for chapter in chapters:
            profiles = self._build_subchapter_profile(chapter, custom_hints)
            if not profiles:
                self.stdout.write(self.style.WARNING(f"\nChapter {chapter.id}: {chapter.name} -> no subchapters, skipped"))
                continue

            questions_qs = Question.objects.filter(chapter=chapter, sub_chapter__isnull=True).order_by("id")
            if limit and limit > 0:
                questions_qs = questions_qs[:limit]
            questions = list(questions_qs)

            if not questions:
                self.stdout.write(f"\nChapter {chapter.id}: {chapter.name} -> 0 unassigned questions")
                continue

            to_update = []
            ambiguous_ids = []
            unmatched_ids = []

            for question in questions:
                question_text_norm = normalize_text(question.question_text or "")
                question_tokens = tokenize(question.question_text or "")

                scores = []
                for profile in profiles:
                    score = self._score_question(question_text_norm, question_tokens, profile)
                    scores.append((score, profile["sub"]))

                scores.sort(key=lambda item: item[0], reverse=True)
                top_score = scores[0][0]

                if top_score <= 0:
                    unmatched_ids.append(question.id)
                    continue

                top_matches = [sub for score, sub in scores if score == top_score]
                if len(top_matches) != 1:
                    ambiguous_ids.append(question.id)
                    continue

                question.sub_chapter = top_matches[0]
                to_update.append(question)

            if apply_changes and to_update:
                Question.objects.bulk_update(to_update, ["sub_chapter"])

            processed_count = len(questions)
            assigned_count = len(to_update)
            ambiguous_count = len(ambiguous_ids)
            unmatched_count = len(unmatched_ids)

            total_processed += processed_count
            total_assigned += assigned_count
            total_ambiguous += ambiguous_count
            total_unmatched += unmatched_count

            self.stdout.write(
                f"\nChapter {chapter.id}: {chapter.name}\n"
                f"  Processed: {processed_count}\n"
                f"  Assigned: {assigned_count}\n"
                f"  Ambiguous: {ambiguous_count}\n"
                f"  Unmatched: {unmatched_count}"
            )

            if ambiguous_ids and sample_unmatched > 0:
                self.stdout.write(f"  Ambiguous sample IDs: {ambiguous_ids[:sample_unmatched]}")
            if unmatched_ids and sample_unmatched > 0:
                self.stdout.write(f"  Unmatched sample IDs: {unmatched_ids[:sample_unmatched]}")

        self.stdout.write(self.style.SUCCESS(
            "\nSummary\n"
            f"  Total processed: {total_processed}\n"
            f"  Total assigned: {total_assigned}\n"
            f"  Total ambiguous: {total_ambiguous}\n"
            f"  Total unmatched: {total_unmatched}"
        ))

        if not apply_changes:
            self.stdout.write(self.style.WARNING(
                "Dry-run finished. Re-run with --apply to save assignments."
            ))
