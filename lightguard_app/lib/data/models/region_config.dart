import 'package:flutter/foundation.dart';

enum RegionId {
  suyeong,
  gangneung,
  chungju,
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

  String get modeDescription {
    return switch (this) {
      RegionId.suyeong => '지자체 미연결 + 시나리오 주입',
      RegionId.gangneung => 'Controller-linked 분전함 모드',
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
        '분전함 339개 · 가로등 분포 기반 분석',
        'AMI 연동 후보 우선 정렬',
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

