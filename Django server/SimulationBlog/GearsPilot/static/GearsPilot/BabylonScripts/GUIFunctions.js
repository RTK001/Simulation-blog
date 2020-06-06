

function createWeightingControl(group, panel) {
  var header = new BABYLON.GUI.TextBlock();
  header.text = group.name;
  header.height = "20px";
  panel.addControl(header);

  var slider = new BABYLON.GUI.Slider();
  slider.width = "200px";
  slider.height = "20px";
  slider.minimum = 0;
  slider.maximum = 1;
  slider.value = 0;
  slider.onValueChangedObservable.add(function(value) {
    console.log(value);
    if (value == 0) {
        group.stop();
    }
    else {
        group.setWeightForAllAnimatables(value);
        group.play(true);
    }
	});
	panel.addControl(slider);
}

function createWeightingRadioButtons(group, panel) {

  var button = new BABYLON.GUI.RadioButton();
  button.width = "20px";
  button.height = "20px";
  button.color = "white";
  button.background = "green";

  button.onIsCheckedChangedObservable.add(function(state) {
      if (state) {
          group.setWeightForAllAnimatables(1);
          group.play(true);
      }
      else {
        group.setWeightForAllAnimatables(0);
        group.reset();
      }
  });

  var header = BABYLON.GUI.Control.AddHeader(button, group.name, "100px", { isHorizontal: true, controlFirst: true });
  header.height = "30px";

  panel.addControl(header);

}
