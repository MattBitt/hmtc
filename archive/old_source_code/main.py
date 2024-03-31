from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from db import Base, engine
from my_logging import setup_logging
from configs import cnf
from source_data import update_sources_in_db, download_sources, verify_files_exist
from track_creator import create_all_tracks
from routers import (
    source_router,
    track_router,
    album_router,
    word_router,
    producer_router,
    tag_router,
    beat_router,
    artist_router,
    whatsplaying_router,
)


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.0.202:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(source_router)
app.include_router(track_router)
app.include_router(album_router)
app.include_router(word_router)
app.include_router(producer_router)
app.include_router(tag_router)
app.include_router(beat_router)
app.include_router(artist_router)
app.include_router(whatsplaying_router)


# Should include a health check for the postgres db
# had a situation where nothing was working, because the db
# needed to be restarted


if __name__ == "__main__":
    logger = setup_logging()
    logger.info("Starting program version: {}".format(cnf.APP_VER))
    logger.debug("The current environment is {}".format(cnf.ENV_STATE))
    logger.debug("Log Level is currently {}".format(cnf.LOG_LEVEL))
    Base.metadata.create_all(bind=engine)
    if not (cnf.ENV_STATE == "dev" and not cnf.APP_CONFIG.import_during_testing):
        logger.info("Searching all channels for new videos")
        update_sources_in_db()
    if not (cnf.ENV_STATE == "dev" and not cnf.APP_CONFIG.download_during_testing):
        logger.info("Downloading any missing media from the sources db")
        download_sources()
    if not (cnf.ENV_STATE == "dev" and not cnf.APP_CONFIG.create_tracks_during_testing):
        create_all_tracks()
    verify_files_exist()

    uvicorn.run(
        "main:app",
        host=cnf.SERVER_HOST,
        port=int(cnf.SERVER_PORT),
        reload=True,
    )
