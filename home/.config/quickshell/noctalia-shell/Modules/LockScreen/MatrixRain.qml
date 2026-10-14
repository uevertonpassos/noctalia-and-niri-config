import QtQuick

// Decorative only: the parent lock screen owns all input and authentication.
Canvas {
    id: rain
    property bool animate: true
    property color accent: "#39ff14"
    property string fontFamily: "MesloLGS Nerd Font"
    property real elapsed: 0
    readonly property int columnCount: Math.min(90, Math.max(1, Math.ceil(width / 30)))
    readonly property string glyphs: "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ<>[]{}:/=+"
    renderStrategy: Canvas.Threaded

    function paintFrame() {
        if (available)
            requestPaint();
    }

    onWidthChanged: paintFrame()
    onHeightChanged: paintFrame()
    onAccentChanged: paintFrame()
    onFontFamilyChanged: paintFrame()
    onAvailableChanged: paintFrame()

    Timer {
        interval: 100
        repeat: true
        running: rain.animate && rain.visible && rain.width > 0 && rain.height > 0
        onTriggered: {
            rain.elapsed += interval / 1000;
            rain.paintFrame();
        }
    }

    onPaint: {
        const ctx = getContext("2d");
        if (!ctx)
            return;
        ctx.clearRect(0, 0, width, height);
        ctx.font = '14px "' + fontFamily + '"';
        ctx.textAlign = "center";
        const step = 22;
        const cycle = height + 440;
        for (let column = 0; column < columnCount; column++) {
            const seed = (column * 137 + 53) % 997;
            const speed = 30 + seed % 45;
            const head = (elapsed * speed + seed * 7) % cycle;
            const x = (column + 0.5) * width / columnCount;
            const length = 9 + seed % 10;
            // Leave the login card and clock visually quiet.
            const centerFade = Math.abs(x - width / 2) < 240 ? 0.20 : 0.65;
            for (let tail = 0; tail < length; tail++) {
                const y = head - tail * step;
                if (y < 0 || y > height + step)
                    continue;
                ctx.globalAlpha = centerFade * (1 - tail / length);
                ctx.fillStyle = tail === 0 ? "#c7f7cf" : accent;
                const index = (seed + tail * 17 + Math.floor(elapsed * 2)) % glyphs.length;
                ctx.fillText(glyphs.charAt(index), x, y);
            }
        }
        ctx.globalAlpha = 1;
    }
}
