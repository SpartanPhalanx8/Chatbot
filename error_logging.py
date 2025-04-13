import logging

logging.basicConfig(level=logging.DEBUG)

logging.debug("Chat endpoint accessed via POST.")
logging.info(f"User input: {user_input}")
logging.error(f"Error during processing: {e}")