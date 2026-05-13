import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

enum DisclaimerPillar { health, mind }

/// Disclaimer banner rendered above any AI response.
/// - Health: red border, "Educational only - not medical advice."
/// - Mind: blue border, "Reflective coaching, not therapy."
class DisclaimerBanner extends StatelessWidget {
  const DisclaimerBanner({
    super.key,
    required this.pillar,
  });

  final DisclaimerPillar pillar;

  @override
  Widget build(BuildContext context) {
    final semantic = Theme.of(context).extension<AppSemanticColors>();
    final color = pillar == DisclaimerPillar.health
        ? (semantic?.crisis ?? AppColors.crisisRed)
        : (semantic?.calm ?? AppColors.calmBlue);
    final copy = pillar == DisclaimerPillar.health
        ? 'Educational only - not medical advice. Always consult a licensed physician.'
        : 'Reflective coaching, not therapy. If you need professional support, find a therapist.';
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: color, width: 1),
        borderRadius: BorderRadius.circular(8),
        color: color.withOpacity(0.05),
      ),
      child: Text(
        copy,
        style: TextStyle(color: color, fontSize: 12),
      ),
    );
  }
}
