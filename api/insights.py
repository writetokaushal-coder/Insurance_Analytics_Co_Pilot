from fastapi import APIRouter, HTTPException
from src.repositories.policy_repository import get_policy_summary, get_portfolio_summary

router = APIRouter(tags=["insights"])

@router.get("/policy/{policy_id}")
def policy_summary_endpoint(policy_id: str):
    try:
        result = get_policy_summary(policy_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"Policy {policy_id} was not found.")
        return result
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.get("/portfolio/summary")
def portfolio_summary_endpoint():
    try:
        return get_portfolio_summary()
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
