import 'package:go_router/go_router.dart';
import '../../features/dashboard/dashboard_screen.dart';
import '../../features/map/map_screen.dart';
import '../../features/inspections/inspection_list_screen.dart';
import '../../features/cabinet_detail/cabinet_detail_screen.dart';
import '../../features/ami_validation/ami_validation_screen.dart';

class AppRoute {
  static const dashboard = '/';
  static const map = '/map';
  static const inspections = '/inspections';
  static const cabinet = '/cabinet/:id';
  static const ami = '/ami-events';
}

GoRouter createRouter() {
  return GoRouter(
    initialLocation: AppRoute.dashboard,
    routes: [
      GoRoute(path: AppRoute.dashboard, builder: (context, state) => const DashboardScreen()),
      GoRoute(
        path: AppRoute.map,
        builder: (context, state) => MapScreen(
          focusCabinetUid: state.uri.queryParameters['cabinet'],
        ),
      ),
      GoRoute(path: AppRoute.inspections, builder: (context, state) => const InspectionListScreen()),
      GoRoute(
        path: AppRoute.cabinet,
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return CabinetDetailScreen(cabinetUid: id);
        },
      ),
      GoRoute(path: AppRoute.ami, builder: (context, state) => const AmiValidationScreen()),
      GoRoute(path: '/regions', redirect: (context, state) => AppRoute.dashboard),
    ],
  );
}
