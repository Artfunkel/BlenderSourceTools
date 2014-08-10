$modelname "blest/Dice.mdl"

$cdmaterials "models"

$model "body_SMD" Dice.smd {
    vcafile Throw.vta
}

$model "body_DMX" Dice.dmx

$boneflexdriver "vcabone_Throw" tx "Throw" 0 1
$boneflexdriver "vcabone_Throw" ty "multi_Throw" 0 1
$upaxis Y // always needed!
$sequence "Fracture_SMD" "vcaanim_Throw.smd" fps 24.0
$sequence "Fracture_DMX" "vcaanim_Throw.dmx" fps 24.0
