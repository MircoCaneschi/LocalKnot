"""
View Models Package.

Contains all ViewModel classes that manage presentation state.

ViewModels have these responsibilities:
- Expose Qt Properties for two-way binding with Views
- Emit Signals to notify Views of state changes
- Provide Slots to handle user interactions from Views
- Contain NO dependencies on QtWidgets (pure business/presentation logic)
- Transform Model data into presentation-ready format
"""

from .projects_viewmodel import ProjectsViewModel
from .boards_viewmodel import BoardsViewModel
from .knots_viewmodel import KnotsViewModel

__all__ = [
    'ProjectsViewModel',
    'BoardsViewModel',
    'KnotsViewModel',
]

