from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os
import math

app = FastAPI()

class CalculationRequest(BaseModel):
    expression: str

class CalculationResponses(BaseModel):  
    result: float
    expression: str
    error: Optional[str] = None

@app.post("/api/calc")
async def calculate(request: CalculationRequest):
    """
    Calculate a mathematical expression.
    Supports basic operations: +, -, *, /, **, %, pow(), sqrt(), sin(), cos(), tan(), etc.
    """
    try:
        # Create a safe namespace with only math functions
        safe_dict = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'pi': math.pi,
            'e': math.e,
            'abs': abs,
            'pow': pow,
            'round': round,
        }
        
        result = eval(request.expression, {"__builtins__": {}}, safe_dict)
        return CalculationResponses(
            result=float(result),
            expression=request.expression,
            error=None
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Calculation error: {str(e)}"
        )

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)