from abc import ABC, abstractmethod
from core.ai.ai_models import AIAnalysisResult

class BaseAIAnalyzer(ABC):
    @abstractmethod
    def load_model(self) -> None:
        """Loads the AI model into memory."""
        pass

    @abstractmethod
    def analyze(self, image_path: str, board_length: int, board_base: int, board_height: int) -> AIAnalysisResult:
        """
        Analyzes the image and returns the standardized results.
        :param image_path: Path to the board image.
        :param board_length: Physical length of the board (used for proportion).
        :param board_base: Physical base of the board.
        :param board_height: Physical height of the board.
        """
        pass
