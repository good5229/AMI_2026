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
      RegionId.suyeong => '수영구 시나리오 주입 모드',
      RegionId.gangneung => '강릉시 제어기 연계 검증 모드',
      RegionId.chungju => '충주시 분전함 자산 모드',
    };
  }

  String get defaultFilterHint {
    return switch (this) {
      RegionId.suyeong => '검증 시나리오 중심 점검',
      RegionId.gangneung => '제어기 연계 구조 검증 중심 점검',
      RegionId.chungju => '고부하/이상 신호 중심 점검',
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
      RegionId.suyeong => '수영구는 시나리오 주입 대상 분전함 중심으로 먼저 확인',
      RegionId.gangneung => '강릉시는 제어기 연계 분전함 우선 탐색',
      RegionId.chungju => '충주시는 분전함 자산 스탠드얼론 대상 우선',
    };
  }

  bool get supportsScenarioInjection {
    return switch (this) {
      RegionId.suyeong => true,
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
      RegionId.chungju => true,
    };
  }

  bool get supportsRealMunicipalAmi {
    return false;
  }

  String get modeDescription {
    return switch (this) {
      RegionId.suyeong => '지자체 미연결 + 시나리오 주입',
      RegionId.gangneung => '제어기 연계 검증 모드',
      RegionId.chungju => '분전함 중심 Asset-only 모드',
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
        '분전함 204개 · 가로등 4,076개',
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
        '분전함 871개 자산 스탠드얼론',
        '가로등 수급 정보 보완 우선',
        '예측·정상범위 임계치 중심 처리',
      ],
    ),
  ];
}
