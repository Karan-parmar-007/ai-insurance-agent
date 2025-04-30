# Agent blueprint for agent-related API endpoints
from flask import Blueprint

agent_bp = Blueprint('agent', __name__)

from . import views
