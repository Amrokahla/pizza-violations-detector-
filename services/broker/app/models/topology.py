"""Alias for shared topology (broker setup uses same names as the task brief)."""

from shared.rabbitmq import TopologySettings as BrokerTopology

__all__ = ["BrokerTopology"]
