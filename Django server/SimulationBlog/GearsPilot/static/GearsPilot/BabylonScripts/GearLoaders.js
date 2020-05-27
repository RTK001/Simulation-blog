

 function AddGearRotations(Gears) {
   const v = new BABYLON.Vector3(0,0,0);
   const angle = Math.PI/32;

   scene.registerBeforeRender(function () {
     //Gears[0].rotate(v, angle, BABYLON.Space.WORLD);
     Gears[0].rotation.y += angle;
   });
};



async function LoadGearMeshesFromFiles_ImportMesh(scene, Files, Gears) {
  for (let g in Files.gears) {
    let f = Files.gears[g].filename;
    await BABYLON.SceneLoader.ImportMeshAsync(g, "./static/GearsPilot/" + Files.name + "/", f, scene, function (meshes, particleSystems, skeletons) {
      //meshes[0].name = f;
      //Gears.push(meshes[0]);
    });
    let gear = scene.meshes[scene.meshes.length -1];
    gear.name = g
    let loc = Files.gears[g]["location"];
    console.log(Files["x_offset"])
    let x = (loc[0] - Files["x_offset"]) * 10
    let y = (loc[2]) * 10
    let z = (loc[1] - Files["y_offset"]) * 10
    gear.position = new BABYLON.Vector3(x, y, z);
    //gear.setPivotPoint(new BABYLON.Vector3(26.661191,0,21.86734974), BABYLON.Space.WORLD);

    Gears.push(gear);
    }
  //AddGearRotations(Gears);
  for (let i = 0; i < Gears.length; i++) {
    rotateAnimation(Gears[i], new BABYLON.Vector3(0,0,0), Files);
}
}


async function awaitLoadJSON(scene, fileListURL, Gears) {
  // Loads the .stl filenames from the JSON
  var Files = [];
  // URL for JSON file. Should abstract this.

  let prom = await fetch(fileListURL);
  Files = await prom.json();
  LoadGearMeshesFromFiles_ImportMesh(scene, Files, Gears);
  }



function LoadJSON(scene, Gears) {
    // Loads the .stl filenames from the JSON
    var Files = [];
    // URL for JSON file. Should abstract this.
    let fileListURL = "./static/GearsPilot/Gear2-files.json";
    let request = new XMLHttpRequest();
    request.open("GET", fileListURL);
    request.responseType = "json";
    request.send();
    request.onload = function(Files) {
      Files = request.response;
      LoadGearMeshesFromFiles_ImportMesh(scene, Files, Gears);
      }
    }










// Old

    function LoadGearMeshesFromFiles(assetsManager, Files, Gears) {
    var fileCounter = 0;

    for (let f of Files) {
      let gearTask = assetsManager.addMeshTask(f + " task", "", "./static/GearsPilot/Gear2/", f + ".stl");
      gearTask.onSuccess = function (task) {
        task.loadedMeshes.name = Files[fileCounter];
        Gears.push(task.loadedMeshes);
      };

      // gearTask.onSuccess = function (task) { GEars.append(task.loadedMeshes); task.loadedMeshes[0].name = f;} // Gear naming did not work as planned
      }
      assetsManager.load();

      return assetsManager;
    }
