from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class RegulationSource:
    source_id: str
    title: str
    publisher: str
    source_kind: str
    authority_level: str
    url: str
    checked_on: date
    ingestion_status: str
    notes: str


T12_SOURCES: tuple[RegulationSource, ...] = (
    RegulationSource(
        source_id="law.animal_protection_act",
        title="동물보호법",
        publisher="국가법령정보센터",
        source_kind="statute",
        authority_level="primary_law",
        url="https://www.law.go.kr/법령/동물보호법",
        checked_on=date(2026, 6, 15),
        ingestion_status="metadata_verified",
        notes="동물 관련 영업과 보호 의무의 상위 법적 근거.",
    ),
    RegulationSource(
        source_id="law.animal_protection_decree",
        title="동물보호법 시행령",
        publisher="국가법령정보센터",
        source_kind="enforcement_decree",
        authority_level="primary_law",
        url="https://www.law.go.kr/법령/동물보호법시행령",
        checked_on=date(2026, 6, 15),
        ingestion_status="metadata_verified",
        notes="법률 위임 사항과 행정 기준 참고 출처.",
    ),
    RegulationSource(
        source_id="law.animal_protection_rule",
        title="동물보호법 시행규칙",
        publisher="국가법령정보센터",
        source_kind="enforcement_rule",
        authority_level="primary_law",
        url="https://www.law.go.kr/법령/동물보호법시행규칙",
        checked_on=date(2026, 6, 15),
        ingestion_status="metadata_verified",
        notes="시설·인력 기준과 영업자 준수사항의 공식 근거.",
    ),
    RegulationSource(
        source_id="guide.animal_business",
        title="반려동물 영업자 안내",
        publisher="국가동물보호정보시스템",
        source_kind="official_guide",
        authority_level="administrative_guidance",
        url="https://www.animal.go.kr/front/awtis/shop/salesList.do?menuNo=5000000023",
        checked_on=date(2026, 6, 15),
        ingestion_status="metadata_verified",
        notes="영업 등록·운영 관련 행정 안내와 등록 업소 확인 경로.",
    ),
    RegulationSource(
        source_id="guide.operator_training",
        title="동물 관련 영업자 법정의무교육 안내",
        publisher="국가동물보호정보시스템·동물사랑배움터",
        source_kind="official_guide",
        authority_level="administrative_guidance",
        url="https://apms.epis.or.kr/",
        checked_on=date(2026, 6, 15),
        ingestion_status="metadata_verified",
        notes="교육 주기와 대상은 원문과 법령을 교차 확인한다.",
    ),
    RegulationSource(
        source_id="rule.consumer_dispute",
        title="소비자분쟁해결기준",
        publisher="국가법령정보센터·공정거래위원회",
        source_kind="administrative_rule",
        authority_level="official_standard",
        url="https://www.law.go.kr/행정규칙/소비자분쟁해결기준",
        checked_on=date(2026, 6, 15),
        ingestion_status="scope_review_required",
        notes="위탁 서비스 취소·환불·손해 문의의 적용 범위를 검토한다.",
    ),
    RegulationSource(
        source_id="data.local_permits",
        title="지방행정 인허가정보",
        publisher="공공데이터포털",
        source_kind="open_data",
        authority_level="official_data",
        url="https://www.data.go.kr/index.do",
        checked_on=date(2026, 6, 15),
        ingestion_status="dataset_discovery_required",
        notes="등록 업소 현황과 지역별 통계의 공식 데이터 후보.",
    ),
    RegulationSource(
        source_id="guide.avma_petcare",
        title="Pet care resources",
        publisher="American Veterinary Medical Association",
        source_kind="veterinary_public_guide",
        authority_level="expert_guidance",
        url="https://www.avma.org/resources-tools/pet-owners/petcare",
        checked_on=date(2026, 6, 16),
        ingestion_status="metadata_verified",
        notes="보호자용 건강·예방관리·수의사 상담 기준 참고 출처.",
    ),
    RegulationSource(
        source_id="guide.aspca_poison",
        title="Animal Poison Control",
        publisher="ASPCA",
        source_kind="poison_control_guide",
        authority_level="expert_guidance",
        url="https://www.aspca.org/pet-care/animal-poison-control",
        checked_on=date(2026, 6, 16),
        ingestion_status="metadata_verified",
        notes="독성 물질 섭취 의심 시 전문기관 또는 동물병원 상담 안내 출처.",
    ),
    RegulationSource(
        source_id="guide.fda_pet_food",
        title="Animal & Veterinary resources",
        publisher="U.S. Food and Drug Administration",
        source_kind="food_safety_guide",
        authority_level="official_guidance",
        url="https://www.fda.gov/animal-veterinary",
        checked_on=date(2026, 6, 16),
        ingestion_status="metadata_verified",
        notes="반려동물 식품 안전, 리콜, 식품 관련 공식 참고 출처.",
    ),
    RegulationSource(
        source_id="guide.aaha_pet_owner",
        title="Pet owner resources",
        publisher="American Animal Hospital Association",
        source_kind="veterinary_public_guide",
        authority_level="expert_guidance",
        url="https://www.aaha.org/your-pet/",
        checked_on=date(2026, 6, 16),
        ingestion_status="metadata_verified",
        notes="예방관리와 동물병원 상담 준비에 활용하는 보호자용 자료.",
    ),
    RegulationSource(
        source_id="guide.cdc_healthy_pets",
        title="Ways to Stay Healthy Around Animals",
        publisher="U.S. Centers for Disease Control and Prevention",
        source_kind="public_health_guide",
        authority_level="official_guidance",
        url="https://www.cdc.gov/healthy-pets/about/index.html",
        checked_on=date(2026, 6, 16),
        ingestion_status="metadata_verified",
        notes="사람-동물 공통 감염 예방, 손 씻기, 생활 위생, 재난·여행 안전 참고 출처.",
    ),
    RegulationSource(
        source_id="guide.cornell_feline_lutd",
        title="Feline Lower Urinary Tract Disease",
        publisher="Cornell University College of Veterinary Medicine",
        source_kind="veterinary_public_guide",
        authority_level="expert_guidance",
        url="https://www.vet.cornell.edu/departments-centers-and-institutes/cornell-feline-health-center/health-information/feline-health-topics/feline-lower-urinary-tract-disease",
        checked_on=date(2026, 6, 16),
        ingestion_status="metadata_verified",
        notes="고양이 배뇨 문제, 화장실 문제, 요도 폐색 응급 신호 참고 출처.",
    ),
)


def list_t12_sources() -> tuple[RegulationSource, ...]:
    return T12_SOURCES
