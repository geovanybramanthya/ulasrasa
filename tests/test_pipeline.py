"""
Unit Tests for UlasRasa ABSA Pipeline & Kitchen Health Score
"""

import os
import pytest
import pandas as pd
from src.absa_pipeline import ABSAPipeline
from src.action_engine import ActionPlanEngine
from src.preprocessing import clean_text

def test_clean_text():
    raw = "Ayamnya enak bgt tp sambalnya dikit & tumpah!!"
    cleaned = clean_text(raw)
    assert "banget" in cleaned
    assert "sedikit" in cleaned
    assert "tapi" in cleaned

def test_analyze_single_review():
    pipeline = ABSAPipeline()
    text = "Ayamnya gurih renyah bumbunya mantap, cuma sambalnya dikit banget dan kemasan mangkok tumpah kuahnya di jalan."
    result = pipeline.analyze_single_review(text)
    
    assert "aspects" in result
    assert result["aspects"]["rasa"]["mentioned"] is True
    assert result["aspects"]["kemasan"]["mentioned"] is True
    assert result["aspects"]["kemasan"]["sentiment"] == "negative"

def test_evaluate_dataframe():
    pipeline = ABSAPipeline()
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_reviews.csv")
    assert os.path.exists(csv_path)
    
    df = pd.read_csv(csv_path)
    eval_res = pipeline.evaluate_dataframe(df)
    
    assert "kitchen_health_score" in eval_res
    khs = eval_res["kitchen_health_score"]
    assert 0.0 <= khs <= 100.0
    
    breakdown = eval_res["aspect_breakdown"]
    for asp in ["rasa", "porsi", "harga", "kemasan", "pelayanan"]:
        assert asp in breakdown
        assert 0.0 <= breakdown[asp]["satisfaction_score"] <= 100.0

def test_action_plan_engine():
    pipeline = ABSAPipeline()
    action_engine = ActionPlanEngine()
    
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_reviews.csv")
    df = pd.read_csv(csv_path)
    eval_res = pipeline.evaluate_dataframe(df)
    
    plan = action_engine.generate_action_plan(
        restaurant_name="Ayam Geprek Juara",
        evaluation_results=eval_res,
        sample_complaints=["Kemasan tumpah kuah di jalan", "Porsi nasi sedikit"]
    )
    
    assert "kitchen_action_checklist" in plan
    assert len(plan["kitchen_action_checklist"]) > 0
    assert "root_cause_analysis" in plan
    assert "sop_recommendations" in plan
