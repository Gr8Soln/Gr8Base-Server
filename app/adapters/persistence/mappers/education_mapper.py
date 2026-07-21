from app.adapters.persistence.models.education_model import EducationModel
from app.domain.entities.education import Education


class EducationMapper:
    @staticmethod
    def to_entity(model: EducationModel) -> Education:
        return Education(
            id=model.id,
            user_id=model.user_id,
            institution=model.institution,
            degree=model.degree,
            field_of_study=model.field_of_study,
            start_year=model.start_year,
            end_year=model.end_year,
            gpa=model.gpa,
            honors=model.honors,
            activities=model.activities,
        )

    @staticmethod
    def to_model(entity: Education) -> EducationModel:
        return EducationModel(
            id=entity.id,
            user_id=entity.user_id,
            institution=entity.institution,
            degree=entity.degree,
            field_of_study=entity.field_of_study,
            start_year=entity.start_year,
            end_year=entity.end_year,
            gpa=entity.gpa,
            honors=entity.honors,
            activities=entity.activities,
        )
