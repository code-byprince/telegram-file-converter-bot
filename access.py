from utils import stats
from config import ADMIN_ID


def has_access(user_id: int) -> bool:
    """Admin ko hamesha access hai, baaki users ko donate karne ke baad access milta hai."""
    if ADMIN_ID and user_id == ADMIN_ID:
        return True
    return stats.is_user_paid(user_id)
