from QtModularUiPack.ModularApplications import *
from QtModularUiPack.Framework import is_non_strict_subclass
from QtModularUiPack.Widgets import EmptyFrame


def get_builtin_frames():
    glob = globals()
    builtin_frames = [EmptyFrame]
    for member in glob:
        if glob[member] not in builtin_frames and is_non_strict_subclass(glob[member], EmptyFrame):
            builtin_frames.append(glob[member])
    return builtin_frames

