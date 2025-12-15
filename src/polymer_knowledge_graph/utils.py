"""
Utility functions for the Polymer Knowledge Graph project.

This module provides helper functions for common tasks including:
- Data validation and cleaning
- File I/O operations
- Graph operations
- Logging and debugging
"""

import logging
import json
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import hashlib


# Configure module logger
logger = logging.getLogger(__name__)


class DataValidator:
    """Utility class for validating and cleaning data."""

    @staticmethod
    def validate_dict_keys(data: Dict[str, Any], required_keys: List[str]) -> bool:
        """
        Validate that a dictionary contains all required keys.

        Args:
            data: Dictionary to validate
            required_keys: List of required keys

        Returns:
            True if all required keys are present, False otherwise
        """
        return all(key in data for key in required_keys)

    @staticmethod
    def validate_not_empty(value: Any) -> bool:
        """
        Validate that a value is not empty.

        Args:
            value: Value to validate

        Returns:
            True if value is not empty, False otherwise
        """
        return value is not None and len(value) > 0

    @staticmethod
    def sanitize_string(text: str) -> str:
        """
        Sanitize a string by removing leading/trailing whitespace and normalizing.

        Args:
            text: String to sanitize

        Returns:
            Sanitized string
        """
        return text.strip() if isinstance(text, str) else ""


class FileOperations:
    """Utility class for file I/O operations."""

    @staticmethod
    def load_json(filepath: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Load JSON data from a file.

        Args:
            filepath: Path to JSON file

        Returns:
            Parsed JSON data or None if error occurs
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"File not found: {filepath}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON format in file: {filepath}")
            return None
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {str(e)}")
            return None

    @staticmethod
    def save_json(data: Dict[str, Any], filepath: Union[str, Path], 
                  indent: int = 2, overwrite: bool = False) -> bool:
        """
        Save data to a JSON file.

        Args:
            data: Data to save
            filepath: Destination file path
            indent: JSON indentation level
            overwrite: Whether to overwrite existing file

        Returns:
            True if successful, False otherwise
        """
        filepath = Path(filepath)
        
        if filepath.exists() and not overwrite:
            logger.warning(f"File already exists: {filepath}. Set overwrite=True to replace.")
            return False

        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            logger.info(f"Successfully saved data to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving file {filepath}: {str(e)}")
            return False

    @staticmethod
    def load_jsonl(filepath: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Load JSONL (JSON Lines) data from a file.

        Args:
            filepath: Path to JSONL file

        Returns:
            List of parsed JSON objects
        """
        data = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            data.append(json.loads(line))
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON at line {line_num} in {filepath}")
            return data
        except Exception as e:
            logger.error(f"Error reading JSONL file {filepath}: {str(e)}")
            return []


class GraphOperations:
    """Utility class for graph-related operations."""

    @staticmethod
    def create_node(node_id: str, node_type: str, attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a node dictionary for a knowledge graph.

        Args:
            node_id: Unique identifier for the node
            node_type: Type/category of the node
            attributes: Additional node attributes

        Returns:
            Node dictionary
        """
        node = {
            "id": node_id,
            "type": node_type,
            "attributes": attributes or {}
        }
        return node

    @staticmethod
    def create_edge(source_id: str, target_id: str, relation_type: str, 
                   attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create an edge dictionary for a knowledge graph.

        Args:
            source_id: Source node identifier
            target_id: Target node identifier
            relation_type: Type of relationship
            attributes: Additional edge attributes

        Returns:
            Edge dictionary
        """
        edge = {
            "source": source_id,
            "target": target_id,
            "relation": relation_type,
            "attributes": attributes or {}
        }
        return edge

    @staticmethod
    def validate_graph_structure(nodes: List[Dict], edges: List[Dict]) -> bool:
        """
        Validate the structure of a knowledge graph.

        Args:
            nodes: List of node dictionaries
            edges: List of edge dictionaries

        Returns:
            True if valid structure, False otherwise
        """
        try:
            node_ids = {node.get("id") for node in nodes}
            for edge in edges:
                source = edge.get("source")
                target = edge.get("target")
                if source not in node_ids or target not in node_ids:
                    logger.warning(f"Edge references non-existent nodes: {source} -> {target}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error validating graph structure: {str(e)}")
            return False


class HashOperations:
    """Utility class for hashing operations."""

    @staticmethod
    def compute_hash(data: str, algorithm: str = "sha256") -> str:
        """
        Compute hash of a string.

        Args:
            data: String to hash
            algorithm: Hash algorithm (default: sha256)

        Returns:
            Hexadecimal hash string
        """
        if algorithm == "sha256":
            return hashlib.sha256(data.encode()).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(data.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    @staticmethod
    def compute_file_hash(filepath: Union[str, Path], algorithm: str = "sha256") -> Optional[str]:
        """
        Compute hash of a file.

        Args:
            filepath: Path to file
            algorithm: Hash algorithm (default: sha256)

        Returns:
            Hexadecimal hash string or None if error occurs
        """
        try:
            if algorithm == "sha256":
                hash_obj = hashlib.sha256()
            elif algorithm == "md5":
                hash_obj = hashlib.md5()
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")

            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Error computing file hash for {filepath}: {str(e)}")
            return None


class StringOperations:
    """Utility class for string operations."""

    @staticmethod
    def split_camel_case(text: str) -> str:
        """
        Convert camelCase to space-separated words.

        Args:
            text: CamelCase string

        Returns:
            Space-separated string
        """
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', text)

    @staticmethod
    def to_snake_case(text: str) -> str:
        """
        Convert string to snake_case.

        Args:
            text: String to convert

        Returns:
            snake_case string
        """
        import re
        text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', text).lower()

    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncate text to a maximum length.

        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to append if truncated

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with standard configuration.

    Args:
        name: Logger name
        level: Logging level

    Returns:
        Configured logger instance
    """
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(level)

    if not logger_instance.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger_instance.addHandler(handler)

    return logger_instance


__all__ = [
    'DataValidator',
    'FileOperations',
    'GraphOperations',
    'HashOperations',
    'StringOperations',
    'setup_logger',
]
