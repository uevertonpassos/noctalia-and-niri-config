.pragma library

// Focus and title changes are handled by the existing delegates' bindings.
// Only change the repeater model when its applications or windows change.
function sameEntries(previous, next) {
    if (previous.length !== next.length)
        return false;
    for (var i = 0; i < previous.length; ++i) {
        var a = previous[i];
        var b = next[i];
        if (a.appId !== b.appId || a.type !== b.type || a.isPinned !== b.isPinned)
            return false;
        var aw = a.toplevels || [];
        var bw = b.toplevels || [];
        if (aw.length !== bw.length)
            return false;
        for (var j = 0; j < aw.length; ++j) {
            if (aw[j] !== bw[j])
                return false;
        }
        if (aw.length === 0 && a.title !== b.title)
            return false;
    }
    return true;
}
