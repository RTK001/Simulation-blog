function babylonVectorFromList(list) {
  return BABYLON.Vector3(list[0], list[1], list[2]);
}


function rotateAnimation(mesh, axis, JSON_File) {

  let gear = JSON_File["gears"][mesh.name]

  type_converter = {
    "BABYLON.Animation.ANIMATIONTYPE_FLOAT" : BABYLON.Animation.ANIMATIONTYPE_FLOAT,
    "BABYLON.Animation.ANIMATIONTYPE_VECTOR3" : BABYLON.Animation.ANIMATIONTYPE_VECTOR3
  }

  for (let ani of gear.animations)
  {
    var animationOne = new BABYLON.Animation("animationOne", ani.variable, 10, type_converter[ani.type], BABYLON.Animation.ANIMATIONLOOPMODE_RELATIVE);
    //var rotationAnimation = new BABYLON.Animation("animationOne", "rotation.y", 10, BABYLON.Animation.ANIMATIONTYPE_FLOAT, BABYLON.Animation.ANIMATIONLOOPMODE_RELATIVE);
    var translationAnimation = new BABYLON.Animation("animationOne", "position", 10, BABYLON.Animation.ANIMATIONTYPE_VECTOR3, BABYLON.Animation.ANIMATIONLOOPMODE_RELATIVE);

    var parentPoint = new BABYLON.TransformNode("root");
    if (ani.parent_point)
    {
      parentPoint.position = babylonVectorFromList(ani.parent_point);
      ParentPoints.push(parentPoint);
    }

    var animationKeys = [];

    if (ani.type == "BABYLON.Animation.ANIMATIONTYPE_FLOAT") {
      for (let kf of ani.keyframes)
      {animationKeys.push(kf);}
    }
    else if (ani.type == "BABYLON.Animation.ANIMATIONTYPE_VECTOR3") {
      for (let kf of ani.keyframes)
      {
        animationKeys.push(
          {
            "frame": kf.frame,
            "value": babylonVectorFromList(kf.value)
          });
      }
    }

    animationOne.setKeys(animationKeys);

    if (ani.parent_point)
      {
        parentPoint.animations.push(animationOne);
        mesh.parent = parentPoint;
        scene.beginWeightedAnimation(parentPoint, 0, 100, 1, true);
      }
    else
    {
      mesh.animations.push(animationOne);
      scene.beginWeightedAnimation(mesh, 0, 100, 1, true);
    }

    //scene.beginDirectAnimation(mesh, [rotationAnimation], 0, 100, true);

  }
}
