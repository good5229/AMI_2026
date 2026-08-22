import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../app/router/app_router.dart';
import '../../app/theme/app_theme.dart';

class LightguardShell extends StatelessWidget {
  const LightguardShell({
    super.key,
    required this.title,
    required this.child,
    this.actions,
  });

  final String title;
  final Widget child;
  final List<Widget>? actions;

  @override
  Widget build(BuildContext context) {
    final isWide = MediaQuery.of(context).size.width >= 900;
    final tabs = <_NavItem>[
      const _NavItem(AppRoute.dashboard, '오늘의 현황', '현황', Icons.home_outlined),
      const _NavItem(AppRoute.map, '현장 지도', '지도', Icons.map_outlined),
      const _NavItem(
          AppRoute.inspections, '점검 대상', '점검', Icons.fact_check_outlined),
      const _NavItem(
          AppRoute.ami, '판정 근거', '근거', Icons.insights_outlined),
      const _NavItem(
          AppRoute.regions, '지역 설정', '지역', Icons.location_city_outlined),
    ];

    final location = GoRouterState.of(context).matchedLocation;

    if (isWide) {
      return Scaffold(
        appBar: AppBar(
          title: Text(title, maxLines: 1, overflow: TextOverflow.ellipsis),
          actions: [...?actions, const _GlossaryButton()],
          bottom: const PreferredSize(
            preferredSize: Size.fromHeight(1),
            child: Divider(height: 1),
          ),
        ),
        body: Row(
          children: [
            DecoratedBox(
              decoration: const BoxDecoration(
                border: Border(right: BorderSide(color: AppTheme.line)),
              ),
              child: NavigationRail(
                minWidth: 92,
                groupAlignment: -0.78,
                selectedIndex: _selectedIndex(tabs, location),
                onDestinationSelected: (index) =>
                    _goto(context, tabs[index].path),
                labelType: NavigationRailLabelType.all,
                leading: const Padding(
                  padding: EdgeInsets.only(top: 12, bottom: 20),
                  child: _SignalMark(),
                ),
                destinations: [
                  for (final t in tabs)
                    NavigationRailDestination(
                      icon: Icon(t.icon),
                      selectedIcon: Icon(t.icon, fill: 1),
                      label: Text(t.label),
                    ),
                ],
              ),
            ),
            const VerticalDivider(width: 1),
            Expanded(
              child: Align(
                alignment: Alignment.topCenter,
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 1440),
                  child: SizedBox.expand(child: child),
                ),
              ),
            ),
          ],
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(title, maxLines: 1, overflow: TextOverflow.ellipsis),
        actions: [...?actions, const _GlossaryButton()],
        bottom: const PreferredSize(
          preferredSize: Size.fromHeight(1),
          child: Divider(height: 1),
        ),
      ),
      body: Align(
        alignment: Alignment.topCenter,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 960),
          child: SizedBox.expand(child: child),
        ),
      ),
      bottomNavigationBar: NavigationBar(
        height: 72,
        selectedIndex: _selectedIndex(tabs, location),
        destinations: [
          for (final t in tabs)
            NavigationDestination(icon: Icon(t.icon), label: t.mobileLabel),
        ],
        onDestinationSelected: (index) => _goto(context, tabs[index].path),
      ),
    );
  }

  static int _selectedIndex(List<_NavItem> tabs, String location) {
    for (var i = 0; i < tabs.length; i++) {
      if (tabs[i].path == location) return i;
      if (tabs[i].path != '/' && location.startsWith(tabs[i].path)) return i;
    }
    return 0;
  }

  static void _goto(BuildContext context, String path) {
    context.go(path);
  }
}

class _SignalMark extends StatelessWidget {
  const _SignalMark();

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'LightGuard 전력 사용 신호',
      child: Container(
        width: 42,
        height: 42,
        decoration: const BoxDecoration(
          color: AppTheme.ink,
          shape: BoxShape.circle,
        ),
        child: const Icon(Icons.bolt_rounded, color: Color(0xFFF7C948)),
      ),
    );
  }
}

class _GlossaryButton extends StatelessWidget {
  const _GlossaryButton();

  @override
  Widget build(BuildContext context) {
    return IconButton(
      tooltip: '용어 도움말',
      style: IconButton.styleFrom(
        backgroundColor: AppTheme.surfaceMuted,
        minimumSize: const Size(44, 44),
      ),
      icon: const Icon(Icons.help_outline),
      onPressed: () => showModalBottomSheet<void>(
        context: context,
        isScrollControlled: true,
        builder: (context) => const _GlossarySheet(),
      ),
    );
  }
}

class _GlossarySheet extends StatelessWidget {
  const _GlossarySheet();

  static const terms = <(String, String)>[
    ('전력계량 자료(AMI)', '분전함이 언제 얼마나 전기를 사용했는지 시간대별로 기록한 자료'),
    ('분전함', '여러 가로등에 전기를 나누어 공급하고 제어하는 시설'),
    ('설비용량', '가로등이 정상적으로 켜졌을 때 사용할 것으로 예상되는 전력의 크기'),
    ('기준 전력', '평소 정상 운전 시간대에 측정된 전력의 비교 기준'),
    ('이상 신호', '예상 점등시간이나 평소 전력 사용과 다른 움직임'),
    ('정상 오분류율', '정상 상태를 이상으로 잘못 표시한 비율. 낮을수록 불필요한 확인이 적음'),
    ('탐지율', '검증용 이상 사례 중 시스템이 찾아낸 비율'),
    ('정밀도', '우선 확인 대상으로 제시한 것 중 검증 기준과 일치한 비율'),
    ('검증용 모의 신호', '실제 고장자료가 없을 때 판정 동작을 시험하려고 의도적으로 만든 전력 변화'),
    ('현장 확인 필요', '고장 확정이 아니라 담당자가 원격 또는 현장에서 확인해야 하는 후보'),
  ];

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 18, 20, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('용어 도움말', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 4),
            const Text('화면에서 사용하는 주요 용어를 일상적인 표현으로 설명합니다.'),
            const SizedBox(height: 12),
            Flexible(
              child: ListView.separated(
                shrinkWrap: true,
                itemCount: terms.length,
                separatorBuilder: (_, __) => const Divider(),
                itemBuilder: (context, index) => ListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text(terms[index].$1,
                      style: const TextStyle(fontWeight: FontWeight.w700)),
                  subtitle: Text(terms[index].$2),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _NavItem {
  const _NavItem(this.path, this.label, this.mobileLabel, this.icon);
  final String path;
  final String label;
  final String mobileLabel;
  final IconData icon;
}
