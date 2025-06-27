import logging
import os
import sys
from datetime import datetime

def setup_logger(name=__name__, log_level=logging.INFO, log_dir="logs"):
    """
    Set up and configure a logger with both file and console handlers
    
    Args:
        name (str): Logger name, typically __name__ in the calling module
        log_level (int): Logging level - use constants from logging module
        log_dir (str): Directory where log files will be stored
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # If logger already has handlers, we've already set it up
    if logger.handlers:
        return logger
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file_path = os.path.join(log_dir, f"ideation_agent_{timestamp}.log")
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set up file handler for logs
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # Set up console handler for displaying logs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)  # Only warnings and above to console by default
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Prevent logs from propagating to the root logger
    logger.propagate = False
    
    return logger

def get_logger(name=__name__, log_level=None):
    """
    Get an existing logger or create a new one
    
    Args:
        name (str): Logger name
        log_level (int, optional): Override default log level if provided
        
    Returns:
        logging.Logger: Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger is not configured yet, set it up
    if not logger.handlers:
        logger = setup_logger(name, log_level or logging.INFO)
        
    # If log_level is provided, update the logger level
    elif log_level is not None:
        logger.setLevel(log_level)
        
    return logger

# Helper log functions with context
def log_function_call(logger, func_name, args=None, kwargs=None):
    """Log when a function is called with its arguments"""
    args_str = str(args) if args else ""
    kwargs_str = str(kwargs) if kwargs else ""
    logger.debug(f"Function called: {func_name} | Args: {args_str} | Kwargs: {kwargs_str}")

def log_function_return(logger, func_name, result=None):
    """Log when a function returns with optional result summary"""
    result_summary = str(result)[:100] + "..." if result and len(str(result)) > 100 else str(result)
    logger.debug(f"Function returned: {func_name} | Result: {result_summary}")

def log_error(logger, error, context=None):
    """Log an exception with optional context"""
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg += f" | Context: {context}"
    logger.error(error_msg, exc_info=True)

def log_api_request(logger, endpoint, params=None):
    """Log API request details"""
    params_str = str(params) if params else "None"
    logger.info(f"API Request | Endpoint: {endpoint} | Params: {params_str}")

def log_api_response(logger, endpoint, status_code, response_summary=None):
    """Log API response with status code and optional response summary"""
    response_str = str(response_summary)[:100] + "..." if response_summary and len(str(response_summary)) > 100 else str(response_summary)
    logger.info(f"API Response | Endpoint: {endpoint} | Status: {status_code} | Response: {response_str}")

def log_user_action(logger, action, details=None):
    """Log user actions in the application"""
    details_str = f" | Details: {details}" if details else ""
    logger.info(f"User Action: {action}{details_str}")
