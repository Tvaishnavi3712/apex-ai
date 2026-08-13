"""
Document Classification Action
Classify documents using Claude vision to determine document type and matching blueprint
"""

from .handler import document_classify, handler

__all__ = ['document_classify', 'handler']
