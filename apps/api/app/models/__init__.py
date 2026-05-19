# Import all models so SQLModel.metadata knows about them
from app.models.exam_session import ExamSession
from app.models.listening_result import ListeningResult
from app.models.reading_result import ReadingResult
from app.models.review_log import VocabularyReviewLog
from app.models.review_task import ReviewTask
from app.models.vocabulary import VocabularyNote, VocabularyEntry
