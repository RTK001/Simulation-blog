function rotateAnimation(mesh, axis, JSON_File) {

  let gear = JSON_File["gears"][mesh.name]
  console.log(mesh.name);
  console.log(gear);
  var rotationAnimation = new BABYLON.Animation("animationOne", "rotation.y", 10, BABYLON.Animation.ANIMATIONTYPE_FLOAT, BABYLON.Animation.ANIMATIONLOOPMODE_RELATIVE);
  var translationAnimation = new BABYLON.Animation("animationOne", "position", 10, BABYLON.Animation.ANIMATIONTYPE_VECTOR3, BABYLON.Animation.ANIMATIONLOOPMODE_RELATIVE);

  var rotationKeys = [];
  var translationKeys = [];

  rotationKeys.push({
    frame : 0,
    value : 0
  });

  rotationKeys.push({
    frame : 50,
    value : Math.PI
  });


  rotationKeys.push({
    frame : 100,
    value : 2 * Math.PI
  });

  translationKeys.push({
    frame:0,
    value:new BABYLON.Vector3(4, 0, 1),
  });

  translationKeys.push({
    frame:50,
    value:new BABYLON.Vector3(-4, 0, 1),
  });

  translationKeys.push({
    frame:100,
    value:new BABYLON.Vector3(4, 0, 1),
  });

  rotationAnimation.setKeys(rotationKeys);
  mesh.animations.push(rotationAnimation);

  //translationAnimation.setKeys(translationKeys);
  //mesh.animations.push(translationAnimation);

  //scene.beginDirectAnimation(mesh, [rotationAnimation, translationAnimation], 0, 100, true);
  scene.beginDirectAnimation(mesh, [rotationAnimation], 0, 100, true);

}



function addAnimations(scene) {
  for (let i = 0; i < scene.meshes.length; i++) {
    rotateAnimation(scene, scene.meshes[i], new BABYLON.Vector3(0,1,0));
  }
}
