import 'package:flutter/foundation.dart';

enum RegionId {
  suyeong,
  gangneung,
  chungju,
}

enum RegionDataBranch {
  suyeongScenarioValidation,
  gangneungControllerLinked,
  chungjuAssetOnly,
}

extension RegionIdX on RegionId {
  String get id {
    return switch (this) {
      RegionId.suyeong => 'suyeong',
      RegionId.gangneung => 'gangneung',
      RegionId.chungju => 'chungju',
    };
  }

  String get label {
    return switch (this) {
      RegionId.suyeong => '부산 수영구',
      RegionId.gangneung => '강릉시',
      RegionId.chungju => '충주시',
    };
  }

  String get seedAsset {
    return switch (this) {
      RegionId.suyeong => 'assets/data/suyeong_v02_seed.json',
      RegionId.gangneung => 'assets/data/gangneung_v02_seed.json',
      RegionId.chungju => 'assets/data/chungju_v02_seed.json',
    };
  }

  RegionDataBranch get branch {
    return switch (this) {
      RegionId.suyeong => RegionDataBranch.suyeongScenarioValidation,
      RegionId.gangneung => RegionDataBranch.gangneungControllerLinked,
      RegionId.chungju => RegionDataBranch.chungjuAssetOnly,
    };
  }

  String get branchLabel {
    return switch (this) {
      RegionId.suyeong => '수영구 공개 자산 · AMI 미연결',
      RegionId.gangneung => '강릉시 공개 자산 · AMI 미연결',
      RegionId.chungju => '충주시 공개 자산 · AMI 미연결',
    };
  }

  String get defaultFilterHint {
    return switch (this) {
      RegionId.suyeong => '공개 자산 조회',
      RegionId.gangneung => '제어기 연계 구조 검증 중심 점검',
      RegionId.chungju => '공개 자산 조회',
    };
  }

  String get targetModeField {
    return switch (this) {
      RegionId.suyeong => 'target_cabinets_3_4kw_like',
      RegionId.gangneung => 'target_cabinet_ids',
      RegionId.chungju => 'target_cabinet_ids',
    };
  }

  String get regionalFilterHint {
    return switch (this) {
      RegionId.suyeong => '수영구 공개 분전함 정보 조회',
      RegionId.gangneung => '강릉시는 제어기 연계 분전함 우선 탐색',
      RegionId.chungju => '충주시는 공개된 분전함·가로등 시설정보를 우선 확인',
    };
  }

  bool get supportsScenarioInjection {
    return switch (this) {
      RegionId.suyeong => false,
      RegionId.gangneung => false,
      RegionId.chungju => false,
    };
  }

  bool get supportsControllerData {
    return switch (this) {
      RegionId.suyeong => false,
      RegionId.gangneung => true,
      RegionId.chungju => false,
    };
  }

  bool get supportsRatedLoad {
    return switch (this) {
      RegionId.suyeong => true,
      RegionId.gangneung => true,
      RegionId.chungju => false,
    };
  }

  bool get supportsRealMunicipalAmi {
    return false;
  }

  String get modeDescription {
    return switch (this) {
      RegionId.suyeong => '시설정보 제공 · 전력 상태 미관측',
      RegionId.gangneung => '시설정보와 제어기 연결정보 제공',
      RegionId.chungju => '기본 시설정보 제공',
    };
  }
}

@immutable
class RegionMetadata {
  const RegionMetadata(this.id, this.modeNotes);

  final RegionId id;
  final List<String> modeNotes;

  static const all = <RegionMetadata>[
    RegionMetadata(
      RegionId.suyeong,
      <String>[
        '개별 가로등/분전함 연결 가능',
        '총 정격용량, 좌표 기반 분석',
        '분전함 204개 · 자산행 4,076개 · 실제 등 수 4,239등',
      ],
    ),
    RegionMetadata(
      RegionId.gangneung,
      <String>[
        '분전함·제어기 연계 가중치 적용',
        '분전함 339개 · 제어기 연계 데이터 중심 분석',
        '강릉시 제어기 연계 구조 검증',
      ],
    ),
    RegionMetadata(
      RegionId.chungju,
      <String>[
        '분전함 871개 시설정보 확인 가능',
        '가로등별 설비용량 정보는 제한적',
        '분전함·가로등 기둥 중심의 기본 시설정보',
      ],
    ),
  ];
}
