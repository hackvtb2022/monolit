from dependency_injector import containers, providers

from service_insights.pipeline import Pipeline


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["service_api.api.router"])
    insights = providers.Singleton(
        Pipeline,
    )
