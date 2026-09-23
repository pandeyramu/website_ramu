from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Question, SolutionSet


def _invalidate_solution_set_caches(question_id):
    for ss in SolutionSet.objects.exclude(question_ids=''):
        ids = [int(x.strip()) for x in ss.question_ids.split(',') if x.strip().isdigit()]
        if question_id in ids:
            cache.delete(f'solset_qids:{ss.id}')


@receiver(post_save, sender=Question)
def invalidate_question_caches(sender, instance, **kwargs):
    cache.delete(f'chapter_qids:{instance.chapter_id}')
    if instance.sub_chapter_id:
        cache.delete(f'subchapter_qids:{instance.sub_chapter_id}')
    _invalidate_solution_set_caches(instance.id)


@receiver(post_delete, sender=Question)
def invalidate_question_caches_on_delete(sender, instance, **kwargs):
    cache.delete(f'chapter_qids:{instance.chapter_id}')
    if instance.sub_chapter_id:
        cache.delete(f'subchapter_qids:{instance.sub_chapter_id}')
    _invalidate_solution_set_caches(instance.id)