from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import accounts, catalog, content, favorites, analytics, operations
from .observability import install_observability
# Backwards-compatible import for the existing test suite.
from .services.accounts import attempts

app = FastAPI(title='QUAN 1 TOURISM API', version='1.3.0')
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(','),
    allow_methods=['GET','POST','PUT','DELETE'],
    allow_headers=['Authorization','Content-Type','Idempotency-Key','X-Consent-Token','X-Request-ID'], expose_headers=['X-Request-ID'])
install_observability(app)
for module in (accounts, catalog, content, favorites, analytics, operations):
    app.include_router(module.router)
