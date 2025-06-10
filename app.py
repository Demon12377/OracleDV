import os
import sys
import time
import numpy as np
import gradio as gr

# Adjust the path to import from the 'api' directory
# This assumes app.py is in the root, and oracle.py is in ./api/
script_dir = os.path.dirname(__file__)
api_module_path = os.path.join(script_dir, 'api')
sys.path.insert(0, api_module_path)

# Now import the necessary functions from oracle
try:
    from oracle import load_local_oracle_artifact, create_charge_vector, fractal_crystallization
except ImportError as e:
    print(f"Error importing from oracle.py: {e}")
    print(f"Ensure oracle.py is in {api_module_path} and does not have top-level errors.")
    # Provide default stubs if import fails, so Gradio can at least launch with an error message
    def load_local_oracle_artifact_stub():
        print("STUB: load_local_oracle_artifact called. Oracle functionality is NOT available.")
        return None, None
    def create_charge_vector_stub(intent, dim):
        print(f"STUB: create_charge_vector called with intent: {intent}. Oracle functionality is NOT available.")
        return np.random.rand(dim)
    def fractal_crystallization_stub(charge, words, vectors):
        print("STUB: fractal_crystallization called. Oracle functionality is NOT available.")
        return "Oracle module import failed. Please check server logs."

    load_local_oracle_artifact = load_local_oracle_artifact_stub
    create_charge_vector = create_charge_vector_stub
    fractal_crystallization = fractal_crystallization_stub


# --- CONFIGURATION for artifact path from root ---
ARTIFACT_FILENAME_CONFIG = 'oracle_ocean.npz'
# _SCRIPT_DIR for app.py is the root directory
_APP_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# The artifact is in 'data/oracle_ocean.npz' relative to the root
_FULL_ARTIFACT_PATH_GRADIO = os.path.join(_APP_ROOT_DIR, 'data', ARTIFACT_FILENAME_CONFIG)

# --- Global variables for Oracle data ---
words_db_global = None
vectors_db_global = None
vector_dim_global = 300 # Default, will be updated on load
oracle_load_error = None

def initialize_oracle():
    global words_db_global, vectors_db_global, vector_dim_global, oracle_load_error

    # Temporarily modify the path variable expected by the original load_local_oracle_artifact
    # This is a bit of a hack. Ideally, load_local_oracle_artifact would take the path as an argument.
    # We need to make load_local_oracle_artifact in oracle.py look for the artifact in the correct path
    # relative to *its own location* if we call it directly, or ensure its internal _FULL_ARTIFACT_PATH is correct.

    # The original oracle.py's _FULL_ARTIFACT_PATH is:
    # os.path.join(os.path.join(os.path.dirname(__file__), '..'), 'data', ARTIFACT_FILENAME_CONFIG)
    # Since __file__ for oracle.py will be /path/to/project/api/oracle.py,
    # os.path.dirname(__file__) is /path/to/project/api
    # os.path.join(os.path.dirname(__file__), '..') is /path/to/project
    # So, the original function *should* correctly resolve to /path/to/project/data/oracle_ocean.npz
    # IF the 'data' directory is at the project root. Let's assume this is the case.
    # No path override seems necessary for load_local_oracle_artifact if its internal logic is sound.

    print(f"[GRADIO APP] Initializing Oracle...")
    print(f"[GRADIO APP] Attempting to load artifact using oracle.py's logic.")
    print(f"[GRADIO APP] Expected artifact location by oracle.py: data/{ARTIFACT_FILENAME_CONFIG} (relative to project root)")

    # To ensure the original function uses the correct path, we might need to temporarily
    # change directory or manipulate its internal path variable if it's not correctly finding it.
    # For now, let's try calling it directly.
    # If load_local_oracle_artifact in oracle.py relies on its own _SCRIPT_DIR to find 'data',
    # and _SCRIPT_DIR is defined as os.path.dirname(__file__) within oracle.py,
    # then its calculation _os.path.join(_SCRIPT_DIR, '..', 'data', ARTIFACT_FILENAME_CONFIG)_
    # should correctly point to `PROJECT_ROOT/data/ARTIFACT_FILENAME_CONFIG`.

    try:
        # Ensure the context for load_local_oracle_artifact is correct
        # The function `load_local_oracle_artifact` in `oracle.py` uses `_SCRIPT_DIR` defined in `oracle.py`
        # `_SCRIPT_DIR` in `oracle.py` is `os.path.dirname(__file__)` which refers to `api/`
        # `_PROJECT_ROOT_APPROX` in `oracle.py` is `os.path.join(_SCRIPT_DIR, '..')` which refers to the project root.
        # `_FULL_ARTIFACT_PATH` in `oracle.py` is `os.path.join(_PROJECT_ROOT_APPROX, 'data', ARTIFACT_FILENAME_CONFIG)`
        # This should correctly resolve to `PROJECT_ROOT/data/oracle_ocean.npz`.

        words_db_global, vectors_db_global = load_local_oracle_artifact()

        if words_db_global is None or vectors_db_global is None:
            oracle_load_error = f"Oracle artifact not loaded. Check logs. Expected at: {os.path.join('data', ARTIFACT_FILENAME_CONFIG)}"
            print(f"[GRADIO APP][ERROR] {oracle_load_error}")
        else:
            vector_dim_global = vectors_db_global.shape[1]
            print(f"[GRADIO APP] Oracle loaded successfully. Words: {len(words_db_global)}, Vector dim: {vector_dim_global}")
    except Exception as e:
        oracle_load_error = f"Exception during Oracle initialization: {str(e)}"
        print(f"[GRADIO APP][CRITICAL ERROR] {oracle_load_error}")
        import traceback
        traceback.print_exc()


def oracle_predict(intent_text: str) -> str:
    global words_db_global, vectors_db_global, vector_dim_global, oracle_load_error

    if oracle_load_error:
        return f"Error: {oracle_load_error}"
    if words_db_global is None or vectors_db_global is None:
        return "Error: Oracle data not loaded. Please check server logs."
    if not intent_text or not intent_text.strip():
        return "Error: Intent text cannot be empty."

    print(f"[GRADIO REQUEST] Received intent: '{intent_text[:100]}{'...' if len(intent_text) > 100 else ''}'")
    start_time = time.time()

    try:
        charge = create_charge_vector(intent_text, vector_dim_global)
        result = fractal_crystallization(charge, words_db_global, vectors_db_global)
    except Exception as e:
        print(f"[GRADIO ERROR] Error processing intent '{intent_text}': {e}")
        import traceback
        traceback.print_exc()
        return f"Error during prediction: {str(e)}"

    end_time = time.time()
    processing_duration = round(end_time - start_time, 3)
    print(f"[GRADIO RESPONSE] Intent: '{intent_text[:50]}...', Result: '{result[:50]}...', Time: {processing_duration}s")

    return result

# Initialize Oracle when the script is loaded
initialize_oracle()

# --- Gradio Interface ---
iface = gr.Interface(
    fn=oracle_predict,
    inputs=gr.Textbox(lines=2, placeholder="Enter your intent here..."),
    outputs=gr.Textbox(label="Crystal"),
    title="Intent Oracle",
    description="Manifest a crystal based on your textual intent. The Oracle meditates on your words and reveals their crystallized essence.",
    allow_flagging='never'
)

if __name__ == '__main__':
    if oracle_load_error:
        print(f"WARNING: Gradio app might not function correctly due to Oracle load error: {oracle_load_error}")

    print("Launching Gradio interface...")
    # For Hugging Face Spaces, it's common to use share=False and let Spaces handle exposure.
    # server_name="0.0.0.0" makes it accessible within the container.
    iface.launch(server_name="0.0.0.0")
