import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../app/router/app_router.dart';

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
      const _NavItem(AppRoute.dashboard, '대시보드', Icons.dashboard),
      const _NavItem(AppRoute.map, '지도', Icons.map),
      const _NavItem(AppRoute.inspections, '점검 우선순위', Icons.warning_amber_rounded),
      const _NavItem(AppRoute.ami, '실제 AMI 사례', Icons.bug_report_outlined),
      const _NavItem(AppRoute.regions, '지역', Icons.location_city_outlined),
    ];

    final location = GoRouterState.of(context).matchedLocation;

    if (isWide) {
      return Scaffold(
        appBar: AppBar(title: Text(title), actions: actions),
        body: Row(
          children: [
            NavigationRail(
              selectedIndex: _selectedIndex(tabs, location),
              onDestinationSelected: (index) => _goto(context, tabs[index].path),
              labelType: NavigationRailLabelType.all,
              destinations: [
                for (final t in tabs)
                  NavigationRailDestination(
                    icon: Icon(t.icon),
                    label: Text(t.label),
                  ),
              ],
            ),
            const VerticalDivider(width: 1),
            Expanded(child: child),
          ],
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text(title), actions: actions),
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex(tabs, location),
        destinations: [
          for (final t in tabs)
            NavigationDestination(icon: Icon(t.icon), label: t.label),
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

class _NavItem {
  const _NavItem(this.path, this.label, this.icon);
  final String path;
  final String label;
  final IconData icon;
}
