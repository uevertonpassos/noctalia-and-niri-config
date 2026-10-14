import QtQuick
import qs.Commons
import qs.Commons as NoctaliaTheme

// Rounded group container using the variant surface color.
// To be used in side panels and settings panes to group fields or buttons.
// Opacity is based on panelBackgroundOpacity but clamped to a minimum to avoid full transparency.

Item {
  id: root

  property color color: NoctaliaTheme.Color.mSurfaceVariant
  property bool forceOpaque: false
  property alias radius: bg.radius
  property alias border: bg.border

  Rectangle {
    id: bg
    anchors.fill: parent
    radius: Style.radiusM
    border.color: Style.boxBorderColor
    border.width: Style.borderS
    color: {
      if (forceOpaque) {
        return root.color;
      }

      return NoctaliaTheme.Color.smartAlpha(root.color);
    }
  }
}
