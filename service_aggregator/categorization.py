from typing import List

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def get_similarity_score(
    corpus_embeddings: List[str],
    role_embedding: List[float],
) -> List[float]:
    """Считает близость описания роли и новости"""
    return cosine_similarity(role_embedding, corpus_embeddings)


def get_filtered_by_role(
    corpus_embeddings: List[str],
    role_embedding: List[float],
    threshold: float = 0.1,
) -> List[int]:
    """Фильтрует новости по схожести с описанием роли.

    Args:
        corpus_embeddings (List[str]): Список с эмбедингами новостей
        role_embedding (List[float]): Эмбединг описания роли
        threshold (float, optional): граница фильтрации. Defaults to 0.1.

    Returns:
        List[int]: Возвращает индексы отфильтрованных новостей.
    """
    scores = get_similarity_score(
        corpus_embeddings=corpus_embeddings, role_embedding=role_embedding
    )
    return np.argwhere(scores > threshold)[:, 1]
