from app.adapters.persistence.models.certification_model import CertificationModel
from app.domain.entities.certification import Certification


class CertificationMapper:
    @staticmethod
    def to_entity(model: CertificationModel) -> Certification:
        return Certification(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            issuer=model.issuer,
            issue_date=model.issue_date,
            expiry_date=model.expiry_date,
            credential_url=model.credential_url,
            credential_id=model.credential_id,
        )

    @staticmethod
    def to_model(entity: Certification) -> CertificationModel:
        return CertificationModel(
            id=entity.id,
            user_id=entity.user_id,
            name=entity.name,
            issuer=entity.issuer,
            issue_date=entity.issue_date,
            expiry_date=entity.expiry_date,
            credential_url=entity.credential_url,
            credential_id=entity.credential_id,
        )
