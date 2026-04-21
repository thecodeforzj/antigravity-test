
import json
from formula_compiler import AOSASTCompiler
compiler = AOSASTCompiler("flow/02_Specs/Hardware_Manifest.json")
dsl = compiler.generate_spatial_dsl("A*X + B", 9, [])
with open("flow/01_Ideation_Threads/REGRESSION_DSL.json", "w") as f:
    json.dump(dsl, f, indent=4)
