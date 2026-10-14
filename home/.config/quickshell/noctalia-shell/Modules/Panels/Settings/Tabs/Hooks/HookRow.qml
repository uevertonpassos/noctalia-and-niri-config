import QtQuick
import QtQuick.Layouts
import qs.Commons
import qs.Commons as NoctaliaTheme
import qs.Widgets

RowLayout {
  id: root

  property string label: ""
  property string description: ""
  property string value: ""

  signal editClicked

  spacing: Style.marginM

  NLabel {
    label: root.label
    description: root.description
    labelColor: root.value ? NoctaliaTheme.Color.mPrimary : NoctaliaTheme.Color.mOnSurface
  }

  NIconButton {
    icon: "settings"
    onClicked: root.editClicked()
    tooltipText: I18n.tr("common.edit")
  }
}
