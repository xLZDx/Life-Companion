import 'package:flutter/material.dart';

/// Semantic colors. Phase 7 may rebrand the palette; widget code uses these
/// names (`crisisRed`, `calmBlue`, etc.) rather than hex literals.
class AppColors {
  // Brand seeds
  static const Color seedLight = Color(0xFF4A6FA5);
  static const Color seedDark = Color(0xFF6B8FC9);

  // Semantic
  static const Color crisisRed = Color(0xFFC62828);
  static const Color calmBlue = Color(0xFF5C8BB0);
  static const Color reflectionGreen = Color(0xFF558B6E);
  static const Color warningAmber = Color(0xFFE69E2A);
}

/// ThemeExtension for semantic colors. Read in widgets via
///   Theme.of(context).extension<AppSemanticColors>()
@immutable
class AppSemanticColors extends ThemeExtension<AppSemanticColors> {
  const AppSemanticColors({
    required this.crisis,
    required this.calm,
    required this.reflection,
    required this.warning,
  });

  final Color crisis;
  final Color calm;
  final Color reflection;
  final Color warning;

  static const light = AppSemanticColors(
    crisis: AppColors.crisisRed,
    calm: AppColors.calmBlue,
    reflection: AppColors.reflectionGreen,
    warning: AppColors.warningAmber,
  );

  static const dark = AppSemanticColors(
    crisis: Color(0xFFEF5350),
    calm: Color(0xFF7BA7CC),
    reflection: Color(0xFF6FA585),
    warning: Color(0xFFFFB74D),
  );

  @override
  ThemeExtension<AppSemanticColors> copyWith({
    Color? crisis,
    Color? calm,
    Color? reflection,
    Color? warning,
  }) {
    return AppSemanticColors(
      crisis: crisis ?? this.crisis,
      calm: calm ?? this.calm,
      reflection: reflection ?? this.reflection,
      warning: warning ?? this.warning,
    );
  }

  @override
  ThemeExtension<AppSemanticColors> lerp(
    covariant ThemeExtension<AppSemanticColors>? other,
    double t,
  ) {
    if (other is! AppSemanticColors) return this;
    return AppSemanticColors(
      crisis: Color.lerp(crisis, other.crisis, t)!,
      calm: Color.lerp(calm, other.calm, t)!,
      reflection: Color.lerp(reflection, other.reflection, t)!,
      warning: Color.lerp(warning, other.warning, t)!,
    );
  }
}
