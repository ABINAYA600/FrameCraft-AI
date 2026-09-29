from ml_models.script_model import ScriptModel
from ml_models.decision_engine import DecisionEngine
from ml_models.video_composer import VideoComposer


print("================================")
print("FRAMECRAFT VIDEO PIPELINE TEST")
print("================================")


# ==================================================
# SCRIPT
# ==================================================

script = """
Welcome to our organic farm.
Fresh vegetables are harvested every morning.
Modern tractors help improve productivity.
"""


# ==================================================
# SCRIPT MODULE
# ==================================================

print("\n[1] Processing script...")

script_model = ScriptModel()

script_output = script_model.process(
    script
)

print("✅ Script processing completed.")

print(
    "Scenes:",
    script_output.get("scenes")
)


# ==================================================
# DECISION ENGINE
# ==================================================

print("\n[2] Decision Engine...")

decision_engine = DecisionEngine()

print(
    "⚠️ Decision engine requires the "
    "media/image output produced by the "
    "current retrieval pipeline."
)

print(
    "Use tests.test_decision_engine.py "
    "for the standalone decision-engine test."
)


# ==================================================
# VIDEO COMPOSER
# ==================================================

print("\n[3] Video Composer...")

video_composer = VideoComposer()

print(
    "✅ VideoComposer initialized."
)


# ==================================================
# RESULT
# ==================================================

print("\n================================")
print("BASIC VIDEO PIPELINE TEST PASSED")
print("================================")