# overall url_source manager
#
#   manage persistent sate

from loguru import logger

from url_source import UrlSource, UrlSources
from url_source_parsers import sources_config
from url_source_validator import UrlSourceValidator

from directory_cache import DirectoryCache
from change_list import ChangeList

class UrlSourceManager():

    def __init__(self, cache: DirectoryCache):
        self.cache = cache
        self.change_list = None

    def update_sources(self) -> UrlSources:

        self.change_list = ChangeList(self.cache)
        self.change_list.load()

        self.change_list.start_run()

        sources = UrlSources()
        sources.scan(sources_config)
        sources.read(self.cache, "sources.txt")
        
        validator = UrlSourceValidator()
        for src in sources.items:
            sources.update_from_remote(src.name)
            if validator.validate(src):
                logger.info(f"   {src.name}: save")
                src.write(src.name, self.cache, self.change_list)
                logger.info(f"   {src.name}: updated from remote")
            else:
                validator.display_status()
                if src.read(src.name, self.cache):
                    logger.warning(f"   {src.name}: use local cache")
                else:
                    self.change_list.record_failed(src.name, "source", src.endpoint, "no local cache")
    
        sources.write(self.cache, "sources.txt")
        self.change_list.finish_run()