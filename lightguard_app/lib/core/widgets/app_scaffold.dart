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
          actions: actions,
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
        actions: actions,
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
      label: 'LightGuard AMI 신호',
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

class _NavItem {
  const _NavItem(this.path, this.label, this.mobileLabel, this.icon);
  final String path;
  final String label;
  final String mobileLabel;
  final IconData icon;
}
