import 'package:flutter/material.dart';

class RegionOnboardingCard extends StatefulWidget {
  const RegionOnboardingCard({super.key});

  @override
  State<RegionOnboardingCard> createState() => _RegionOnboardingCardState();
}

class _RegionOnboardingCardState extends State<RegionOnboardingCard> {
  final _controller = TextEditingController();
  Set<String> _roles = {};

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final missing = _contracts.keys.toSet().difference(_roles);
    return Card(
      key: const Key('region-onboarding-card'),
      color: const Color(0xFFF2F6FA),
      child: ExpansionTile(
        leading: const Icon(Icons.upload_file_outlined),
        title: const Text('새 지역 자료 연결 준비'),
        subtitle: const Text('CSV 파일의 첫 번째 행을 붙여 넣어 활용 가능한 항목을 미리 확인합니다.'),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        children: [
          const Align(
            alignment: Alignment.centerLeft,
            child: Text(
              '원본 데이터는 전송하거나 저장하지 않습니다. 열 이름만 현재 화면에서 검사합니다.',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
            ),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _controller,
            minLines: 2,
            maxLines: 4,
            decoration: const InputDecoration(
              labelText: 'CSV 첫 행의 열 이름',
              hintText: '예: 관리번호, 위도, 경도, 정격용량, 접수일, 처리일',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 8),
          Align(
            alignment: Alignment.centerLeft,
            child: FilledButton.icon(
              onPressed: _inspect,
              icon: const Icon(Icons.fact_check_outlined),
              label: const Text('연결 가능 항목 확인'),
            ),
          ),
          if (_roles.isNotEmpty) ...[
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerLeft,
              child: Text('확인된 항목 ${_roles.length}종',
                  style: const TextStyle(fontWeight: FontWeight.w700)),
            ),
            const SizedBox(height: 6),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: [
                for (final role in _roles)
                  Chip(label: Text(_contracts[role]!.$1)),
              ],
            ),
            const SizedBox(height: 8),
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                missing.isEmpty
                    ? '다음 단계: 실제 파일의 값 형식, 연결번호 중복, 누락값을 검수합니다.'
                    : '추가로 필요한 항목: ${missing.map((role) => _contracts[role]!.$1).join(' · ')}',
              ),
            ),
          ],
          const Divider(height: 24),
          const _OnboardingStep(number: '1', text: '열 이름과 값 형식 확인'),
          const _OnboardingStep(number: '2', text: 'LightGuard 표준 항목과 연결'),
          const _OnboardingStep(number: '3', text: '누락·중복·좌표 오류 검사'),
          const _OnboardingStep(number: '4', text: '사용 가능한 화면과 제한사항 안내'),
        ],
      ),
    );
  }

  void _inspect() {
    final header = _controller.text.toLowerCase();
    setState(() {
      _roles = {
        for (final entry in _contracts.entries)
          if (entry.value.$2.hasMatch(header)) entry.key,
      };
    });
  }

  static final _contracts = <String, (String, RegExp)>{
    'SIGNAL': ('전력·점등 상태', RegExp(r'전력|전류|전압|점등|소등|누전')),
    'OPERATIONS': ('고장 접수·처리 이력', RegExp(r'접수|처리|고장|민원|보수|수리|조치')),
    'CABINET': ('분전함 정보', RegExp(r'분전함|제어함|배전함')),
    'LOAD': ('설비용량 정보', RegExp(r'정격|용량|와트|watt')),
    'SPATIAL': ('설치 위치', RegExp(r'위도|경도|좌표|주소|소재지|설치위치')),
    'ASSET': ('가로등 시설정보', RegExp(r'관리번호|가로등번호|보안등번호|등주|등기구|광원')),
  };
}

class _OnboardingStep extends StatelessWidget {
  const _OnboardingStep({required this.number, required this.text});

  final String number;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        children: [
          CircleAvatar(radius: 11, child: Text(number)),
          const SizedBox(width: 8),
          Expanded(child: Text(text)),
        ],
      ),
    );
  }
}
