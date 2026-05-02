# =============================================================================
# mi_m_t/models/__init__.py
# Import all ORM models to register them in the SQLAlchemy mapper registry.
# Required: FK resolution between models (e.g. stat_adj_by_id -> users.id)
# fails at first flush if target models are not yet imported.
# citation: SQLAlchemy docs — "configure mappers" pattern.
# =============================================================================
from mi_m_t.models.base import Base  # noqa: F401
from mi_m_t.models.project import Project  # noqa: F401
from mi_m_t.models.user import User  # noqa: F401
from mi_m_t.models.test_target import TestTarget  # noqa: F401
from mi_m_t.models.test_case import TestCase  # noqa: F401
from mi_m_t.models.request import Request  # noqa: F401
from mi_m_t.models.test_run import TestRun  # noqa: F401
from mi_m_t.models.item_status_history import ItemStatusHistory  # noqa: F401
from mi_m_t.models.item_status_transition import ItemStatusTransition  # noqa: F401
from mi_m_t.models.iteration_test_set import IterationTestSet  # noqa: F401
