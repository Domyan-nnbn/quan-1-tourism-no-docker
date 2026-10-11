from ..repositories import operations as repo
from ..config import settings
from ..observability import snapshot

def readiness(db):
    try:
        checks=repo.checks(db)
    except Exception:
        db.rollback()
        checks={'database':False,'schema':False,'worker':False}
    ready=checks['database'] and checks['schema'] and (checks['worker'] or not settings.worker_required)
    return ready, {'status':'ready' if ready else 'not_ready','database':'postgresql',
                   'checks':checks,'worker_required':settings.worker_required}

def metrics(db):
    return {'http':snapshot(),'jobs':repo.job_counts(db)}
