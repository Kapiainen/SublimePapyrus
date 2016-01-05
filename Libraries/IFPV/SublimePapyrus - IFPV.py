import sublime, sublime_plugin, sys, os
PYTHON_VERSION = sys.version_info
if PYTHON_VERSION[0] == 2:
    import imp
    mainPackage = os.path.join(os.path.split(os.getcwd())[0], "SublimePapyrus", "SublimePapyrus.py")
    imp.load_source("SublimePapyrus", mainPackage)
    del mainPackage
    import SublimePapyrus
if PYTHON_VERSION[0] == 3:
    from SublimePapyrus import SublimePapyrus

class PapyrusIfpvBooleanConfigValueSuggestionsCommand(SublimePapyrus.PapyrusShowSuggestionsCommand):
    def get_items(self, **args):
        items = {
            "bActivated": "bActivated",
            "bAimBow": "bAimBow",
            "bAimCrossbow": "bAimCrossbow",
            "bAimMagic": "bAimMagic",
            "bAimMagicLeft": "bAimMagicLeft",
            "bAimMagicRight": "bAimMagicRight",
            "bAttackAnyHanded": "bAttackAnyHanded",
            "bAttackAnyHandedLeft": "bAttackAnyHandedLeft",
            "bAttackAnyHandedRight": "bAttackAnyHandedRight",
            "bAttackOneHanded": "bAttackOneHanded",
            "bAttackOneHandedLeft": "bAttackOneHandedLeft",
            "bAttackOneHandedRight": "bAttackOneHandedRight",
            "bAttackTwoHanded": "bAttackTwoHanded",
            "bCrafting": "bCrafting",
            "bDead": "bDead",
            "bDialogue": "bDialogue",
            "bDisableVATS": "bDisableVATS",
            "bDismounting": "bDismounting",
            "bEnabled": "bEnabled",
            "bFocus": "bFocus",
            "bGrabbing": "bGrabbing",
            "bHeadtrack": "bHeadtrack",
            "bHideHead": "bHideHead",
            "bIndoors": "bIndoors",
            "bIsActive": "bIsActive",
            "bIsInIFPV": "bIsInIFPV",
            "bIsTargetOverwritten": "bIsTargetOverwritten",
            "bJumping": "bJumping",
            "bKillMove": "bKillMove",
            "bMounted": "bMounted",
            "bMounting": "bMounting",
            "bRunning": "bRunning",
            "bSendModEvents": "bSendModEvents",
            "bSitting": "bSitting",
            "bSneaking": "bSneaking",
            "bSprinting": "bSprinting",
            "bSwimming": "bSwimming",
            "bToggleIntoIFPV": "bToggleIntoIFPV",
            "bVampireLord": "bVampireLord",
            "bWalking": "bWalking",
            "bWeaponOut": "bWeaponOut",
            "bWereWolf": "bWereWolf",
            "bZoomIntoIFPV": "bZoomIntoIFPV"
        }
        return items

class PapyrusIfpvFloatConfigValueSuggestionsCommand(SublimePapyrus.PapyrusShowSuggestionsCommand):
    def get_items(self, **args):
        items = {
            "fCameraViewOffsetHorizontal": "fCameraViewOffsetHorizontal",
            "fCameraViewOffsetVertical": "fCameraViewOffsetVertical",
            "fExtraRotationFromCamera": "fExtraRotationFromCamera",
            "fExtraRotationMouse": "fExtraRotationMouse",
            "fFocusMinAngle": "fFocusMinAngle",
            "fFocusSpeed": "fFocusSpeed",
            "fFOV": "fFOV",
            "fNearClip": "fNearClip",
            "fPositionOffsetDepth": "fPositionOffsetDepth",
            "fPositionOffsetHorizontal": "fPositionOffsetHorizontal",
            "fPositionOffsetVertical": "fPositionOffsetVertical",
            "fRestrictAngleHorizontal": "fRestrictAngleHorizontal",
            "fRestrictAngleVertical": "fRestrictAngleVertical",
            "fRotationFromHead": "fRotationFromHead",
            "fTimeScale": "fTimeScale",
            "fTweenLength": "fTweenLength",
            "fUpdateProfileInterval": "fUpdateProfileInterval"
        }
        return items

class PapyrusIfpvIntegerConfigValueSuggestionsCommand(SublimePapyrus.PapyrusShowSuggestionsCommand):
    def get_items(self, **args):
        items = {
            "iCameraState": "iCameraState",
            "iDebug": "iDebug",
            "iDebug2": "iDebug2",
            "iFaceCrosshair": "iFaceCrosshair",
            "iFocusDelay": "iFocusDelay",
            "iObjectBaseFormId": "iObjectBaseFormId",
            "iObjectRefFormId": "iObjectRefFormId"
        }
        return items

class PapyrusIfpvStringConfigValueSuggestionsCommand(SublimePapyrus.PapyrusShowSuggestionsCommand):
    def get_items(self, **args):
        items = {
            "sCameraNode": "sCameraNode",
            "sFurniture": "sFurniture",
            "sRace": "sRace"
        }
        return items

class PapyrusIfpvModEventNameSuggestionsCommand(SublimePapyrus.PapyrusShowSuggestionsCommand):
    def get_items(self, **args):
        items = {
            "IFPV_EnteringProfile": "IFPV_EnteringProfile",
            "IFPV_EnteringView": "IFPV_EnteringView",
            "IFPV_LeavingProfile": "IFPV_LeavingProfile",
            "IFPV_LeavingView": "IFPV_LeavingView"
        }
        return items