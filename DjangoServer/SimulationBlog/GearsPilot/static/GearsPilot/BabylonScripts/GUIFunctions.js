
var sliderHeight = "20px";
var sliderWidth = "200px";
var sliderHeaderHeight = sliderHeight;
var headerColor = "white"

function createSlider(panel, title, maxVal, minVal, initialVal, step, onChange)
{
  // variables for all sliders
  var sliderHeight = "20px";
  var sliderWidth = "200px";
  var sliderHeaderHeight = sliderHeight;
  var headerColor = "white";

  var header = new BABYLON.GUI.TextBlock();
  header.text = title + Math.round(initialVal*10)/10
  header.height = sliderHeaderHeight;
  header.width = sliderWidth;
  header.color = headerColor;
  panel.addControl(header);

  var slider = new BABYLON.GUI.Slider();
  let multiplier = maxVal - minVal;
  slider.minimum = minVal;
  slider.maximum = minVal + 1;
  slider.value = (initialVal - minVal) / multiplier;
  slider.height = sliderHeight;
  slider.width = sliderWidth;
  //slider.step = step  // Babylon.js slider steps only work with step values below 1.
  slider.onValueChangedObservable.add(function(value) {
    // round
    value = (value - minVal) * multiplier + minVal;
    value = Math.round(value / step) * step;
    onChange(value);
    header.text = title + Math.round(value*10)/10;
  }
  );
  panel.addControl(slider);

  return slider;
}

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


function createWeightingRadioButtons(group, panel, isChecked = false) {

  var button = new BABYLON.GUI.RadioButton(group.name);
  button.width = "20px";
  button.height = "20px";
  button.color = "white";
  button.background = "green";
  button.isChecked = isChecked;
  button.onIsCheckedChangedObservable.add(function(state)
  {
      if (state) {
          group.setWeightForAllAnimatables(1);
          group.play(true);
      }
      else {
        group.setWeightForAllAnimatables(0);
        group.pause();
      }
  });


  var header = BABYLON.GUI.Control.AddHeader(button, group.name, "100px", { isHorizontal: true, controlFirst: true });
  header.height = "30px";
  header.width = "120px";
  panel.addControl(header);
}

function createButton(panel, name, text, func) {
  var button = BABYLON.GUI.Button.CreateSimpleButton(name, text);
    button.width = "100px";
    button.height = "40px";
    button.color = "white";
    button.background = "black";
    button.onPointerClickObservable.add(function(){
      func();
    });

    panel.addControl(button);
    return button;
}

function createText(panel, text) {
  var textBlock = new BABYLON.GUI.TextBlock();
  textBlock.text = text;
  textBlock.color = "white";
  textBlock.fontsize = 24;
  textBlock.height = "30px";
  textBlock.width = "200px";
  panel.addControl(textBlock);
  return textBlock;
}
