from fastapi import FastAPI, HTTPException
from owlready2 import *
import os

# construct the path to the ontology file
onto_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), "ontology", "ontology.owl")

try:
    onto = get_ontology(onto_path).load()

    # verify classes are loaded
    print("ontology loaded")
    print("available classes:", list(onto.classes()))

    # print data properties to verify 'formula'
    print("data properties:", list(onto.data_properties()))
except Exception as e:
    print(f"ontology loading error: {e}")
    onto = None

app = FastAPI()


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ontology_loaded": onto is not None,
        "available_classes": list(onto.classes()) if onto else []
    }


@app.get("/calculate_area/")
async def calculate_area(shape_name: str, radius: float = None, side: float = None,
                         length: float = None, width: float = None,
                         base: float = None, height: float = None):
    # check if ontology is loaded
    if onto is None:
        raise HTTPException(status_code=500, detail="Ontology not loaded")

    try:
        # construct the iri pattern for the individual
        individual_iri = f"*{shape_name}_1"

        # search for the individual by iri pattern
        shape_individual = onto.search_one(iri=individual_iri)
        print("Shape Individual:", shape_individual)

        if shape_individual is None:
            raise HTTPException(
                status_code=400,
                detail=f"Shape individual '{
                    shape_name}' not found in ontology."
            )

        # access the 'formula' data property using .get_properties() and .value
        formula_property = onto.search_one(iri="*formula")
        if formula_property is None:
            raise HTTPException(
                status_code=400,
                detail="'formula' property is not defined in the ontology."
            )

        # retrieve the value of the 'formula' property for the individual
        for prop in shape_individual.get_properties():
            if prop == formula_property:
                formulas = prop[shape_individual]
                break
        else:
            formulas = []

        if not formulas:
            raise HTTPException(
                status_code=400,
                detail=f"No formula found for shape individual '{shape_name}'."
            )

        formula = formulas[0]

        # prep dimensions for evaluation
        dimensions = {
            'radius': radius,
            'side': side,
            'length': length,
            'width': width,
            'base': base,
            'height': height
        }

        # remove none values
        dimensions = {k: v for k, v in dimensions.items() if v is not None}

        # check if required dimensions are provided
        if not dimensions:
            raise HTTPException(
                status_code=400,
                detail="At least one dimension is required."
            )

        # safely evaluate the formula
        try:
            area = eval(formula, {"__builtins__": {}}, dimensions)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error calculating area: {e}"
            )

        return {"shape": shape_name, "formula": formula, "area": area}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected calculation error: {e}"
        )
