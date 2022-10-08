from typing import Dict, List

import pandas as pd

from service_aggregator import get_clusters, get_topK_clusters, get_topK_news


def run_pipeline(
    corpus: pd.DataFrame,
    clusters: int,
    cluster_top_news: int,
    embedding_col: str,
    date_col: str,
) -> List[Dict[int, List[dict]]]:
    """Запуск пайплайна выделения кластеров и отбора новостей в кластере.

    Args:
        corpus (pd.DataFrame): датафрейм новостей.
            Должен содержать [дата, эмбединг]
        clusters (int): количество новостей на выходе.
        cluster_top_news (int): количество новостей на выходе.
        date_col (str, optional): название колонки с датой.
        embedding_col (str, optional): название колонки с эмбедингами.

    Returns:
        Dict[int, List[dict]] : кластеризованный корпус
    """
    corpus["cluster"] = get_clusters(corpus[embedding_col].to_list())
    clusters_index = get_topK_clusters(corpus, K=clusters, date_col=date_col)
    clustered_corpus = []
    for cluster in clusters_index:
        corpus_cluster = corpus[corpus["cluster"] == cluster]
        news_index = get_topK_news(
            corpus_cluster,
            K=cluster_top_news,
            date_col=date_col,
            embedding_col=embedding_col,
        )
        news_top = corpus_cluster.loc[news_index]
        clustered_corpus.append(
            {
                "trand_id": cluster,
                "trand_title": news_top.loc[news_index[0], "title"],
                "news": news_top.to_dict(orient="records"),
            }
        )
    return clustered_corpus
