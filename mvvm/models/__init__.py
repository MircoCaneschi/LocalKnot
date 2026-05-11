"""
Data Models for LocalKnot application.

Contains pure data classes representing domain entities without any GUI dependencies.
These models encapsulate the business logic and data validation.
"""


class Project:
    """
    Represents a Project entity.

    Attributes:
        name (str): Unique project name
        species (str): Associated species for this project
    """

    def __init__(self, name: str, species: str):
        """
        Initialize a Project.

        Args:
            name: Project identifier
            species: Species associated with the project
        """
        pass

    def validate_name(self, name: str) -> bool:
        """
        Validate project name according to business rules.

        Args:
            name: Project name to validate

        Returns:
            bool: True if valid, False otherwise
        """
        pass

    def __eq__(self, other):
        """Compare two projects by name."""
        pass

    def __repr__(self):
        """String representation of the project."""
        pass


class Species:
    """
    Represents a Species entity.

    Attributes:
        name (str): Unique species name
    """

    def __init__(self, name: str):
        """
        Initialize a Species.

        Args:
            name: Species identifier
        """
        pass

    def validate_name(self, name: str) -> bool:
        """
        Validate species name according to business rules.

        Args:
            name: Species name to validate

        Returns:
            bool: True if valid, False otherwise
        """
        pass

    def __eq__(self, other):
        """Compare two species by name."""
        pass


class Board:
    """
    Represents a Board entity within a Project.

    Attributes:
        board_no (int | str): Board identifier
        height (float): Board height measurement
        base (float): Board base measurement
        length (float): Board length measurement
        test_position (str): Test position reference
        comment (str): Additional notes about the board
    """

    def __init__(self, board_no: int | str, height: float = 0.0,
                 base: float = 0.0, length: float = 0.0,
                 test_position: str = "", comment: str = ""):
        """
        Initialize a Board.

        Args:
            board_no: Unique board identifier
            height: Height measurement
            base: Base measurement
            length: Length measurement
            test_position: Test position reference
            comment: Additional notes
        """
        pass

    def validate_measurements(self) -> bool:
        """
        Validate that all measurements are positive.

        Returns:
            bool: True if valid, False otherwise
        """
        pass


class Knot:
    """
    Represents a Knot entity within a Board.

    Attributes:
        knot_no (int | str): Knot identifier
        x (float): X coordinate position
        pith_z (float): Pith Z coordinate
        pith_y (float): Pith Y coordinate
        is_fake_pith (bool): Whether this is a fake pith
        comment (str): Additional notes about the knot
    """

    def __init__(self, knot_no: int | str, x: float = 0.0,
                 pith_z: float = 0.0, pith_y: float = 0.0,
                 is_fake_pith: bool = False, comment: str = ""):
        """
        Initialize a Knot.

        Args:
            knot_no: Unique knot identifier
            x: X coordinate
            pith_z: Pith Z coordinate
            pith_y: Pith Y coordinate
            is_fake_pith: Whether pith is fake
            comment: Additional notes
        """
        pass

    def validate_coordinates(self) -> bool:
        """
        Validate that coordinates are within acceptable ranges.

        Returns:
            bool: True if valid, False otherwise
        """
        pass

