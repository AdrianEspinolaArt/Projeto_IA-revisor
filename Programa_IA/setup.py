from cx_Freeze import setup, Executable

setup(
    name="AI REVISOR",
    version="1.0",
    description="revisor de texto baseado em nlp e chatgpt",
    executables=[Executable("seu_script.py")],
)