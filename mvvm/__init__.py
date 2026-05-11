"""
MVVM Architecture Module.

This module organizes the application into Model, ViewModel, and View layers,
ensuring strict separation of concerns and one-way data flow:

- Model: Pure business logic and data
- ViewModel: Presentation state management with Properties and Signals
- View: UI components that bind to ViewModels

No circular dependencies between layers.
"""

