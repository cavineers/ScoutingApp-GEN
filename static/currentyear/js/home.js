let teamLayout = ["red", "red", "red", "blu", "blu", "blu"];
const teamOrder = ["red1", "red2", "red3", "blu1", "blu2", "blu3"];

const RED_COLOR = "#aa0000";
const RED_BORDER_COLOR = "#aa0000";
const BLUE_COLOR = "#476291";
const BLUE_BORDER_COLOR = "#476291";

window.addEventListener("load", () => {
    let teams = document.querySelectorAll(".red, .blu");
    for (let i = 0; i<teams.length; i++) {
        teams[i].addEventListener("click", (ev) => {
            if (ev.button!=0) return;
            teamLayout[i] = teamOrder[(teamOrder.indexOf(teamLayout[i])+1)%teamOrder.length];
            switch(teamLayout[i]) {
                case "red":
                    teams[i].style.background = RED_COLOR;
                    teams[i].style.borderColor = RED_BORDER_COLOR;
                    break;
                case "blu":
                    teams[i].style.background = BLUE_COLOR;
                    teams[i].style.borderColor = BLUE_BORDER_COLOR;
                    break;
                default:
                    teams[i].style.background = UNSELECTED_COLOR;
                    teams[i].style.borderColor = UNSELECTED_COLOR;
                    break;
            }
        });
    }
});

function verifyInfo(inputs) {
    console.log(inputs.matchNumber)
    if (inputs.matchNumber < 1) {
        outputError("Invalid match number.");
        return false;
    }
    else if (inputs.teamNumber < 1) {
        outputError("Invalid team number.")
        return false;
    }
    else if (inputs.scouterName=="placeholder") {
        outputError("Enter your name (The name of the person scouting).");
        return false;
    }
    return true;
}

function outputError(message) {
  console.error(message);
  let errorOutput = document.getElementById("errorOutput");
  if (errorOutput==null) {
    const submitForm = document.getElementById("submitForm");
    if (submitForm==null) return; //nowhere to visibly output error to
    errorOutput = document.createElement("p");
    errorOutput.style.color = "#be0000";
    errorOutput.id = "errorOutput";
    submitForm.prepend(errorOutput);
  }
  errorOutput.innerHTML = message;
}
