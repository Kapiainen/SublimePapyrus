import sublime, sublime_plugin, sys, os
PYTHON_VERSION = sys.version_info
if PYTHON_VERSION[0] == 2:
    import imp
    root, module = os.path.split(os.getcwd())
    coreModule = "SublimePapyrus"
    # SublimePapyrus core module
    mainPackage = os.path.join(root, coreModule, "Plugin.py")
    imp.load_source("SublimePapyrus", mainPackage)
    del mainPackage
    import SublimePapyrus
    # Cleaning up
    del root
    del module
    del coreModule
elif PYTHON_VERSION[0] >= 3:
    from SublimePapyrus import Plugin as SublimePapyrus

class SublimePapyrusSkyrimIfpvBooleanConfigValueSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
    def get_items(self, **args):
        items = {
            "bActivated": "",
            "bAimBow": "",
            "bAimCrossbow": "",
            "bAimMagic": "",
            "bAimMagicLeft": "",
            "bAimMagicRight": "",
            "bAttackAnyHanded": "",
            "bAttackAnyHandedLeft": "",
            "bAttackAnyHandedRight": "",
            "bAttackOneHanded": "",
            "bAttackOneHandedLeft": "",
            "bAttackOneHandedRight": "",
            "bAttackTwoHanded": "",
            "bCrafting": "",
            "bDead": "",
            "bDialogue": "",
            "bDisableVATS": "",
            "bDismounting": "",
            "bEnabled": "",
            "bFocus": "",
            "bGrabbing": "",
            "bHeadtrack": "",
            "bHideHead": "",
            "bIndoors": "",
            "bIsActive": "",
            "bIsInIFPV": "",
            "bIsTargetOverwritten": "",
            "bJumping": "",
            "bKillMove": "",
            "bMounted": "",
            "bMounting": "",
            "bRunning": "",
            "bSendModEvents": "",
            "bSitting": "",
            "bSneaking": "",
            "bSprinting": "",
            "bSwimming": "",
            "bToggleIntoIFPV": "",
            "bVampireLord": "",
            "bWalking": "",
            "bWeaponOut": "",
            "bWereWolf": "",
            "bZoomIntoIFPV": ""
        }
        return items

class SublimePapyrusSkyrimIfpvFloatConfigValueSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
    def get_items(self, **args):
        items = {
            "fCameraViewOffsetHorizontal": "",
            "fCameraViewOffsetVertical": "",
            "fExtraRotationFromCamera": "",
            "fExtraRotationMouse": "",
            "fFocusMinAngle": "",
            "fFocusSpeed": "",
            "fFOV": "",
            "fNearClip": "",
            "fPositionOffsetDepth": "",
            "fPositionOffsetHorizontal": "",
            "fPositionOffsetVertical": "",
            "fRestrictAngleHorizontal": "",
            "fRestrictAngleVertical": "",
            "fRotationFromHead": "",
            "fTimeScale": "",
            "fTweenLength": "",
            "fUpdateProfileInterval": ""
        }
        return items

class SublimePapyrusSkyrimIfpvIntegerConfigValueSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
    def get_items(self, **args):
        items = {
            "iCameraState": "",
            "iDebug": "",
            "iDebug2": "",
            "iFaceCrosshair": "",
            "iFocusDelay": "",
            "iObjectBaseFormId": "",
            "iObjectRefFormId": ""
        }
        return items

class SublimePapyrusSkyrimIfpvStringConfigValueSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
    def get_items(self, **args):
        items = {
            "sCameraNode": "",
            "sFurniture": "",
            "sRace": ""
        }
        return items

class SublimePapyrusSkyrimIfpvModEventNameSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
    def get_items(self, **args):
        items = {
            "IFPV_EnteringProfile": "",
            "IFPV_EnteringView": "",
            "IFPV_LeavingProfile": "",
            "IFPV_LeavingView": ""
        }
        return items