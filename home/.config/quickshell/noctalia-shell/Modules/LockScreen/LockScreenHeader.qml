import QtQuick
import qs.Commons
import qs.Commons as NoctaliaTheme

MatrixHeader {
  anchors.fill: parent
  accent: NoctaliaTheme.Color.mPrimary
  muted: NoctaliaTheme.Color.mOnSurfaceVariant
  fontFamily: Settings.data.ui.fontFixed
  localeName: Settings.data.general.language || "pt"
}
