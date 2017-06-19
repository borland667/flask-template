import logging

from restify.application import create_app, get_config

module_logger = logging.getLogger(__name__)

application = create_app(get_config('restify.config.Production'))
