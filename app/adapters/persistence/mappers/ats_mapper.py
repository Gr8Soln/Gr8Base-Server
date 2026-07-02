from app.adapters.persistence.models.ats_model import ATSScoreModel
from app.domain.entities.ats import ATSScore, ScoreDimension


class ATSScoreMapper:
    @staticmethod
    def to_entity(model: ATSScoreModel) -> ATSScore:
        dimensions = [
            ScoreDimension(
                name=d.get("name", ""),
                score=d.get("score", 0.0),
                weight=d.get("weight", 0.0),
                feedback=d.get("feedback", ""),
                suggestions=d.get("suggestions", []),
            )
            for d in (model.dimensions or [])
        ]
        return ATSScore(
            id=model.id,
            user_id=model.user_id,
            resume_id=model.resume_id,
            job_id=model.job_id,
            overall_score=model.overall_score,
            dimensions=dimensions,
            missing_keywords=model.missing_keywords or [],
            weak_sections=model.weak_sections or [],
            recommendations=model.recommendations or [],
            recruiter_critique=model.recruiter_critique,
            is_ats_safe=model.is_ats_safe,
        )

    @staticmethod
    def to_model(entity: ATSScore) -> ATSScoreModel:
        dimensions = [
            {
                "name": d.name,
                "score": d.score,
                "weight": d.weight,
                "feedback": d.feedback,
                "suggestions": d.suggestions,
            }
            for d in entity.dimensions
        ]
        return ATSScoreModel(
            id=entity.id,
            user_id=entity.user_id,
            resume_id=entity.resume_id,
            job_id=entity.job_id,
            overall_score=entity.overall_score,
            dimensions=dimensions,
            dimension_breakdown={},
            missing_keywords=entity.missing_keywords,
            weak_sections=entity.weak_sections,
            recommendations=entity.recommendations,
            recruiter_critique=entity.recruiter_critique,
            is_ats_safe=entity.is_ats_safe,
            safety_issues=[],
        )
