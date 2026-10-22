"""
Weather Activity Advisor - Inference Engine
Implements a forward-chaining expert system inference mechanism with:
1. Working Memory fact assertion & linguistic abstraction
2. Pattern matching against the Knowledge Base
3. Conflict resolution (Priority + Specificity + Confidence)
4. Explainable AI (XAI) audit trail and rule trace
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from knowledge_base import (
    Rule,
    get_all_rules,
    categorize_temperature,
    categorize_wind
)


@dataclass
class RuleEvaluationTrace:
    """Detailed record of how an individual rule was evaluated during forward chaining."""
    rule_id: str
    rule_name: str
    priority: int
    matched: bool
    reasons: List[str]
    recommendation: str


@dataclass
class InferenceResult:
    """The final deduction package produced by the expert system."""
    fired_rule: Rule
    working_memory: Dict[str, Any]
    candidate_rules: List[Rule]
    evaluation_traces: List[RuleEvaluationTrace]
    explanation_summary: str
    suitability_score: int
    primary_activity: str
    category: str
    clothing_checklist: List[str]
    safety_advisories: List[str]
    alternative_activities: List[str]


class WeatherInferenceEngine:
    """
    Forward-chaining inference engine for Weather Activity Advisory.
    """

    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules: List[Rule] = rules if rules is not None else get_all_rules()

    def create_working_memory(
        self,
        temperature: float,
        rain: str,
        wind_speed: float,
        time_of_day: str = "Afternoon",
        humidity: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Transforms raw quantitative sensor/user inputs into qualitative symbolic facts.
        """
        temp_category = categorize_temperature(temperature)
        wind_category = categorize_wind(wind_speed)

        facts = {
            "temperature": round(float(temperature), 1),
            "temp_category": temp_category,
            "rain": str(rain).strip(),
            "wind_speed": round(float(wind_speed), 1),
            "wind_category": wind_category,
            "time_of_day": time_of_day,
            "humidity": round(float(humidity), 1) if humidity is not None else None,
        }
        return facts

    def run_inference(
        self,
        temperature: float,
        rain: str,
        wind_speed: float,
        time_of_day: str = "Afternoon",
        humidity: Optional[float] = None
    ) -> InferenceResult:
        """
        Executes the expert system forward-chaining cycle:
        1. Fact Assertion (Working Memory)
        2. Match Phase (Condition Testing)
        3. Conflict Resolution Phase (Priority & Specificity)
        4. Act / Conclude Phase (Fires winning rule)
        5. Explanation Generation (Audit Trace)
        """
        # Step 1: Fact assertion
        working_memory = self.create_working_memory(
            temperature=temperature,
            rain=rain,
            wind_speed=wind_speed,
            time_of_day=time_of_day,
            humidity=humidity
        )

        candidates: List[Rule] = []
        traces: List[RuleEvaluationTrace] = []

        # Step 2: Match Phase (Pattern Matching)
        for rule in self.rules:
            is_match, reasons = rule.matches(working_memory)
            traces.append(
                RuleEvaluationTrace(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    priority=rule.priority,
                    matched=is_match,
                    reasons=reasons if is_match else ["Condition mismatch with current weather facts"],
                    recommendation=rule.recommendation
                )
            )
            if is_match:
                candidates.append(rule)

        # Step 3: Conflict Resolution
        # Sorting criterion:
        # 1. Rule Priority (higher integer = higher priority, e.g. severe alerts)
        # 2. Number of specified conditions (specificity)
        # 3. Suitability score
        if candidates:
            def specificity_key(r: Rule) -> int:
                count = 0
                if r.temp_categories is not None:
                    count += 1
                if r.rain_conditions is not None:
                    count += 1
                if r.wind_categories is not None:
                    count += 1
                return count

            candidates.sort(
                key=lambda r: (r.priority, specificity_key(r), r.suitability_score),
                reverse=True
            )
            winning_rule = candidates[0]
        else:
            # Fallback default rule if no rule explicitly matched
            winning_rule = Rule(
                rule_id="R_FALLBACK",
                name="Default Weather Leisure Protocol",
                priority=0,
                recommendation="Casual Indoor Relaxation or Local Community Center",
                category="Indoor",
                suitability_score=70,
                clothing=["Comfortable casual clothing", "Light jacket"],
                safety_warnings=["Always monitor rapid weather changes."],
                alternative_activities=["Movie streaming at home", "Coffee with friends", "Indoor gym workout"],
                explanation="No specific expert rule matched this exact combination; applying general indoor baseline."
            )

        # Step 4: Explanation Construction
        fired_reasons = []
        for trace in traces:
            if trace.rule_id == winning_rule.rule_id:
                fired_reasons = trace.reasons
                break

        explanation_summary = (
            f"Rule '{winning_rule.name}' [{winning_rule.rule_id}] triggered with priority {winning_rule.priority}. "
            f"Grounds: {'; '.join(fired_reasons)}. "
            f"Expert rationale: {winning_rule.explanation}"
        )

        # Return comprehensive result package
        return InferenceResult(
            fired_rule=winning_rule,
            working_memory=working_memory,
            candidate_rules=candidates,
            evaluation_traces=traces,
            explanation_summary=explanation_summary,
            suitability_score=winning_rule.suitability_score,
            primary_activity=winning_rule.recommendation,
            category=winning_rule.category,
            clothing_checklist=winning_rule.clothing,
            safety_advisories=winning_rule.safety_warnings,
            alternative_activities=winning_rule.alternative_activities
        )
